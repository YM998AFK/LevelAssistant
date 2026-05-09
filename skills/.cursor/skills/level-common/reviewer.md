# 审查 / 校验规范（通用）

> **适用对象**：
> - **审查员子 agent**（`explore` + `readonly: true`）执行交付前逐条核查时读本文件
> - **改造员子 agent** 需要运行硬闸门或排查平台导入失败时读本文件
> - **主 agent 质检**：收到子 agent 返回后，对照本文件各节质检问进行验收
>
> 本文件不包含关卡生成/修改规则；规则见 `SKILL.md` 第零章 MUST/NEVER。

---

## §1 校验图例

| 标记 | 含义 | 兜底机制 |
|---|---|---|
| 🤖 **自动** | `verify_gates.py` 闸门机器拦截 | 退出码 0 才允许交付；FAIL 必须修 |
| 🔍 **审查员** | 独立审查员（`explore` + readonly）必检项 | 交付前开一次新子 agent 逐条核对 |
| 👀 **人工** | agent 自觉 + 设计师确认 | 交付消息必须显式声明"已自检"或"已问确认" |

---

## §2 交付消息自检声明（硬格式）

每次交付消息**必须**包含以下两行，缺任一行 → 不许交付：

```
MUST/NEVER 自检：M1-8 ✅ / N1-12 ✅（🤖 verify_gates PASS / 🤖 MCP validate PASS / 🔍 审查员 PASS / 👀 人工已确认）
verify_gates.py   : PASS (4/4)  gate1 params ✅  gate2 no-next ✅  gate3 mcp-validate ✅  gate4 zip-完整性 ✅
validate_workspace: valid=true  error_count=0  warning_count=<N>（warning 无害，只要 error=0）
```

任一条未通过或未确认 → **不许交付**，必须先处理。

审查员报告里涉及 M3/M6/N2/N6/N7/N8/N9/N11/N12 以及**观赏性 / 人类常识**的结论，必须在主 agent 给设计师的交付消息里"转述一遍"，不能只写"审查员 PASS"。

---

## §3 交付前四大硬闸门

### 运行命令

```bash
# 新建关卡
python scripts/verify_gates.py <target_zip>

# 修改关卡（加 --baseline 启用 gate2 strict 模式）
python scripts/verify_gates.py <target_zip> --baseline <母本zip>

# 结构化 JSON 输出（供子 agent 读取）
python scripts/verify_gates.py <target_zip> --json --quiet
```

- 退出码 `0` = 全部 gate PASS，可交付
- 退出码 `2` = 任一 gate FAIL，修复后重打包
- 退出码 `3` = usage / IO / import 错误

### 四闸职责分工

| 闸门 | 检查什么 | 权威来源 | 缺它会漏掉 |
|---|---|---|---|
| `gate1` params-count | 每个积木的 params 槽位数是否符合 registry | `scripts/params_registry.json`（实证扫的 27 个上线关卡） | 参数少一个 / 多一个、嵌套 block 未 `{"type":"block","val":...}` 包装 |
| `gate2` no-new-next | 有无新增 `block.next` 链（会让编辑器只渲染链头）| 所有上线关卡一律用 `children` 平铺实证 | "看起来合法但编辑器只渲染第一块"的隐形事故 |
| `gate3` mcp-validate | 工程级协议合法性（scene / scripts / myblocks 一致性）| `mcp/hetu_mcp/block_models.py` / `workspace_schema.py` | 格式畸形、scene 根节点缺字段、myblock 引用断裂 |
| `gate4` zip-completeness | zip 内必须含 `.ws` + icon `.png` + `solution.json` + `export_info.json` | N11 规则 | 引擎报"zip 包无效，请从源工程重新导出" |

**四者互补，缺一不可**——参数槽通过不代表协议合法，协议合法不代表没 next 事故，next 检查通过不代表 zip 包完整。

> **gate4 已知 false positive**：`verify_gates` gate4 强制要求 `export_info.solutionUid == solution.init`，但平台实际要求 solutionUid 为数字微秒时间戳格式（`"1777453042389527"`）。新建包时 gate4 FAIL 属已知 false positive，不算错；只需保证 N11 三值一致性（见 §5）。

---

## §4 主 agent 质检问（收到子 agent 返回后执行）

### 扫描员质检三问

