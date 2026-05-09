# 改关卡模式库 modify_playbook v0

> **生成日期**：2026-04-23
> **语料**：61 包跨包分析 + `ref_diff.py` 输出 + 历史对话沉淀
> **用途**：基于已有包改造时的**常见改动模式**。每个模式给出"场景识别 → 最小 diff → 校验"三段式。
> **前置**：开工前必读 `cinematics.md` / `oj_standard_vars.md` / `pitfalls.md`。

---

## 使用方式

1. **先跑 `ref_diff`**：当前包 vs 母本，看机器识别出哪些 diff。
2. **按 "场景识别" 匹配本文件的模式**，查对应的 "最小 diff"。
3. **按 "校验" 清单逐项勾选**，确认没有副作用。

---

## §1 · 模式总览

| 代号 | 模式 | 典型场景 | 最小改动量 |
|---|---|---|---|
| M-1 | **cid 切分练习** | 一包多练换题号 | 2 处 SetVar |
| M-2 | **题目编号替换** | 换题干（cpp/答案/试题号）但演出不变 | solution.json + .cpp + .js |
| M-3 | **提示文案替换** | err_msg 改文案 | 改若干 SetVar("err_msg", ...) 的 literal |
| M-4 | **循环上界调整** | F.tree 的 n 范围 / F.fire 的火堆数 | 若干 If 条件 literal |
| M-5 | **单题 → 循环题** | 挑战2(单值) → 挑战3(for循环) | +T-4 循环演出 + +若干变量 |
| M-6 | **族内替换主角** | 计数机器人换成另一个角色 | Character.AssetId + 若干动画参数 |
| M-7 | **同族加一关** | 练习5/7/9 再加一关 | 照搬，cid 增加 |
| M-8 | **跨族替换演出** | 成长树改日晷 | ⚠️ 等价于重做，不建议走改造路径 |
| M-9 | **增加 cin 校验层** | 从 C-3 最简升级到 F.number | +4 消息 +4 handler |
| M-10 | **学生代码模板升级** | .cpp 学生页增删 | 只改 .cpp 和 .js |
| M-11 | **折叠边界变化→演出结构重构** | 两题 ▼▲ 边界不同，换行/循环位置要动 | 演示值 + Repeat 次数 + 广播位置 |

---

## §2 · 各模式详解

### M-1 · cid 切分练习（一包多练）

**场景识别**：
- 母本是 F.sundial（练习5/7/9）类"一包多练" 结构
- 要求改成"练习 N"，实际只需切换 `cid` 值
- `ref_diff` 输出只显示"2 处 SetVar(cid, ...) 不同"

**最小 diff（2 处）**：

1. `WhenGameStarts` 里的 SetVar：
   ```
   SetVar(cid, "<新值>")
   ```
2. `WhenReceiveMessage("展示关卡效果")` 里的 SetVar：
   ```
   SetVar(cid, "<新值>")     # 必须同步
   ```

**硬规则**：两处值**必须相同**，见 `pitfalls.md` P-3.1。

**校验清单**：
- [ ] `ref_diff <母本> <改后>` 输出**只有这 2 处 SetVar 变化**
- [ ] solution.json 的 name/id 已改
- [ ] cpp 答案页 / 学生页 / .js 已换成新题

**典型参考**：练习5 (cid=1) → 练习7 (cid=2) → 练习9 (cid=3)

---

### M-2 · 题目编号替换（同演出换题干）

**场景识别**：
- 演出保持一致，只是题目编号 / 题干变化
- 学生代码模板不同但关卡骨架不变

**最小 diff**：
1. `solution.json` 里 `name` / `id` / `uuid`（如需新建）
2. `<题号>答案页.cpp` / `<题号>学生页.cpp` / `<题号>.js` 三件套替换
3. `export_info.json` 里的 title / id
4. `.ws` 里**不动**演出逻辑

**校验清单**：
- [ ] `ref_diff` 输出 "props2/EVENT/handlers 完全一致"
- [ ] cpp 的 cin/cout 契约与 L0 骨架的 `cin_cut / cout_cut` 读取逻辑匹配
- [ ] .js 的 noticeDict 键更新（避免 key 冲突）

---

### M-3 · 提示文案替换

**场景识别**：
- 要求改错误提示文案（如 "数字超出范围" → "请输入 1~100 的整数"）
- 其他完全不变

**最小 diff**：
所有 `SetVar(err_msg, "...")` 的**第二参数 literal 文本**。

