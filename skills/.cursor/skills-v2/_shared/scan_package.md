---
name: scan-package
description: 通用扫包模块。调用方读取本文件后，代入变量执行以下步骤。
---

# 扫包模块

调用方在读取本文件前，需在任务上下文中确认以下变量：

| 变量 | 含义 |
|------|------|
| `EXTRACTED_DIR_PATH` | 解压目录绝对路径（含 `.ws` 文件的子目录） |
| `WS_FILE_PATH` | `.ws` 文件绝对路径 |
| `SKILL_DIR` | Skill 目录绝对路径（系统提示中提供） |

---

## 前置步骤：解压（EXTRACTED_DIR_PATH 尚未就绪时）

若调用方传入的是 zip 文件路径，**必须先调用 `extract_archive` MCP 工具**完成解压，再继续 S1/S2：

```
extract_archive(
  archive_path = <zip 文件绝对路径>,
  dest_dir     = <工作目录>/input_extracted
)
```

> ⚠️ 禁止使用任何 shell 命令（`unzip`、PowerShell `ZipFile`、`tar` 等）替代。  
> 这些命令在路径含中文/空格时会**静默失败**（无报错、无输出）。  
> `extract_archive` 是唯一受支持的解压方式。

解压完成后：
- `EXTRACTED_DIR_PATH` = `extract_archive` 返回的 `dest` 绝对路径
- `WS_FILE_PATH` = `EXTRACTED_DIR_PATH` 内唯一的 `.ws` 文件绝对路径（用 `list_files` 或 `glob` 确认）

---

## 步骤 1 + 2a：S1 / S2a 并行执行（同一消息批次）

**S1 — 包结构全貌**（`ref_diff.py`，两参数均填同一路径，diff 为空属正常，目的是读取各节结构摘要）：

```
run_python(
  script_rel = "<SKILL_DIR>/scripts/ref_diff.py",
  args       = [EXTRACTED_DIR_PATH, EXTRACTED_DIR_PATH]
)
```

**S2a — 轻量扫描**（只输出 §1~§4，用于语义转换和对比卡，约 65 行）：

```
run_python(
  script_rel = "<SKILL_DIR>/scripts/_scan_level.py",
  args       = [EXTRACTED_DIR_PATH, WS_FILE_PATH, "--sections", "1,2,3,4"]
)
```

> 两个调用在同一消息批次并行发出，不串行等待。

---

## 步骤 3：S2a 质检二问

收到 S2a stdout 后，以下两项必须全 YES 才继续：

1. §1~§4 四个区段全部有内容？
2. §4 中存在含 `*OJ-Judge='1'` 的 WhenGameStarts fragment（演示 fragment）？

任一 NO → 脚本执行失败，检查报错原因后重新调用，不得自行代为分析 WS 文件。

---

## 步骤 4：语义转换（质检通过后输出，不得省略）

> **S2b 调用时机**：语义转换完成、M7 对比卡确认后、生成改动清单前，调用 S2b 加载 handler 序列：
> ```
> run_python(
>   script_rel = "<SKILL_DIR>/scripts/_scan_level.py",
>   args       = [EXTRACTED_DIR_PATH, WS_FILE_PATH, "--sections", "5,6,7,8,A,B"]
> )
> ```
> S2b 结果用于提取精确积木路径，填入改造员任务卡的改动清单。

**在内部推导以下摘要（禁止输出给用户，仅作为后续对比卡的信息源）**：

```
【语义转换】
演示值（当前）：*OJ-输入信息=<值>  *OJ-执行结果=<值>
              （来源：S2 §4 WhenGameStarts 的 SetVar）
主流程（当前）：
  1. <handler 名> 触发 → <一句话描述玩家看到的动作，不写积木名>
  2. <handler 名> 触发 → <同上>
  …（按事件触发顺序，直到结束）
改后变化：
  - <改动点>：原来 <行为>，改后 <行为>（对应改动 N）
  …（无改动时填"无"）
```

> **演示值来源规则（§4 多 fragment 时）**：
> S2 §4 下通常存在多个 `WhenGameStarts` fragment，其中：
> - 只含 `SetVar('*OJ-输入信息', '')` 的是**重置 fragment**，演示值为空，**不得用作演示值来源**
> - 同时含 `SetVar('*OJ-Judge', '1')` 的才是**演示 fragment**，按以下优先级读演示值：
>   1. 若该 fragment 有 `SetVar('*OJ-输入信息', '<非空非0值>')` → 直接用该值
>   2. 若 `*OJ-输入信息` 未设置或值为 `''`/`'0'`，但有 `ListAdd ... 'cin_cut'` 积木 → **演示值来源为 cin_cut 预载列表**：`*OJ-输入信息` = 各 ListAdd 值用空格拼接，`*OJ-执行结果` = 根据 cpp 逻辑计算推算
>   3. 两者均无 → 列出该 fragment 全部 SetVar 积木，询问设计师
> - 若没有 `*OJ-Judge='1'` 的 fragment → 取 `*OJ-输入信息` 非空且值不为 `' '` 的那个；若仍有歧义，列出所有候选并询问
>
> 来源说明：
> - 若已读取 `modify_playbook.md` M-11，折叠区分析结论直接填入"改后变化"
> - 无 cpp 文件 / 无模式特定改动时，"改后变化"填"无"
>
> 此摘要留在内部，不进入对比卡或确认单正文。