1. §1~§8 八个区段全部有内容？
2. 表 A（三栏分类）存在且每个 fragment 都有分类标注？
3. 表 B（变量覆盖影响表）存在，且覆盖 A 栏所有 SetVar / IncVar / ListReplaceItemAt / ListInsertItemAt / ListDeleteItemAt？

### 改造员质检五问

1. 改造前确认表存在且每个改动都有列出？
2. 每个改动都有"[改动N] 完成"执行回报？
3. `validate_workspace` error_count == 0（MCP 校验，M8）？
4. `verify_gates` gate1/gate2/gate3 均 PASS（或 FAIL 与母本一致）？
5. `verify_gates` gate4（zip 完整性）PASS 或与母本 FAIL 一致（遗留），或属已知 false positive？

### 审查员质检三问

1. `总体：PASS` 字面存在？
2. 第6项（MUST/NEVER）和第7项（观赏性）所有子条目都是 PASS？
3. M3/M5/M6/N2/N6/N7/N8/N9/N12 以及观赏性（5条）的具体结论已在返回报告中？（主 agent 交付消息必须逐条转述，不能只写"审查员 PASS"）

---

## §5 平台导入 / 覆盖失败排查（Player.log）

当平台报「**覆盖失败**」/「**导入失败**」，必须先查 Player.log：

### Player.log 路径

```
C:\Users\{用户名}\AppData\LocalLow\hetao101\Walnut Coding Curriculum\Player.log
```

> ⚠️ 用户名可能变化。找不到时用 `Glob "C:\Users\*\AppData\LocalLow\hetao101\Walnut Coding Curriculum\Player.log"` 定位，或让用户提供路径。

### 排查步骤

1. `Read Player.log  offset: -200  limit: 200`（读最后 200 行，含最新错误）
2. 搜索关键词：`[OverrideProject] failed` / `exception =` / `InvalidOperationException`
3. 根据异常类型查下表修复

### 已知异常 → 原因 → 修复

| 异常信息 | 根因 | 修复方法 |
|---------|------|---------|
| `JsonData instance doesn't hold an int` | Effect 节点 `"AssetId":"14760"`（字符串）而非 `"AssetId":14760`（整数）；引擎解析 int 字段时崩溃 | 遍历所有 Effect 节点，将 `AssetId` 字符串值转为整数：`props["AssetId"] = int(props["AssetId"])` |
| `[OverrideProject] failed` 无后续异常 | `export_info.solutionUid` 与目标平台项目 ID 不匹配 | 从平台目标项目导出一次，取其 `export_info.json` 里的 `solutionUid`，替换我们包的 `export_info.solutionUid` + `solution.modified` + `projects[0].file` / `projects[0].icon` 路径（三处需一致） |
| `NullReferenceException` in Scene/Character load | 场景树某节点缺必填字段（如 `EulerAngles`、`Scale`） | 用 `validate_workspace` 定位，补全缺失字段 |

### 新建包的 export_info 三值一致规则（N11 落地实现）

```python
solutionUid = str(int(time.time() * 1_000_000))   # 微秒时间戳
sol["modified"]   = int(solutionUid) // 1_000_000
proj["file"]      = f"pangu3d/universe/develop/{solutionUid}/{ws_uuid}.ws"
proj["icon"]      = f"pangu3d/universe/develop/{solutionUid}/{icon_uuid}.png"
export_info["solutionUid"] = solutionUid
```

---

## §6 文件职责说明（当前架构）

本文件（`reviewer.md`）**不是**审查员子 agent 读的文件，是主 agent 和改造员的参考手册。

| 文件 | 用途 | 读者 |
|---|---|---|
| `level-common/reviewer.md`（本文件） | 通用校验规范：校验图例、四大硬闸门、质检问、平台导入失败排查 | **主 agent**（§4 质检问）/ **改造员**（§3 跑闸门 + §5 导入失败排查） |
| `level-common/reviewer_skill.md` | 审查员子 agent 的自包含技能（7 项检查清单 + PASS/FAIL 格式） | **审查员子 agent**（explore + readonly） |
| `level-modify/reviewer_prompt.md` | 修改关卡：审查员派遣模板（告知审查员读 reviewer_skill.md） | 主 agent 填写后发给审查员 |
| `level-new/reviewer_prompt.md` | 新建关卡：审查员派遣模板（告知审查员读 reviewer_skill.md） | 生成员填写后发给审查员 |