**注意**：某些包会用 `Concatenate` 拼接文案，要找的是 SetVar 后面挂着的字符串 block，不能只替换一处。

**校验清单**：
- [ ] 用 `ref_diff` 看 SetVar 统计：`err_msg=<literal>` 行数应该减 / 增相同（新 literal 替换老 literal）
- [ ] 所有出错分支都已替换（搜 "传递失败" 的上文）

---

### M-4 · 循环上界调整

**场景识别**：
- 母本有循环演出但上界写死（如挑战3 的 `n<11`）
- 要求支持更大/更小的 n

**最小 diff**：
1. `cin判断` handler 里的 `If ... IsLess(cin_cut[1], ...)` 的阈值
2. `cout判断` 正确分支里的 `If ... And(IsGreater, IsLess)` 的双阈值
3. 循环体 `Repeat(固定N)` 的 N（若题目要求动态则改成 `Repeat(变量)`）

**校验清单**：
- [ ] 把学生输入**贴到新上界**做人工联调（如果改 n<11 到 n<100，就输 n=99 试试）
- [ ] 确认 pitfalls P-2.1（n>上界的哑火）已修复

**硬规则**：若题目可能出现 n>上界的情况，**必须加 else 分支**明确广播"传递失败 + err_msg"，不能依赖沉默。

---

### M-5 · 单题 → 循环题（挑战2 风格 → 挑战3 风格）

**场景识别**：
- 母本是单次判题（if 一次）
- 要求改成循环判题（for N 次 + 每次 if）
- `ref_diff` 会显示：variant 独有 handler `单独判断`, 以及 cout判断 序列显著变长

**最小 diff**（看挑战3 vs 挑战2 的 diff 输出）：
1. 新增 handler：`WhenReceiveMessage("单独判断")`
2. 新增 #EVENT：`单独判断`
3. 新增顶层 UIView（如 `Screen Text.Basic`）用于循环过程展示
4. 改 `cout判断` 正确分支：插入 T-4 循环演出代替 T-3 单次演出
5. 增加变量：`单独判断_i`（循环索引）

**校验清单**：
- [ ] 所有新 handler 挂对节点（Screen Text 而不是 control）
- [ ] 循环上限设合理（见 M-4）
- [ ] `ref_scan` 输出的 hats 增加大约 10~12 个
- [ ] 联调 n=3 / n=10 / n>10 三种情形

**典型参考**：挑战2 → 挑战3（见 `参考-extracted/挑战3/_diff_vs_挑战2.md`）

---

### M-6 · 族内替换主角

**场景识别**：
- 保持演出族（F.tree/F.beast/...），把主角换一个（比如"计数机器人"→"气象机器人"）
- 只换视觉资产，不换行为

**最小 diff**：
1. `scene.children[角色].props.AssetId` 改新 AssetId（见 `asset_catalog.md`）
2. `PlayAnimation` 里的**动画名**若角色动画库不同，要换（见 `animation_dict.md`）
3. 新角色的动画名查 `animation_dict.md`，按新 AssetId 找对应的动画列表

**校验清单**：
- [ ] 新主角的动画名在 `animation_dict.md` 有登记
- [ ] `ref_scan` 输出的 PlayAnimation 表里所有动画名都在新主角的动画库里
- [ ] 模型尺寸（查 `resource_index.jsonl` 的 `size_tier` 字段）和 Position 匹配（主角太大会穿模）

---

### M-7 · 同族加一关（复制 + 微调）

**场景识别**：
- 已有 N 个一包多练（cid=1~N），要加 cid=N+1
- 演出完全族内，题目不同

**最小 diff**：
1. 找族内最相似的现有关卡，`ref_diff` 对比
2. 在 2 处 cid SetVar 加入新值 "N+1"
3. 下游的 `If IsEqual(cid, "N+1")` 分支**新加一组**（文案/参数）
4. solution.json + cpp + js 三件套新增

**校验清单**：
- [ ] 母本的所有 cid 分支数量加 1
- [ ] 新增分支的文案不与现有分支冲突（特别是 err_msg）
- [ ] 联调所有 cid 值（1~N+1）都能正常走通

---

### M-8 · ⚠️ 跨族替换演出（不建议）

**场景识别**：
- 要求把母本的演出风格整个换掉（如 F.tree → F.sundial）
- `ref_diff` 会显示：handler / #EVENT / 场景树大量差异

**建议**：**不要走改造路径**。直接以目标族的标准关卡为母本新建，要省的只是 .cpp / .js 和题干。

