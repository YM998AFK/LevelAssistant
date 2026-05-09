# hetu-mcp ↔ skills-v2 术语对照表

> **作用**：hetu-mcp 内部用工程侧命名（来自 Hetu 编辑器源码），skills-v2 用业务侧命名（来自设计师/关卡文档）。两套术语指向同一个东西时容易互相混淆，本表做一次性映射。
>
> **维护时机**：MCP 或 Skill 任一方引入新术语时同步更新。

## 一、积木 / 脚本结构

| MCP 术语 | Skill / 参考包术语 | 说明 |
|---|---|---|
| `workspace` | `.ws` 文件 / "工作区" | Hetu 关卡的完整 JSON 根对象 |
| `fragment` | `入口积木` / `事件积木` / `顶层脚本块` | `WhenGameStarts` / `WhenReceiveMessage` / `WhenTouchBy` 等引擎触发的脚本片段 |
| `block` | `积木` / `积木块` | fragment 树内部的单个可执行节点（如 `SayForSeconds`、`PlayAnimation`） |
| `myblock` | `自定义积木` / `用户函数` | 设计师封装的可复用子程序，签名存 `myBlockRegistry` |
| `define` | `积木类型名` | block 节点里的 `"define": "..."` 字段，如 `"SetVar"` |
| `sections[].params` | `参数槽` / `槽位` | block 的参数列表。参数槽数量必须符合 `verify_blocks.py` 注册表 |
| `param.type` = `"var"` | `固定参数` / `[固]` | 字符串字面值，如变量名、动画名 |
| `param.type` = `"block"` | `嵌套积木` / `[值]` | 参数位里再嵌一个 block（`Add` / `Variable` / `Multiply` 等） |
| `{}` 空 dict | `self 占位` | 占位表示"对自己发作用"，由引擎运行时填充 |
| `next` | `积木链` | 积木之间的顺序连接；禁止新关卡使用（见 `verify_no_new_next.py`） |

## 二、场景树结构

| MCP 术语 | Skill / 设计术语 | 说明 |
|---|---|---|
| `scene` | `根场景` / `Scene` | `.ws` 根对象下的 `scene` 字段，场景树根 |
| `node.type` | `节点类型` | Character / MeshPart / Effect / Folder / BlockScript / Music / Sound / CameraService / Scene |
| `children` | `子节点数组` / `挂载点` | 场景树嵌套关系的载体 |
| `props` | `属性` / `编辑器面板参数` | 节点直接的静态属性（Name / Position / Scale / AssetId / Visible ...） |
| `props.Position` `[x,y,z]` | `位置` | **单位：米**（UI 显示 = ws值 × 30 的厘米；附 Y/Z 轴互换，详见 §四） |
| `props.Size` `[w,h,d]` | `尺寸` / `长宽高` | **单位：米** |
| `props.Scale` | `缩放倍数` | 1.0 = 原始大小 |
| `props.Visible` | `可见性` | 控制编辑器/运行时是否显示 |
| `AssetId` | `资产 ID` | 对应 `asset_catalog.md` 里的资源 |
| `Effect` 子节点 | `特效挂件` | 挂在角色下，Name 会被注册成该角色可播的"动画名" |

## 三、数据 / 工具约定

| MCP 概念 | Skill 对应 | 说明 |
|---|---|---|
| `load_workspace_file(path)` 返回 `{"data": ..., ...}` | 读取 `.ws` | 只返回数据，不原地修改任何东西 |
| `modify_block_parameter(data, ...)` | 改积木参数槽 | **返回新 data**（函数式，不原地改），见 `level-new/agents/creator_agent.md §MCP 函数式 API 规则` |
| `add_fragment(data, frag)` | 追加事件脚本 | 返回新 data |
| `append_block(data, ...)` | 在某 fragment 末尾加积木 | 返回新 data |
| `insert_block_child(data, ...)` | 在某 block 的 `sections[i].params` 插入 | 返回新 data |
| `save_workspace_file(path, data, create_backup=False)` | 写回 `.ws` | **`create_backup=False` 否则会产 `.backup_*.ws`**（冲突 7） |
| `validate_workspace(data)` | 协议校验 | 只查工程级协议；**不查业务规则/单位**（冲突 6） |
| `find_blocks_by_type(data, type)` | 按 define 搜索 | — |

## 四、单位术语（2026-04-27 修正版）

> ⚠️ 2026-04-27 实测修正：Position 的编辑器换算系数为 **× 30**（非 × 100），且 ws 的 Y/Z 轴与编辑器 Y/Z **互换**。

| 字段 | JSON 存储单位 | 编辑器显示换算 |
|---|---|---|
| `Position` / `Size` / `BoundsCenter` / `BoundsSize` | **米（m）** | 厘米（= ws值 × 30）；Position 另有轴互换：ws[1]↔编辑器Z，ws[2]↔编辑器Y |
| `GotoPosition3D` / `GlideSecsToPosition3D` / `MoveSteps` 坐标参数 | **米（m）** | 厘米（ws值 × 30） |
| `CameraFollow` 的 `distance` / `offsetY` / `height` | **厘米（cm）** | 厘米（无需换算） |
| `Scale` | 倍数 | 倍数 |
| `ChangeSize` / `SetSize` | **百分比**（100 = 原始） | 百分比 |
| `SetCameraFOV` | 度 | 度 |
| `PointInDirection` / `PointInPitch` | 度 | 度 |

**ws → 编辑器坐标换算公式**：
```
editor_X(cm) = ws.Position[0] × 30      # 前后方向
editor_Y(cm) = ws.Position[2] × 30      # 左右方向  ← ws[2]，不是[1]
editor_Z(cm) = ws.Position[1] × 30      # 高度方向  ← ws[1]，不是[2]
```

**记忆口诀**：JSON 几乎全是米（写代码直接写米），只有 `CameraFollow` 三参数是厘米异类。读已有 .ws 换算编辑器坐标时用 × 30 + 轴互换。

## 五、常见误会速查

| 听到的描述 | 实际对应 | 注意事项 |
|---|---|---|
| "编辑器里改位置是厘米" | UI 显示层是厘米；JSON 里必须按米写 | 写代码时用米（1m = `"1"`），不是 `"100"`；编辑器显示 = ws值 × 30（附 Y/Z 轴互换） |
| "Position 是米" | **对**（JSON 存储） | 2026-04-27 最终实证结论 |
| "Position 是厘米" | **错**（中间一次搞错过，已作废） | 见本文 §四 2026-04-27 实测修正结论 |
| "CameraFollow 值好大" | 正常，它用厘米（`640` = 6.4m） | 摄像机是唯一历史遗留字段 |
| "MCP 通过校验了" | 只代表协议合法 | 业务规则（动画注册、单位合理、AssetId 存在）需 Skill/agent 自行验证 |
| "积木" / "函数" / "脚本块" | 可能指 `fragment` / `block` / `myblock` | 看语境：事件触发（`When*`）= fragment；可复用子程序 = myblock；其它单个节点 = block |

## 六、扩展记录

- 2026-04-23：首次创建本术语表，起因——MCP API 文档使用 fragment/block/myblock，而参考包评论和 Skill 使用"入口积木/积木/自定义积木"，双方沟通时容易对不上。
- 单位章节与 `presets.md` 零节同步维护，任一方更新另一方必须 review。
