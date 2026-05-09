# 动画名 → 情绪/能力标签字典

> **用途：仅供选角时推断角色能力**。当需要判断某角色的动画名对应哪种情绪/能力标签时查此文件。  
> 正常情况下 `resource_index.jsonl` 里已有每个角色的 `emotions`/`abilities` 列表，无需手动推断。  
> 本字典用于：①角色有新动画名未在 JSONL 中识别 ②调试 `build_resource_index.py` 标签逻辑。  
> 数据来源：`scripts/build_resource_index.py` 的 `EXPLICIT_MAP` + `KEYWORD_RULES`（保持同步，改脚本同步改此文件）。

---

## 情绪标签枚举

| 标签 | 典型剧情场合 |
|------|------------|
| 开心 | 过关、答对、获得奖励、升级 |
| 胜利 | 打败BOSS、完成挑战、颁奖 |
| 自信 | 主角登场、帅气亮相 |
| 悲伤 | 失败、难过、同情 |
| 惊讶 | 发现、意外、反转 |
| 害怕 | 紧张、惊慌、逃跑前夕 |
| 愤怒 | 对抗、冲突、反派登场 |
| 战斗 | 打斗、攻击、对战 |
| 眩晕 | 被击中、受挫、头晕 |
| 失败 | 倒地、摔倒、战败 |
| 平静 | 日常、对话、讲解 |

## 能力标签枚举

| 标签 | 说明 |
|------|------|
| 闲置 | 站立 idle，几乎所有角色必有 |
| 走 | walk 类步行 |
| 跑 | run 类奔跑 |
| 飞 | 飞行、漂浮 |
| 跳 | jump |
| 游泳 | swim |
| 坐 | 坐姿 idle / 坐下动作 |
| 睡 | 躺、睡觉 |
| 攻击 | 主动攻击、战斗 |
| 举物 | 抬手、举东西、持道具 |
| 瞬时 | 短暂动作（惊讶一瞬、拍手、打响指） |
| 特殊 | 非通用动作（倒立、转头、骑乘、倒地等） |

---

## 精确匹配表（EXPLICIT_MAP）

> 优先查此表。动画名完全匹配时直接返回，不再走关键字规则。

| 动画名 | 情绪 | 能力 |
|--------|------|------|
| `idle` / `idle01` / `idle02` / `idle03` / `idleL` | 平静 | 闲置 |
| `idle(zhan)` / `zhanli` / `zhanli_loop` | 平静 | 闲置 |
| `walk` / `walk2` | — | 走 |
| `run` / `run2` | — | 跑 |
| `fly` / `feixing` / `feixing_idle` / `feixingzhuangtai` / `feixingzhuangtai02` | — | 飞 |
| `piaofu` / `piaofu_idle` | — | 飞 |
| `jump` | — | 跳 |
| `swim` | — | 游泳 |
| `zuo_idle` / `idle(zuo)` / `zuozaidishang_loop` / `zuodishangdakeshui` | 平静 | 坐 |
| `sleep` / `sleep_strat` / `tang-idle` / `tangdi_idle` | 平静 | 睡 |
| `kaixin_idle` / `paizhao_idle` / `changge` | 开心 | 闲置 |
| `yanyanyixi` / `dianzan` / `xiaodonghua` / `xiaodonghua2` | 开心 | 瞬时 |
| `deyi` / `chuanqi` / `dangfeng` / `qifen` / `baoxiongchuifeng` | 自信 | 闲置 |
| `badao_loop` | 胜利 | 闲置 |
| `xusheng` / `guzhang_loop` / `huanhu` | 胜利 | 瞬时 |
| `beixi` / `xuruo` / `xuruo_loop` / `fangzhibeixi` / `idle_beishang` / `qugan` / `tanqi` | 悲伤 | 闲置 |
| `huaguidaku_loop` / `guididaku` | 悲伤 | 特殊 |
| `chayao` | 悲伤 | 瞬时 |
| `jingya` / `jingyataitou` / `jingxia` / `zhenjing` / `yihuo` / `jingtan` | 惊讶 | 瞬时 |
| `jingkong` / `jingkong_loop` / `jinzhangmaohan` / `eyun` / `fadou_start` / `fadou_loop` / `fadou_end` | 害怕 | 闲置 |
| `jingkongpao` / `taopao` / `huangzhangpao` / `taochumimaben_idle` | 害怕 | 跑 |
| `duoshan` | 害怕 | 瞬时 |
| `shengqi` / `shengqi_loop` / `fennuzhiren` | 愤怒 | 闲置 |
| `zhandou_loop` / `attack` / `gongji` / `yaoshou` / `huiwu` | 战斗 | 攻击 |
| `juchui` / `juchuizhanli` | 战斗 | 举物 |
| `yundao` / `yundao_loop` / `yundaodaiji` / `yundaozaidi` / `yundaozaidi_loop` | 眩晕 | 特殊 |
| `yangtouyundaozaidi_loop` / `xuanyun_guidishang` / `hunmi_loop` / `hunmipingtang` | 眩晕 | 特殊 |
| `zhongdu` / `zhongdu_start` / `touyun` | 眩晕 | 特殊/闲置 |
| `xuanyun_zhanli` | 眩晕 | 闲置 |
| `vertigo` / `vertigo_walk` | 眩晕 | 走 |
| `yundao_shuijiao` / `yundao_shuizhao` | 眩晕 | 睡 |
| `daodi` / `daodiloop` / `daodi_loop` / `daodi_end` | 失败 | 特殊 |
| `jifeidaodi` / `jiangluo` / `shuaidao` / `shuaidao_loop` / `shuaidaoidle` | 失败 | 特殊 |
| `beizadao` / `beizadao_loop` / `beizadao_zhanqilai` / `beidafei` | 失败 | 特殊 |
| `taitou_loop` / `taitou_Loop` / `taitou_Loop02` / `zuokantaitou_Loop` / `youkantaitou_Loop` | 平静 | 瞬时 |
| `ditou_idle` / `naotou loop` / `sikao` / `huidaiji` / `biwu_idle` | 平静 | 闲置 |
| `zhuantou_Loop` / `zhuantou_loop` / `tanshou` / `xunwen` / `jiangjie` | 平静 | 瞬时 |
| `ketou` / `paipai` / `xiaguibaoquan` / `xiaguibaoquan_loop` / `heshui` | 平静 | 瞬时 |
| `wanyao_idle` | 平静 | 坐 |
| `taishou` / `taishou_loop` / `taishou_end` | — | 举物 |
| `judongxi_loop` / `shoutizi` / `nawuqi_idle` / `najianju_idle` | — | 举物 |
| `nachulongdi` / `shenchushuangshou_loop` / `shenshoukan_loop` / `shenyoushoukan_loop` | — | 举物 |
| `dakai` / `dakai_loop` / `guanbi` | — | 瞬时 |
| `xiangqianchong` / `daoli_run` / `daolipao` | — | 跑 |
| `daolixingzou` | — | 走 |
| `daoli_idle` / `daolidaiji` / `daoliidle` | — | 特殊 |