若坚持改造，步骤如下（代价极高）：
1. 删光原族的所有演出 handler（fragments）
2. 按目标族的 §3/§4/... 依赖表，一个个加入目标族的 handler 和 #EVENT
3. 场景树里删老主角/加新主角（见 M-6）
4. 重跑所有联调

**预计工时**：比新建一包多出 50%（因为要反复清旧物）。

---

### M-9 · 增加 cin 校验层（C-3 升级到 F.number）

**场景识别**：
- 母本 `cin判断` 只做最简单的范围检查（如 `cin_cut[1] >= 1`）
- 题目新要求"检查输入不是小数"、"不是字母"、"数据个数正确"

**最小 diff**：
1. `#EVENT` 加 4 个：`判断是否有小数`, `判断是否为非数字`, `判断输入数据的个数`, `判断输入数据大小`（后者按需）
2. 加 4 个对应 handler（`control.WhenReceiveMessage("...")`）
3. 改 `cin判断` handler：改成顺序广播这 4 个消息
4. 每个子 handler 内部：If 不满足条件则 `SetVar(err_msg, "<具体提示>")` + `Broadcast(传递失败)`

**校验清单**：
- [ ] 4 个子 handler 的 err_msg 文案彼此区分（"请输入整数" vs "请输入数字" vs ...）
- [ ] 顺序是"浅→深"：先 "是否为数字" → "是否小数" → "个数" → "范围"

**典型参考**：L14-2-低-练习15/16 vs L14-2-低-终极挑战 的 cin 链路差异。

---

### M-10 · 学生代码模板升级

**场景识别**：
- 仅更新学生代码的脚手架（如从 `int main(){}` 改成 `int main(){int x; cin>>x; // TODO}`）
- 关卡演出完全不变

**最小 diff**：
1. `<题号>学生页.cpp` 直接编辑
2. `<题号>答案页.cpp` 按需同步
3. `<题号>.js` 的 noticeDict 若提到代码位置要同步

**校验清单**：
- [ ] .ws 完全不动
- [ ] 新模板 cin/cout 行数与关卡 cin_cut / cout_cut 期待一致

---

### M-11 · 折叠边界变化 → 演出结构重构

**场景识别**：
- 用户提供了两个答案页 cpp（旧题 / 新题），文件名含"答案页"或含 `▼▲` 折叠标记
- `ref_diff` 只能看到值的差异（演示值、SetVar 参数），**但两个 cpp 的 `▼▲` 边界行不同**
- 典型特征：旧题折叠区 B 包含整个外层循环，新题折叠区 B 只含循环体（外层循环头已给出）

**⛔ 关键陷阱**：只看"代码输出什么形状"会漏掉结构改动。必须逐行对比 `▼▲` 边界才能拿到完整改动清单。

**推导步骤**（必须全部完成，不得跳过）：

1. 逐行标出两个 cpp 各折叠区的**起止行内容**
2. 对比折叠区边界是否移动（**不是值变了，是边界行本身变了**）
3. 每个边界移动 → 找到对应的演出积木：

| cpp 层 | 演出层对应积木 |
|--------|--------------|
| 折叠区B包含整个外层 for | 外层 `Repeat` 次数固定为 1，换行在循环体**外** |
| 折叠区B仅含内层循环体（外层 for 头已给出） | 外层 `Repeat` 次数 = n，换行在外层循环体**内** |
| 折叠区B包含 `cout<<endl` | 换行广播（`BroadcastMessageAndWait('换行')`）在 `cmd=cin` 分支 |
| 折叠区B中 `cout<<endl` 在循环内 | 换行广播移入外层 `Repeat` 循环体末尾 |

**最小 diff（示例：挑战2 → 挑战4）**：

1. 演示值：`*OJ-输入信息` 改新输入值，`*OJ-执行结果` 改新期望输出
2. `ListReplaceItemAt` 第3参数：`'1'` → `ListGetItemAt(1, cin_cut)`（外层循环跑 n 次）
3. 外层 `Repeat` 循环体末尾：新增 `BroadcastMessageAndWait('换行')`
4. `cmd=cin` 分支：删除 `BroadcastMessageAndWait('换行')`（换行已移入循环内）

**校验清单**：
- [ ] 两个 cpp 的 `▼▲` 分段全部列出，边界差异已一一标注
- [ ] 每个边界移动都能映射到至少一条演出积木改动
- [ ] `ref_diff` 验证：diff 条目数 = 值类改动 + 结构类改动之和（不多不少）
- [ ] 联调演示值：输入新 n，演出帧数 / 换行次数与 cpp 期望输出一致

