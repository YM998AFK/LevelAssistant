# resource_index.jsonl 统计报告

> 自动由 [scripts/build_resource_index.py](../../../scripts/build_resource_index.py) 生成。
> 扫描了 61 个参考关卡的 .ws 文件。

## 资产数量

- **Sprite2D**: 735 条（按 sprite_set 合并后；原 2055 帧 → 217 组多帧 + 518 组单帧）
- **MeshPart**: 1065 条
- **Effect**: 488 条
- **Character**: 391 条
- **Scene**: 181 条
- **Music**: 304 条
- **Sound**: 798 条
- **UI**: 2 条
- **合计**: 3985 条

## 角色统计

- 主角候选 (score ≥ 70): **8** 个
- 有使用记录 (usage > 0): **16** 个

## 物件统计

- 有实际尺寸数据: **1022** 个
  - 超小: 49 个
  - 小: 333 个
  - 中: 365 个
  - 大: 122 个
  - 巨: 153 个

## 2D精灵分类统计

- **2D动画/Spine序列帧**: 865 条
- **UI/进度条与数值标签**: 148 条
- **弹窗/通用信息弹窗**: 110 条
- **文字/字母数字素材**: 110 条
- **交互/剧情选项按钮**: 82 条
- **2D动画/未标注序列帧**: 72 条
- **工具/标注辅助遮罩**: 57 条
- **任务/主线任务内容**: 41 条
- **弹窗/道具物品弹窗**: 40 条
- **UI/地图与导航**: 39 条
- **弹窗/书册秘籍攻略**: 39 条
- **交互/自定义代码块**: 35 条
- **弹窗/剧情道具图片**: 32 条
- **收集/技术包图鉴**: 32 条
- **UI/功能面板**: 31 条
- **交互/UI通用按钮组件**: 28 条
- **卡牌/游戏卡牌**: 28 条
- **测试/废弃资源**: 27 条
- **剧情/插画高光图**: 25 条
- **UI/战斗结算界面**: 21 条
- **任务/标题与图标**: 21 条
- **材料/物品图标**: 18 条
- **弹窗/线索调查材料**: 17 条
- **交互/游戏玩法按钮**: 16 条
- **UI/倒计时序列**: 16 条
- **其他/未分类**: 14 条
- **UI/手机通讯界面**: 12 条
- **材料/合成材料图标**: 11 条
- **交互/密码解锁输入**: 9 条
- **剧情/定格CG**: 9 条
- **弹窗/情报信件**: 9 条
- **装饰/电路科技元素**: 9 条
- **文字/讲解对白框**: 6 条
- **剧情/对话气泡**: 4 条
- **UI/车辆演示界面**: 4 条
- **装饰/关卡装饰件**: 4 条
- **其他/节日活动图**: 3 条
- **文字/品牌LOGO**: 3 条
- **任务/其他**: 3 条
- **文字/字幕转场**: 3 条
- **任务/关卡目标提示**: 2 条

## 查询速查（rg 语法）

```bash
# 按 id 精确查询
rg '"id":12156'  _knowledge/resource_index.jsonl
# 按名称模糊查询
rg '小核桃'  _knowledge/resource_index.jsonl
# 所有主角候选
rg '"score":[7-9][0-9]'  _knowledge/resource_index.jsonl
# 有特定动画的角色
rg '"animations".*"beixi"' _knowledge/resource_index.jsonl
# 可交互物件
rg '"can_open":true' _knowledge/resource_index.jsonl
# 中等尺寸物件
rg '"size_tier":"中"' _knowledge/resource_index.jsonl
# 所有场景
rg '"type":"Scene"' _knowledge/resource_index.jsonl
# 2D精灵 - 按分类查询
rg '"sprite_category":"交互/剧情选项按钮"' _knowledge/resource_index.jsonl
rg '"sprite_category":"弹窗/' _knowledge/resource_index.jsonl
rg '"sprite_category":"UI/' _knowledge/resource_index.jsonl
rg '"sprite_category":"2D动画/' _knowledge/resource_index.jsonl
# 2D精灵 - 多帧动画（有 fps 字段）
rg '"fps":24' _knowledge/resource_index.jsonl
# 2D精灵 - 按时长筛选（超过1秒）
rg '"duration_s":[1-9]' _knowledge/resource_index.jsonl
```
