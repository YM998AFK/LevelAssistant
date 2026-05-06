"""Claude agent 循环，支持流式输出和工具调用。"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, List
import traceback

from PySide6.QtCore import QThread, Signal
import anthropic

from .config import (
    ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, CLAUDE_USER_AGENT,
    DEFAULT_MODEL, MAX_TOOL_ITERATIONS, MAX_TOKENS_PER_TURN,
    skills_dir, cursor_skills_dir, mcp_dir, output_dir,
)
from .tools import ToolBox, tool_definitions

_app_log = logging.getLogger("levelassistant")


def build_system_prompt(
    skill_content: str,
    skill_path: Path | None,
    mode_label: str,
    workspace: Path,
    uploaded_files: List[str] | None = None,
) -> str:
    from datetime import datetime
    uploaded_files = uploaded_files or []
    out_dir = output_dir()
    skills_root = skills_dir()
    cursor_skills = cursor_skills_dir()
    mcp_root = mcp_dir()
    session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # SKILL.md 内容优先——程序只追加运行时路径信息
    parts = [
        skill_content or f"你是「{mode_label}」模式的专业助手，自由发挥。",
        "",
        "---",
        "## 运行时路径（程序自动注入，不可修改）",
        f"- 工作目录：`{workspace}`",
        f"- 产出目录：`{out_dir}`",
        f"- Skill 目录：`{cursor_skills}`",
        f"- MCP 目录：`{mcp_root}`",
        f"- 公共资源目录：`{skills_root}`",
        f"- ⏱️ 当前会话开始时间：`{session_start}`（程序启动时注入，每次重启刷新）",
        "  - 判断「同 session 轻量修复路径」时，**只有在 task.log 中最新扫描记录的时间戳晚于此时间**，才允许视为同 session",
        "  - 否则一律走完整 4 步标准路径，不得跳过 S1/S2/S3 扫包",
    ]
    if skill_path:
        parts.append(f"- 本次技能包：`{skill_path}`")
    if uploaded_files:
        parts.append("- 用户上传文件（可读）：")
        for f in uploaded_files:
            parts.append(f"  - `{f}`")
    parts.extend([
        "",
        f"产出包用 create_archive 保存到产出目录：`{out_dir}/<文件名>.zip`",
        "",
        "## 执行规则（优先级低于技能规范）",
        "- 技能规范中要求「等用户确认」的步骤：必须输出确认单后**立即停止，不得再调用任何工具**，等收到用户明确回复后再继续",
        "  - ⚠️ 每次新会话开始时，无论历史日志中是否有确认记录，都必须重新输出确认单并等待用户当前会话的明确回复",
        "  - ⚠️ 「上次确认过」不等于「本次确认」，跨会话必须重新走 M7 卡点",
        "- 技能规范要求「dispatch 子 agent」时：使用 run_subagent 工具，按规范填写 prompt 模板再调用",
        "- 技能规范要求「先读某文件」时：必须先完整读取该文件再继续后续步骤",
        "- 审查员子 agent 返回后，若输出中含有「总体：FAIL」字样，**必须走重做流程**（新开改造员 → 新开审查员），严禁自行宣判「可豁免」或「建议通过」",
        "  - 唯一例外：若 FAIL 项目在主 agent 判断后属于纯描述笔误（改动内容本身已经正确），可在向用户明确说明后跳过，但必须得到用户明确 OK",
        "- 扫描员子 agent 返回后，若输出不含「§1」「§8」「表 A」「表 B」等完整区段标记，**必须打回重做（新开 Task）**，不得自行代为分析 WS 文件",
        "- 遇到不确定的地方直接向用户提问，不要硬猜",
    ])
    return "\n".join(parts)



def build_review_prompt(
    task_description: str,
    workspace: Path,
    output_files: List[str],
    skill_content: str,
) -> str:
    """独立审查官的系统提示——与执行 Agent 上下文完全隔离。"""
    from datetime import datetime
    out_dir = output_dir()
    skills_root = skills_dir()
    session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_list = "\n".join(f"  - {f}" for f in output_files) if output_files else "  （暂无）"
    return "\n".join([
        "你是「独立审查官」，与执行任务的 AI 相互独立、上下文隔离。",
        "你的唯一职责：对改关卡任务的产出进行严格审查，找出问题，不执行修改。",
        "",
        "## 任务原始要求",
        task_description,
        "",
        "## 路径信息",
        f"- 工作目录：`{workspace}`",
        f"- 产出目录：`{out_dir}`",
        f"- 技能/规范目录：`{skills_root}`",
        "- 本次产出文件：",
        file_list,
        "",
        "## 审查步骤（严格按顺序，每步必须执行）",
        "1. **解压产出包**：extract_archive 解压上方产出 zip 到 `review_unpack/`",
        "2. **结构校验**：ws_validate 校验所有 .ws 文件，记录 error/warning 数量",
        "3. **变量追踪审查**：",
        "   - 用 ws_find_value 搜索任务要求中提到的每个关键变量/值",
        "   - 用 ws_get_value 读取实际路径上的值，与预期对比",
        "   - 重点检查 ListReplaceItemAt / SetVar 的赋值是否被下游分支正确使用",
        "4. **误改检查**：搜索「不该变」的关键词，确认没有误改",
        "5. **SKILL 校验清单**：读取相关 SKILL.md，对照校验清单逐项勾选",
        "",
        "## 输出格式（严格遵守，不超过 40 行）",
        "```",
        "### 🔍 审查报告",
        "",
        "**ws 结构**：✅ PASS（error=0, warning=N）/ ❌ FAIL",
        "",
        "**修改项核查**",
        "- ✅/❌ [修改项名称]：期望=X，实际=Y（路径: a.b.c）",
        "（每项一行，必须写路径和实际读取到的值）",
        "",
        "**误改检查**",
        "- ✅/❌ [检查项]：...",
        "",
        "**总结**：✅ 全部通过 / ❌ 发现 N 个问题",
        "**建议**（如有问题）：...",
        "```",
        "",
        "不要输出超过格式要求的内容，不要展示 JSON 原文，只写结论和路径。",
        "",
        f"## 可参考的技能规范",
        skill_content or "（无技能文件）",
    ])


class ReviewWorker(QThread):
    """独立审查 Agent，与主 AgentWorker 上下文隔离，仅用于验证产出。"""
    text_chunk = Signal(str)
    tool_call_start = Signal(str, dict)
    tool_call_end = Signal(str, dict)
    iteration_update = Signal(int)
    error = Signal(str)
    finished_turn = Signal()

    MAX_ITERATIONS = 20

    def __init__(
        self,
        task_description: str,
        workspace: Path,
        output_files: List[str],
        skill_content: str,
        skill_dir: Path | None = None,
        task_logger: logging.Logger | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.task_description = task_description
        self.workspace = Path(workspace)
        self.output_files = list(output_files)
        self.skill_content = skill_content
        self.skill_dir = Path(skill_dir) if skill_dir else None
        self.log = task_logger or _app_log
        self._stop = False

    def request_stop(self):
        self._stop = True

    def run(self):
        self.log.info("审查 Agent 启动 workspace=%s", self.workspace)
        system_prompt = build_review_prompt(
            self.task_description, self.workspace,
            self.output_files, self.skill_content,
        )
        messages = [{"role": "user", "content":
                     "请开始审查，严格按照审查步骤逐项执行，最后输出规定格式的审查报告。"}]

        readable_roots = [skills_dir()]
        if self.skill_dir:
            readable_roots.append(self.skill_dir)
        toolbox = ToolBox(
            workspace=self.workspace,
            readable_roots=readable_roots,
            readable_files=self.output_files,
            extra_writable_roots=[output_dir(), output_dir().parent],
        )
        try:
            client = anthropic.Anthropic(
                api_key=ANTHROPIC_API_KEY,
                base_url=ANTHROPIC_BASE_URL,
                default_headers={"User-Agent": CLAUDE_USER_AGENT},
            )
            tools = tool_definitions()
            full_ai_text: list[str] = []

            for iteration in range(self.MAX_ITERATIONS):
                if self._stop:
                    break
                self.log.info("[审查] 轮次 %d", iteration + 1)
                self.iteration_update.emit(iteration + 1)
                try:
                    with client.messages.stream(
                        model=DEFAULT_MODEL,
                        max_tokens=8000,
                        system=system_prompt,
                        tools=tools,
                        messages=messages,
                    ) as stream:
                        for event in stream:
                            if self._stop:
                                break
                            etype = getattr(event, "type", "")
                            if etype == "content_block_delta":
                                delta = getattr(event, "delta", None)
                                if delta and delta.type == "text_delta":
                                    self.text_chunk.emit(delta.text)
                                    full_ai_text.append(delta.text)
                        final_message = stream.get_final_message()
                except Exception as e:
                    self.log.error("[审查] 请求失败: %s", e)
                    self.error.emit(f"审查请求失败: {e}")
                    return

                stop_reason = final_message.stop_reason
                ai_text = "".join(full_ai_text)
                full_ai_text.clear()
                if ai_text:
                    self.log.debug("[审查] AI 输出: %s", ai_text[:300])

                assistant_blocks = []
                for block in final_message.content:
                    if block.type == "text":
                        assistant_blocks.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        assistant_blocks.append({
                            "type": "tool_use", "id": block.id,
                            "name": block.name, "input": block.input,
                        })
                messages.append({"role": "assistant", "content": assistant_blocks})

                if stop_reason != "tool_use":
                    break

                tool_results = []
                for block in final_message.content:
                    if block.type != "tool_use" or self._stop:
                        continue
                    self.log.info("[审查] 工具 → %s", block.name)
                    self.tool_call_start.emit(block.name, block.input)
                    try:
                        method = getattr(toolbox, block.name, None)
                        result = method(**block.input) if method else {"error": f"未知工具: {block.name}"}
                    except Exception as e:
                        result = {"error": f"{type(e).__name__}: {e}"}
                    self.tool_call_end.emit(block.name, result)
                    tool_results.append({
                        "type": "tool_result", "tool_use_id": block.id,
                        "content": _stringify_result(result),
                    })
                if tool_results:
                    messages.append({"role": "user", "content": tool_results})

            self.log.info("[审查] 完成")
        except Exception as e:
            self.log.error("[审查] 异常: %s", traceback.format_exc())
            self.error.emit(f"审查异常: {e}")
        finally:
            self.finished_turn.emit()


class AgentWorker(QThread):
    text_chunk = Signal(str)
    tool_call_start = Signal(str, dict)
    tool_call_end = Signal(str, dict)
    iteration_update = Signal(int)   # 当前轮次
    error = Signal(str)
    finished_turn = Signal()

    def __init__(
        self,
        messages: list,
        system_prompt: str,
        workspace: Path,
        skill_dir: Path | None,
        uploaded_files: List[str] | None = None,
        model: str = DEFAULT_MODEL,
        task_logger: logging.Logger | None = None,
        mode: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.messages = messages
        self.system_prompt = system_prompt
        self.workspace = Path(workspace)
        self.skill_dir = Path(skill_dir) if skill_dir else None
        self.uploaded_files = list(uploaded_files or [])
        self.model = model
        self.log = task_logger or _app_log
        self.mode = mode
        self._stop = False

    def request_stop(self):
        self._stop = True
        self.log.info("用户请求停止")

    def _make_toolbox(self) -> ToolBox:
        readable_roots = [skills_dir()]
        if self.skill_dir:
            readable_roots.append(self.skill_dir)
        return ToolBox(
            workspace=self.workspace,
            readable_roots=readable_roots,
            readable_files=self.uploaded_files,
            extra_writable_roots=[output_dir(), output_dir().parent],
            mode=self.mode,
        )

    def run(self):
        self.log.info("Agent 启动 model=%s workspace=%s", self.model, self.workspace)
        self.log.debug("system_prompt_length=%d chars", len(self.system_prompt))
        try:
            client = anthropic.Anthropic(
                api_key=ANTHROPIC_API_KEY,
                base_url=ANTHROPIC_BASE_URL,
                default_headers={"User-Agent": CLAUDE_USER_AGENT},
            )
            toolbox = self._make_toolbox()
            tools = tool_definitions()
            full_ai_text: list[str] = []

            for iteration in range(MAX_TOOL_ITERATIONS):
                if self._stop:
                    self.log.info("Agent 已停止（iteration=%d）", iteration)
                    break

                self.log.info("--- 轮次 %d 开始请求 ---", iteration + 1)
                self.iteration_update.emit(iteration + 1)
                # 记录消息结构（方便排查图片问题）
                if iteration == 0 and self.messages:
                    first = self.messages[0]
                    c = first.get("content", "")
                    if isinstance(c, list):
                        img_cnt = sum(1 for b in c if isinstance(b, dict) and b.get("type") == "image")
                        self.log.info("首条消息含 %d 个图片 block，共 %d 个 block", img_cnt, len(c))
                    else:
                        self.log.info("首条消息为纯文字")
                try:
                    with client.messages.stream(
                        model=self.model,
                        max_tokens=MAX_TOKENS_PER_TURN,
                        system=self.system_prompt,
                        tools=tools,
                        messages=self.messages,
                    ) as stream:
                        for event in stream:
                            if self._stop:
                                break
                            etype = getattr(event, "type", "")
                            if etype == "content_block_delta":
                                delta = getattr(event, "delta", None)
                                if delta and delta.type == "text_delta":
                                    self.text_chunk.emit(delta.text)
                                    full_ai_text.append(delta.text)

                        final_message = stream.get_final_message()
                except Exception as e:
                    self.log.error("模型请求失败: %s: %s", type(e).__name__, e, exc_info=True)
                    self.error.emit(f"模型请求失败: {type(e).__name__}: {e}")
                    return

                stop_reason = final_message.stop_reason
                self.log.info("轮次 %d 完成 stop_reason=%s", iteration + 1, stop_reason)

                # 记录 AI 本轮输出的文字
                ai_text_this_turn = "".join(full_ai_text)
                full_ai_text.clear()
                if ai_text_this_turn:
                    self.log.debug("AI 回复（%d chars）: %s", len(ai_text_this_turn),
                                   ai_text_this_turn[:500] + ("..." if len(ai_text_this_turn) > 500 else ""))

                assistant_blocks = []
                for block in final_message.content:
                    if block.type == "text":
                        assistant_blocks.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        assistant_blocks.append({
                            "type": "tool_use", "id": block.id,
                            "name": block.name, "input": block.input,
                        })

                self.messages.append({"role": "assistant", "content": assistant_blocks})

                # token 上限被截断 → 自动续写
                if stop_reason in (None, "max_tokens"):
                    self.log.warning("token 上限触发（stop_reason=%s），自动续写", stop_reason)
                    self.text_chunk.emit("\n▶ 续写中…\n")
                    self.messages.append({
                        "role": "user",
                        "content": (
                            "[系统自动续写] 请继续完成上面未完成的内容。"
                            "重要提醒：如果你尚未向用户展示确认单并收到用户的明确确认，"
                            "必须先输出完整确认单，停下来等待用户回复，不得直接执行修改。"
                        ),
                    })
                    continue

                if stop_reason != "tool_use":
                    break

                tool_results = []
                for block in final_message.content:
                    if block.type != "tool_use":
                        continue
                    if self._stop:
                        break

                    self.log.info("工具调用 → %s  input=%s", block.name,
                                  _truncate_repr(block.input, 300))
                    self.tool_call_start.emit(block.name, block.input)

                    try:
                        method = getattr(toolbox, block.name, None)
                        if method is None:
                            result = {"error": f"未知工具: {block.name}"}
                        else:
                            result = method(**block.input)
                    except Exception as e:
                        result = {"error": f"{type(e).__name__}: {e}"}
                        self.log.exception("工具 %s 抛出异常", block.name)

                    ok = result.get("ok", not result.get("error"))
                    self.log.info("工具结果 ← %s  ok=%s  %s",
                                  block.name, ok, _truncate_repr(result, 400))
                    if result.get("error"):
                        self.log.warning("工具错误详情: %s", result["error"])

                    self.tool_call_end.emit(block.name, result)
                    tool_results.append({
                        "type": "tool_result", "tool_use_id": block.id,
                        "content": _stringify_result(result),
                    })

                if tool_results:
                    self.messages.append({"role": "user", "content": tool_results})

            self.log.info("Agent 完成，共 %d 条消息", len(self.messages))

        except Exception as e:
            self.log.error("Agent 异常: %s", traceback.format_exc())
            self.error.emit(f"Agent 异常: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        finally:
            self.finished_turn.emit()


def _stringify_result(result: Any) -> str:
    import json
    try:
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        return str(result)


def _truncate_repr(obj: Any, max_len: int) -> str:
    import json
    try:
        s = json.dumps(obj, ensure_ascii=False)
    except Exception:
        s = repr(obj)
    return s[:max_len] + "..." if len(s) > max_len else s