---

## §3 · 通用"最小改动"流程

1. **先 diff**：`python scripts/ref_diff.py <母本> <当前> --save`
2. **定位模式**：看 diff 报告匹配本文件哪个 M-*
3. **最小改动**：只改模式列出的内容，其他零动
4. **再 diff 验证**：改完再跑一次 `ref_diff`，看 diff 是否在预期范围内
5. **rescan**：`python scripts/ref_scan.py <当前>` 刷新 _analysis.md
6. **场景联调**：至少跑 3 组输入（边界值 + 正常值 + 错误值）

---

## §4 · 反模式（踩过的弯路）

### A-1 "顺手优化"母本的 props2 结构
**现象**：改一个关卡，顺手删了几个"看起来没用"的变量。
**后果**：某个跨族 handler 读那个变量，静默失败。
**原则**：**非必要不改 props2**。要删变量，先 `ref_scan` 确认没有 SetVar / Variable 引用。

### A-2 "随手改名"让消息更"规范"
**现象**：把 `机器人走到大门前` 改成 `角色走到大门前` 想更通用。
**后果**：所有 `Broadcast("机器人走到大门前")` 的上游失联。
**原则**：保持原字面量；如实在要规范化，必须全局替换 + `ref_scan` 验证 no broken ref。

### A-3 "推测"哪个 handler 可以删
**现象**：`ref_scan` 显示某 handler 只被一个 fragment 调用，判断"只用一次可以内联"。
**后果**：该 handler 也许被云端 / 前端 / 系统消息机制间接触发。
**原则**：除非明确知道调用点，否则**不删 handler**，哪怕只挂一次。

---

## §5 · diff 输出阅读小抄

`ref_diff` 六段的典型含义：

| 段 | 空表示什么 | 有内容表示什么 |
|---|---|---|
| §1 props2 | 变量集完全一致 | 加/删/换族时大量变化 |
| §2 #EVENT | 消息集完全一致 | 加 handler 会在这里反映 |
| §3 handlers | handler 数量一致 + 内容一致 | 9 项以上内容差异 = 重构；3~5 项 = 正常改造 |
| §4 场景树 | 角色/UI 完全一致 | 加 UI 节点 / 换主角时有差异 |
| §5 fragments hat | BlockScript hats 一致 | M-5（单→循环）会大量增加 hat |
| §6 Broadcast 序列 | 同 hat 下演出序列一致 | M-4（上界调整）/ M-3（文案）不会出现在这里，但 M-5 会 |

---

## §6 · 扫描硬约束（从 level-modify SKILL 搬入）

> Agent 扫母本输出 `scripts/_<关卡名>_scripts.md` 时必须遵守，缺一项视为不合格返工。

### §6.1 三栏分类（硬约束）

扫描产物**必须分三栏**，不得混写：

| 栏 | 判据 | 含义 |
|---|---|---|
| **A 活代码** | 从事件块根集合 BFS 可达 | 会真正执行，是"母本现在是怎么跑的"唯一依据 |
| **B1 候补模块** | `head.define == WhenReceiveMessage` 且 `params[0].val == "参数注入"` | 受保护 hat，默认静默，云编译下会被广播激活。严禁当 B2 删 |
| **B2 真遗留** | 非事件块 hat + 无可达路径，或 hat 事件名既非"参数注入"也从未被广播 | ⚠️ 未连接，不会执行，仅供参考 |

**可达性判定**（BFS 根集合 + 可达边）：
- 根集合：`WhenGameStarts` / `WhenReceiveMessage` / `WhenClick` / `WhenKeyPressed` / `Trigger` / `OnMessage` / `OnCollide` 等事件块
- 可达边：`sections[].children[]` + `next` 指针 + `BroadcastMessage("X")` → `WhenReceiveMessage("X")`
- 唯一例外：`WhenReceiveMessage("参数注入")` 即使被广播也**不算 A 栏**，除非本次明确声明激活候补

**B2 的规范化修复**：若 B2 内容是"参数注入"用途（写 `cin_cut` / `*OJ-*`），挂 `WhenReceiveMessage("参数注入")` hat 升格为 B1。**禁止**改成 `WhenGameStarts` 强制启动（破坏架构语义）。

### §6.2 运行时变量覆盖影响表（硬约束）

A 栏渲染活代码时，对以下积木必须显式注明"会覆盖谁 / 下游哪些循环/条件读到"：