---

## 关键字推导规则（KEYWORD_RULES）

> 精确匹配未命中时，按此表做**子字符串匹配**（动画名转小写后逐行匹配）。  
> ⚠️ `_shd` 前缀 = 骨骼/材质噪声，直接跳过不打标。

| 关键字 | 情绪 | 能力 |
|--------|------|------|
| `kaixin` | 开心 | 闲置 |
| `guzhang` / `badao` / `xusheng` / `huanhu` | 胜利 | 瞬时/闲置 |
| `chuanqi` / `dangfeng` | 自信 | 闲置 |
| `beixi` / `xuruo` / `daku` / `beishang` / `tanqi` | 悲伤 | 闲置/特殊 |
| `jingya` / `jingtan` / `jingxia` / `zhenjing` / `yihuo` | 惊讶 | 瞬时 |
| `jingkong` / `jingkongpao` | 害怕 | 闲置/跑 |
| `taopao` / `duoshan` / `fadou` / `huangzhangpao` | 害怕 | 跑/瞬时/闲置 |
| `shengqi` / `fennu` | 愤怒 | 闲置 |
| `zhandou` / `attack` / `gongji` / `juchui` / `yaoshou` / `huiwu` | 战斗 | 攻击/举物 |
| `yundao` / `xuanyun` / `hunmi` / `vertigo` / `zhongdu` / `touyun` | 眩晕 | 特殊/闲置 |
| `daodi` / `shuaidao` / `jifeidaodi` / `jiangluo` / `beizadao` / `beidafei` | 失败 | 特殊 |
| `ketou` / `paipai` | 平静 | 瞬时 |
| `sleep` / `tang` | 平静 | 睡 |
| `zuo_idle` / `zuozaidishang` | 平静 | 坐 |
| `taitou` / `ditou` / `zhuantou` / `naotou` / `sikao` / `jiangjie` | 平静 | 瞬时/闲置 |
| `fly` / `feixing` / `piaofu` | — | 飞 |
| `swim` | — | 游泳 |
| `jump` | — | 跳 |
| `walk` / `zoulu` | — | 走 |
| `run` / `pao` | — | 跑 |
| `nawuqi` / `najianju` / `taishou` / `shouti` / `judongxi` / `dakai` / `guanbi` | — | 举物/瞬时 |
| `idle`（兜底，最后匹配） | 平静 | 闲置 |

---

## 物种分类规则（SPECIES_RULES）

> 用角色名称关键字推断物种，用于选角时判断"物种契合剧情"。

| 物种 | 名称含关键字 |
|------|------------|
| 机械 | 机甲、机器人、机械、机 |
| 交通工具 | 核桃车、飞机、越野车、车、飞车 |
| 神话 | 龙王、青龙、白虎、朱雀、大鹏、金翅、凤、麒麟、毕方、饕餮、貔貅、夸浮、九婴、鹤仙、黄大仙、仙、妖、鬼 |
| 动物-鸟类 | 鸭、鹅、鹦鹉、鹤、鸟、鸡、雀、鹏 |
| 动物 | 熊猫、狐、马、牛、狗、猫、虎、狼、鹿、羊、兔、螃蟹、鱼、蛙、龟、鸡蛋、蟹、鲲、土拨鼠、青蛙、鸭子、河马、雪球 |
| 植物 | 食人花 |
| Q版人类 | （默认，其他全归此类） |