| 积木类型 | 必须标注 |
|---|---|
| `SetVar(X, ...)` / `IncVar(X, ...)` | X 在后续哪些 `Repeat(X)` / `If X` / `ListGetItemAt(_, X)` 被读到 |
| `ListReplaceItemAt(i, L, v)` | L[i] 在后续哪些下游被读到，**尤其同一事件链里更早的 Repeat 会不会因此变次数** |
| `ListInsertItemAt / ListDeleteItemAt` | 对 L 长度敏感的所有下游 |

扫描员必须额外产出一张"变量覆盖影响表"，格式：

```markdown
### 运行时变量覆盖影响
| 覆盖位置（路径） | 被覆盖对象 | 新值 | 下游受影响的循环/条件 | 净效果 |
|---|---|---|---|---|
| fragments[2].If(cmd=="cin").children[N] | cin_cut[1] | "1" | 同 handler 更早的 Repeat(ListGetItemAt(1,cin_cut)) | 外层只跑 1 次 |
```

没这张表的扫描汇报视为不合格，主 agent 必须打回让扫描员补齐再开工。

> 历史教训：扫描员按字面渲染双层 `Repeat(cin_cut[1]) × Repeat(z)`，看似直角三角形；实际同一 handler 里先跑了 `ListReplaceItemAt("1","cin_cut","1")`，外层次数被锁为 1，真实效果是一排 n 颗星。

---

## §7 · 联动检查清单（改动时必查）

### §7.1 cin_cut 联动（输入数量/结构变化时）

当 C++ 代码中 `cin >>` 的**数量或语义**发生变化时，必须同步检查：

| 检查项 | 说明 |
|---|---|
| `ListAdd` 数量 | cin_cut 注入值个数 = 代码 cin 次数 |
| 首个索引起点 | 若 `cin_cut[1]` 是元信息（轮次），角色脚本中 `i` 从 `2` 起；若直接是数据，`i` 从 `1` 起 |
| 循环次数逻辑 | `Repeat` / `sy_n` / `IfElse` 的轮次来源是否需要调整 |
| 显示标签 | UI 气泡读取的 `cin_cut[N]` 索引是否随之偏移 |
| cin 范围校验 | `cin判断` handler 中的校验条件是否仍适用，不适用则移除 |

**cin_cut 注入值有效性校验（必做）**：
注入 `ListAdd` 之后、`If(*OJ-Judge == 1)` 之前，加入前置校验块。规则来源：对照 C++ 题目的输入约束或已有 `cin判断` handler。

```
WhenGameStarts
  SetVar("*OJ-Judge", "1")
  ListAdd(值, "cin_cut")            ← 注入数据
  If(<cin_cut 值不满足约束>)         ← 前置校验
    SetVar("err_msg", "<说明>")
    BroadcastMessageAndWait("传递失败")
    StopScript("all")
  If(*OJ-Judge == 0) ...
  If(*OJ-Judge == 1) ...正常展示流程...
```

校验规则推导顺序：
1. 优先复用已有 `cin判断` handler 的范围检查
2. 无 handler 时从 C++ 代码反推：有轮次 `n` → 至少校验 `n >= 1`；循环体 n 次输入 → 校验 `ListLength(cin_cut) == n + 1`
3. 即使注入值完全可控，校验仍保留作防呆保障

### §7.2 事件广播联动（流程变化时）

- 移除某个 `BroadcastMessageAndWait` 时 → 检查接收方 handler 是否成死代码，若是则删除
- 新增广播时 → 检查是否有对应 `WhenReceiveMessage` handler
- 简化分支（如 IfElse 拍平）时 → 检查被删除分支中是否有独立副作用

---

## 相关文档

- `cinematics.md` —— 演出桥段库（改关卡前必读）
- `oj_standard_vars.md` —— 变量/消息 checklist
- `pitfalls.md` —— 已知坑库
- `SKILL.md` —— 主入口
- `../level-modify/SKILL.md` —— 修改关卡的流程（本文件是其"模式知识库"部分）

---

## 修订记录

- **v0（2026-04-23）**：首版，10 条正式模式 + 3 条反模式。基于 `ref_diff 挑战2 挑战3` / `ref_diff 练习5 练习7` 等实测验证。
- **v0.1（2026-04-24）**：从 `level-modify/SKILL.md` 搬入 §6（扫描硬约束：三栏分类 + 变量覆盖影响表）和 §7（联动检查清单：cin_cut + 事件广播），SKILL 主文件精简为纯流程文档。
