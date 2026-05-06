"""将所有分散的资源文档整合为单一可搜索的 resource_index.jsonl。

数据来源（按优先级）：
  1. asset_catalog.md       — AssetId/名称/动画/大类/标签等基础字段
  2. object_prefab_meta.md  — 物件碰撞体/轴心/clip时长/默认Scale
  3. 参考-extracted/*.ws    — 角色与物件的实际使用次数 + MeshPart 真实尺寸

输出：
  .cursor/skills/level-common/resource_index.jsonl
    每行一个 JSON 对象，对应一个 AssetId
  .cursor/skills/level-common/resource_index_stats.md
    汇总统计报告

查询示例（使用 rg）：
  rg '"id":12156'               resource_index.jsonl   # 精确 id 查询
  rg '"name":"小核桃"'            resource_index.jsonl   # 精确名称
  rg '小核桃'                    resource_index.jsonl   # 模糊名称
  rg '"type":"Character"'       resource_index.jsonl   # 所有角色
  rg '"score":[7-9][0-9]'       resource_index.jsonl   # score>=70 的角色
  rg '"animations".*"beixi"'   resource_index.jsonl   # 有 beixi（悲伤）动画
  rg '"tags".*可交互'            resource_index.jsonl   # 可交互物件
  rg '"size_tier":"中"'          resource_index.jsonl   # 中等尺寸物件
  rg '"type":"Scene"'           resource_index.jsonl   # 所有场景
  rg '"type":"Sound"'           resource_index.jsonl   # 所有音效
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

# ─── 2D精灵分类函数 ───────────────────────────────────────────────────────────
def _classify_sprite2d(sprite_set: str) -> str:
    """根据 sprite_set 名称推断语义分类，写入 sprite_category 字段。

    一级/二级结构，格式为 "大类/子类"。
    """
    s = sprite_set

    # 0. 2D动画
    if re.search(r"[Ss]pine|spiine", s) or re.search(r"伪[Ss]pine|伪spiine", s):
        return "2D动画/Spine序列帧"
    if re.search(r"(L\d+-\d+.*(拿剑|变身|变形|出现|待机|进场|入场|循环))|百灵记忆.绘本动画", s):
        return "2D动画/未标注序列帧"

    # 1. 交互
    if re.match(r"^交互[：;:：]", s):
        return "交互/剧情选项按钮"
    if any(k in s for k in ["二选一", "分镜3交互", "打开机关-按钮", "选项按钮", "多字型按钮",
                             "选项底图", "请给英雄", "没问题", "你来拍", "我来拍",
                             "相信他", "他骗人", "按钮查看图册", "点击交互"]):
        return "交互/剧情选项按钮"
    if any(k in s for k in ["3d按钮", "QWCL", "L1-2交互按钮", "按钮底板", "继续挑战按钮",
                             "增加投影能力按钮", "改造成无人机按钮"]):
        return "交互/UI通用按钮组件"
    if any(k in s for k in ["特效开关", "猜拳", "剪刀石头布", "不太喜欢", "喜欢", "邀请", "不邀请"]):
        return "交互/游戏玩法按钮"
    if any(k in s for k in ["舞台特效代码块", "阿怪舞蹈代码块", "下拉菜单文案",
                             "舞蹈特效下拉菜单", "代码块弹窗"]):
        return "交互/自定义代码块"
    if any(k in s for k in ["密码按键", "密码格子", "密码屏幕", "密码解码背景板",
                             "第六关锁代码", "第七关选中效果", "第七关UI提示"]):
        return "交互/密码解锁输入"

    # 2. 任务
    if re.search(r"任务标题|任务图标|任务栏", s):
        return "任务/标题与图标"
    if re.search(r"第.课任务|C\+\+第.*任务|任务L|配课资源|主线任务", s):
        return "任务/主线任务内容"
    if any(k in s for k in ["关卡1任务目标", "关卡1目标", "机械虎任务时间表"]):
        return "任务/关卡目标提示"
    if "任务" in s:
        return "任务/其他"

    # 3. 弹窗
    if any(k in s for k in ["攻略", "图册", "书本弹窗", "武功秘籍", "武功", "秘笈", "秘籍",
                             "咒语残本", "魔法学院录取", "歌谣手稿", "异闻录",
                             "借阅记录", "欧阳日记本", "图书馆规则", "线索图书", "《密码手册》"]):
        return "弹窗/书册秘籍攻略"
    if re.search(r"弹窗|弹出", s):
        if any(k in s for k in ["道具", "魔法书", "钥匙", "宝典", "天工五绝", "神笔", "王者之剑"]):
            return "弹窗/道具物品弹窗"
        return "弹窗/通用信息弹窗"
    if any(k in s for k in ["飞船防御系统弹窗"]):
        return "弹窗/通用信息弹窗"
    if any(k in s for k in ["智慧核心", "智慧小屋", "魔法屋充能", "道具-", "道具弹窗"]):
        return "弹窗/道具物品弹窗"
    if any(k in s for k in ["相关线索", "线索图示", "欧阳回忆", "借阅记录内页",
                             "欧阳日记本规则", "欧阳日记本内页", "大耳朵图", "大展宏图",
                             "3欧阳在哪", "1欧阳在哪", "2乱码", "4她在画里",
                             "2最多次借阅", "1925年", "欧阳画像", "缺口", "线索图书-底板"]):
        return "弹窗/线索调查材料"
    if any(k in s for k in ["喵皇圣旨", "信鸽情报", "母龙的信", "学霸来信",
                             "正常班半山老师照片", "犯罪侧写", "机械组倒戈",
                             "流浪月球计划", "漫波懦夫"]):
        return "弹窗/情报信件"
    if any(k in s for k in ["茶宠秘笈", "识茶秘笈", "龙王红茶经", "龙王绿茶经",
                             "九转还魂丹", "《妖王星座图》", "神器收集", "工资记账本",
                             "蒸汽宝典", "天工五绝店铺", "碎布", "蒙汗药", "205胶水",
                             "密码备忘录", "社牛水晶球图片", "金蟾花变形魔药",
                             "魅惑菇说明图", "大王花说明图", "金鱼草说明图",
                             "冷南瓜笔记", "防毒材料堆", "契约"]):
        return "弹窗/剧情道具图片"

    # 4. 卡牌
    if re.search(r"^卡牌[_\-]", s) or any(k in s for k in ["恶龙禁锢咒", "全屏_不一定唤龙笛", "神器合集"]):
        return "卡牌/游戏卡牌"

    # 5. 收集
    if re.search(r"^技术包[_\-]|^技术包$", s):
        return "收集/技术包图鉴"
    if re.search(r"^神器收集|^神器合集", s):
        return "收集/神器图鉴"

    # 6. UI
    if any(k in s for k in ["进度条", "墨水进度条", "墨水闪烁", "生产值", "文明值",
                             "药量标签", "轮次标签", "时长标签", "高光点亮", "能量槽"]):
        return "UI/进度条与数值标签"
    if any(k in s for k in ["血条", "血量", "史莱姆血条", "等级界面", "结算界面",
                             "等级徽章", "等级画面", "法师等级"]):
        return "UI/战斗结算界面"
    if any(k in s for k in ["地图", "全览图", "进程图", "大地图", "九婴全览",
                             "全向车自动行驶路线图", "地标名称", "营地周边地图",
                             "黄牛画的地图", "景王定位图", "定位图标", "雪宝头像定位"]):
        return "UI/地图与导航"
    if any(k in s for k in ["手机", "朋友圈", "ui手机", "ui挂断", "ui接听", "ui呼出",
                             "通讯系统界面", "通讯系统_独立小界面", "通讯系统_标题底框", "直播框"]):
        return "UI/手机通讯界面"
    if any(k in s for k in ["熔炉控制面板", "无人机控制", "磁暴线圈的控制面板",
                             "打开机关桥界面", "程序面板", "避雷针操作界面",
                             "屏幕数组容器", "屏幕底板", "雷达面板", "雷达预警界面",
                             "2D火晶能量槽", "标签bg", "密码背景板"]):
        return "UI/功能面板"
    if any(k in s for k in ["倒计时", "陨石", "计时"]):
        return "UI/倒计时序列"
    if any(k in s for k in ["车灯展示", "感应障碍停车", "麦轮车俯视"]):
        return "UI/车辆演示界面"

    # 7. 文字
    if any(k in s for k in ["英文字母", "数字加1", "数字+1", "图标_&和I"]):
        return "文字/字母数字素材"
    if any(k in s for k in ["字幕", "转场字幕", "转场"]):
        return "文字/字幕转场"
    if any(k in s for k in ["核桃编程", "logo", "Logo"]):
        return "文字/品牌LOGO"
    if any(k in s for k in ["讲解框", "对白框"]):
        return "文字/讲解对白框"

    # 8. 剧情
    if any(k in s for k in ["插画", "高光插图", "绘本动画", "全景", "课前插画",
                             "传奇密室插画", "千面记忆"]):
        return "剧情/插画高光图"
    if any(k in s for k in ["定格帧", "阿怪结尾", "回忆效果", "欧阳回忆",
                             "猫meme", "交给我", "帮助他"]):
        return "剧情/定格CG"
    if any(k in s for k in ["气泡", "bubble", "Air bubble", "对话框", "回忆气泡"]):
        return "剧情/对话气泡"
    if any(k in s for k in ["CG", "截图"]):
        return "剧情/定格CG"

    # 9. 材料/图标
    if any(k in s for k in ["硫磺", "火药", "木炭", "硝石", "硼砂", "树脂",
                             "合金材料", "凝胶弹", "火晶原画", "红色货物小块",
                             "保安树种子2D"]):
        return "材料/合成材料图标"
    if any(k in s for k in ["图标-", "图标_"]):
        return "材料/物品图标"
    if any(k in s for k in ["纸张金蛋", "纸张宝刀", "魔法书光效", "flag", "Flag",
                             "增加投影能力", "改造成无人机", "尖尖顶", "金灿灿"]):
        return "材料/物品图标"

    # 10. 工具/标注
    if any(k in s for k in ["红线", "箭头", "凸显框", "红圈", "矩形红框", "矩形",
                             "白底", "蒙版", "mask", "圈圈", "透明框", "缺口",
                             "准心", "红勾", "对勾", "叉", "圆圈", "点",
                             "Alpha", "成功", "失败", "回忆效果", "小手（抚摸）"]):
        return "工具/标注辅助遮罩"
    if any(k in s for k in ["电路", "节点", "磁暴线圈"]):
        return "装饰/电路科技元素"
    if any(k in s for k in ["螺丝", "屏幕装饰"]):
        return "装饰/关卡装饰件"

    # 11. 节日/测试
    if any(k in s for k in ["元旦", "中秋", "节日", "快乐", "瑞龙腾空"]):
        return "其他/节日活动图"
    if any(k in s for k in ["测试", "废弃", "1111", "抠图", "Kanban-aida",
                             "Click here", "Finger_2D", "Aperture"]):
        return "测试/废弃资源"

    return "其他/未分类"


# ─── 路径 ────────────────────────────────────────────────────────────────────
ROOT       = Path(r"c:\Users\Hetao\Desktop\公司")
SKILL_DIR  = ROOT / ".cursor" / "skills" / "level-common"
CATALOG    = SKILL_DIR / "asset_catalog.md"
PREFAB_MD  = SKILL_DIR / "object_prefab_meta.md"
EXTRACTED  = ROOT / "参考-extracted"
OUT_JSONL  = SKILL_DIR / "resource_index.jsonl"
OUT_STATS  = SKILL_DIR / "resource_index_stats.md"

# ─── 动画 → 情绪/能力 映射表（与 build_character_tags.py 保持同步）─────────────
EXPLICIT_MAP: dict[str, tuple[str, str]] = {
    "idle": ("平静", "闲置"), "idle02": ("平静", "闲置"), "idle03": ("平静", "闲置"),
    "idle01": ("平静", "闲置"), "idleL": ("平静", "闲置"),
    "walk": ("-", "走"), "walk2": ("-", "走"),
    "run": ("-", "跑"), "run2": ("-", "跑"),
    "fly": ("-", "飞"), "feixing": ("-", "飞"), "feixing_idle": ("-", "飞"),
    "feixingzhuangtai": ("-", "飞"), "feixingzhuangtai02": ("-", "飞"),
    "piaofu": ("-", "飞"), "piaofu_idle": ("-", "飞"),
    "jump": ("-", "跳"), "swim": ("-", "游泳"),
    "zuo_idle": ("平静", "坐"), "idle(zuo)": ("平静", "坐"),
    "zuozaidishang_loop": ("平静", "坐"), "zuodishangdakeshui": ("平静", "坐"),
    "sleep": ("平静", "睡"), "sleep_strat": ("平静", "睡"),
    "tang-idle": ("平静", "睡"), "tangdi_idle": ("平静", "睡"),
    "idle(zhan)": ("平静", "闲置"), "zhanli": ("平静", "闲置"), "zhanli_loop": ("平静", "闲置"),
    "kaixin_idle": ("开心", "闲置"), "yanyanyixi": ("开心", "瞬时"),
    "dianzan": ("开心", "瞬时"), "deyi": ("自信", "闲置"),
    "xiaodonghua": ("开心", "瞬时"), "xiaodonghua2": ("开心", "瞬时"),
    "chuanqi": ("自信", "闲置"), "dangfeng": ("自信", "闲置"),
    "badao_loop": ("胜利", "闲置"), "xusheng": ("胜利", "瞬时"),
    "guzhang_loop": ("胜利", "瞬时"), "huanhu": ("胜利", "瞬时"),
    "qifen": ("自信", "闲置"),
    "beixi": ("悲伤", "闲置"), "xuruo": ("悲伤", "闲置"), "xuruo_loop": ("悲伤", "闲置"),
    "fangzhibeixi": ("悲伤", "闲置"), "huaguidaku_loop": ("悲伤", "特殊"),
    "guididaku": ("悲伤", "特殊"), "idle_beishang": ("悲伤", "闲置"),
    "qugan": ("悲伤", "闲置"), "chayao": ("悲伤", "瞬时"), "tanqi": ("悲伤", "闲置"),
    "jingya": ("惊讶", "瞬时"), "jingyataitou": ("惊讶", "瞬时"),
    "jingxia": ("惊讶", "瞬时"), "jingkong": ("害怕", "闲置"),
    "jingkong_loop": ("害怕", "闲置"), "jingkongpao": ("害怕", "跑"),
    "zhenjing": ("惊讶", "瞬时"), "yihuo": ("惊讶", "瞬时"), "jingtan": ("惊讶", "瞬时"),
    "jinzhangmaohan": ("害怕", "闲置"), "duoshan": ("害怕", "瞬时"),
    "eyun": ("害怕", "闲置"), "fadou_start": ("害怕", "闲置"),
    "fadou_loop": ("害怕", "闲置"), "fadou_end": ("害怕", "闲置"),
    "shengqi": ("愤怒", "闲置"), "shengqi_loop": ("愤怒", "闲置"),
    "fennuzhiren": ("愤怒", "闲置"), "zhandou_loop": ("战斗", "攻击"),
    "attack": ("战斗", "攻击"), "gongji": ("战斗", "攻击"),
    "juchui": ("战斗", "举物"), "juchuizhanli": ("战斗", "举物"),
    "yaoshou": ("战斗", "攻击"), "huiwu": ("战斗", "攻击"),
    "yundao": ("眩晕", "特殊"), "yundao_loop": ("眩晕", "特殊"),
    "yundaodaiji": ("眩晕", "特殊"), "yundaozaidi": ("眩晕", "特殊"),
    "yundaozaidi_loop": ("眩晕", "特殊"), "yangtouyundaozaidi_loop": ("眩晕", "特殊"),
    "xuanyun_guidishang": ("眩晕", "特殊"), "xuanyun_zhanli": ("眩晕", "闲置"),
    "hunmi_loop": ("眩晕", "特殊"), "hunmipingtang": ("眩晕", "特殊"),
    "vertigo": ("眩晕", "走"), "vertigo_walk": ("眩晕", "走"),
    "zhongdu": ("眩晕", "特殊"), "zhongdu_start": ("眩晕", "特殊"),
    "touyun": ("眩晕", "闲置"), "yundao_shuijiao": ("眩晕", "睡"),
    "yundao_shuizhao": ("眩晕", "睡"),
    "daodi": ("失败", "特殊"), "daodiloop": ("失败", "特殊"), "daodi_loop": ("失败", "特殊"),
    "daodi_end": ("失败", "特殊"), "jifeidaodi": ("失败", "特殊"),
    "jiangluo": ("失败", "特殊"), "shuaidao": ("失败", "特殊"),
    "shuaidao_loop": ("失败", "特殊"), "shuaidaoidle": ("失败", "特殊"),
    "beizadao": ("失败", "特殊"), "beizadao_loop": ("失败", "特殊"),
    "beizadao_zhanqilai": ("失败", "特殊"), "daodiqishen": ("-", "特殊"),
    "beidafei": ("失败", "特殊"),
    "taopao": ("害怕", "跑"), "huangzhangpao": ("害怕", "跑"),
    "taochumimaben": ("害怕", "跑"), "taochumimaben_idle": ("害怕", "闲置"),
    "xiangqianchong": ("-", "跑"), "daoli_run": ("-", "跑"), "daolipao": ("-", "跑"),
    "daoli_idle": ("-", "特殊"), "daolidaiji": ("-", "特殊"),
    "daolixingzou": ("-", "走"), "daoliidle": ("-", "特殊"),
    "taitou_loop": ("平静", "瞬时"), "taitou_Loop": ("平静", "瞬时"),
    "taitou_Loop02": ("平静", "瞬时"), "ditou_idle": ("平静", "闲置"),
    "zhuantou_Loop": ("平静", "瞬时"), "zhuantou_loop": ("平静", "瞬时"),
    "zuokantaitou_Loop": ("平静", "瞬时"), "youkantaitou_Loop": ("平静", "瞬时"),
    "naotou loop": ("平静", "闲置"), "sikao": ("平静", "闲置"),
    "tanshou": ("平静", "瞬时"), "xunwen": ("平静", "瞬时"),
    "jiangjie": ("平静", "瞬时"), "paizhao_idle": ("开心", "闲置"),
    "changge": ("开心", "闲置"), "biwu_idle": ("平静", "闲置"),
    "huidaiji": ("平静", "闲置"),
    "taishou": ("-", "举物"), "taishou_loop": ("-", "举物"), "taishou_end": ("-", "举物"),
    "judongxi_loop": ("-", "举物"), "shoutizi": ("-", "举物"),
    "nawuqi_idle": ("-", "举物"), "najianju_idle": ("-", "举物"),
    "nachulongdi": ("-", "举物"), "shenchushuangshou_loop": ("-", "举物"),
    "shenshoukan_loop": ("-", "举物"), "shenyoushoukan_loop": ("-", "举物"),
    "dakai": ("-", "瞬时"), "dakai_loop": ("-", "瞬时"), "guanbi": ("-", "瞬时"),
    "ketou": ("平静", "瞬时"), "paipai": ("平静", "瞬时"),
    "xiaguibaoquan": ("平静", "瞬时"), "xiaguibaoquan_loop": ("平静", "瞬时"),
    "baoxiongchuifeng": ("自信", "闲置"), "heshui": ("平静", "瞬时"),
    "wanyao_idle": ("平静", "坐"),
}

KEYWORD_RULES: list[tuple[str, str | None, str | None]] = [
    ("_shd", None, None),
    ("kaixin", "开心", "闲置"), ("deyi", "自信", "闲置"), ("dianzan", "开心", "瞬时"),
    ("guzhang", "胜利", "瞬时"), ("badao", "胜利", "闲置"), ("xusheng", "胜利", "瞬时"),
    ("huanhu", "胜利", "瞬时"), ("chuanqi", "自信", "闲置"), ("dangfeng", "自信", "闲置"),
    ("beixi", "悲伤", "闲置"), ("xuruo", "悲伤", "闲置"), ("daku", "悲伤", "特殊"),
    ("beishang", "悲伤", "闲置"), ("tanqi", "悲伤", "闲置"),
    ("jingya", "惊讶", "瞬时"), ("jingtan", "惊讶", "瞬时"), ("jingxia", "惊讶", "瞬时"),
    ("zhenjing", "惊讶", "瞬时"), ("yihuo", "惊讶", "瞬时"),
    ("jingkong", "害怕", "闲置"), ("jingkongpao", "害怕", "跑"),
    ("taopao", "害怕", "跑"), ("duoshan", "害怕", "瞬时"), ("fadou", "害怕", "闲置"),
    ("shengqi", "愤怒", "闲置"), ("fennu", "愤怒", "闲置"),
    ("zhandou", "战斗", "攻击"), ("attack", "战斗", "攻击"), ("gongji", "战斗", "攻击"),
    ("juchui", "战斗", "举物"), ("yaoshou", "战斗", "攻击"), ("huiwu", "战斗", "攻击"),
    ("yundao", "眩晕", "特殊"), ("xuanyun", "眩晕", "特殊"), ("hunmi", "眩晕", "特殊"),
    ("vertigo", "眩晕", "特殊"), ("zhongdu", "眩晕", "特殊"), ("touyun", "眩晕", "闲置"),
    ("daodi", "失败", "特殊"), ("shuaidao", "失败", "特殊"),
    ("jifeidaodi", "失败", "特殊"), ("jiangluo", "失败", "特殊"),
    ("beizadao", "失败", "特殊"), ("beidafei", "失败", "特殊"),
    ("huangzhangpao", "害怕", "跑"), ("ketou", "平静", "瞬时"), ("paipai", "平静", "瞬时"),
    ("sleep", "平静", "睡"), ("tang", "平静", "睡"),
    ("zuo_idle", "平静", "坐"), ("zuozaidishang", "平静", "坐"),
    ("taitou", "平静", "瞬时"), ("ditou", "平静", "闲置"),
    ("zhuantou", "平静", "瞬时"), ("naotou", "平静", "闲置"),
    ("sikao", "平静", "闲置"), ("jiangjie", "平静", "瞬时"),
    ("fly", None, "飞"), ("feixing", None, "飞"), ("piaofu", None, "飞"),
    ("swim", None, "游泳"), ("jump", None, "跳"),
    ("walk", None, "走"), ("run", None, "跑"), ("pao", None, "跑"), ("zoulu", None, "走"),
    ("nawuqi", None, "举物"), ("najianju", None, "举物"),
    ("taishou", None, "举物"), ("shouti", None, "举物"),
    ("judongxi", None, "举物"), ("dakai", None, "瞬时"), ("guanbi", None, "瞬时"),
    ("idle", "平静", "闲置"),
]

SPECIES_RULES: list[tuple[list[str], str]] = [
    (["机甲", "机器人", "机械", "jiqiren", "机"], "机械"),
    (["核桃车", "飞机", "越野车", "车", "飞车"], "交通工具"),
    (["龙王", "青龙", "白虎", "朱雀", "大鹏", "金翅", "凤", "麒麟", "毕方",
      "饕餮", "貔貅", "夸浮", "九婴", "鹤仙", "黄大仙", "龙椅",
      "神秘人", "仙", "妖", "鬼"], "神话"),
    (["鸭", "鹅", "鹦鹉", "鹤", "鸟", "鸡", "雀", "鹏"], "动物-鸟类"),
    (["熊猫", "狐", "马", "牛", "狗", "猫", "虎", "狼", "鹿", "羊", "兔",
      "螃蟹", "鱼", "蛙", "龟", "鸡蛋", "卡皮巴拉", "菠萝卡皮巴拉",
      "蟹", "鲲", "土拨鼠", "青蛙", "鸭子", "河马", "雪球"], "动物"),
    (["食人花"], "植物"),
]

EMOTION_ORDER = ["开心", "胜利", "自信", "悲伤", "惊讶", "害怕",
                 "愤怒", "战斗", "眩晕", "失败", "平静"]
CAP_ORDER     = ["闲置", "走", "跑", "飞", "跳", "游泳", "坐", "睡",
                 "攻击", "举物", "瞬时", "特殊"]


# ─── 解析辅助 ─────────────────────────────────────────────────────────────────

def _parse_md_table_rows(text: str, start_marker: str, end_markers: list[str]) -> tuple[dict[str, int], list[list[str]]]:
    """从 markdown 文本中提取指定章节的表格行。

    返回 (col_idx, rows)，其中 rows 是已 strip 的单元格列表。
    """
    lines = text.splitlines()
    in_section = False
    header_found = False
    col_idx: dict[str, int] = {}
    rows: list[list[str]] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(start_marker):
            in_section = True
            header_found = False
            col_idx = {}
            rows = []
            continue
        if in_section and any(stripped.startswith(m) for m in end_markers):
            break
        if not in_section or not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not header_found:
            if "AssetId" in cells:
                col_idx = {c: i for i, c in enumerate(cells)}
                header_found = True
            continue
        if cells[0].startswith("-"):
            continue
        if "AssetId" in col_idx and col_idx["AssetId"] < len(cells):
            rows.append(cells)
    return col_idx, rows


def _tag_animation(anim: str) -> tuple[set[str], set[str]]:
    emotions: set[str] = set()
    caps: set[str] = set()
    clean = anim.strip()
    if clean in EXPLICIT_MAP:
        e, c = EXPLICIT_MAP[clean]
        if e and e != "-":
            emotions.add(e)
        if c and c != "-":
            caps.add(c)
        return emotions, caps
    lower = clean.lower()
    for kw, e, c in KEYWORD_RULES:
        if kw in lower:
            if e:
                emotions.add(e)
            if c:
                caps.add(c)
            return emotions, caps
    return emotions, caps


def _classify_species(name: str) -> str:
    for keywords, label in SPECIES_RULES:
        for kw in keywords:
            if kw in name:
                return label
    return "Q版人类"


def _compute_score(emotions: set[str], caps: set[str], usage: int) -> int:
    emotion_part = min(len(emotions - {"平静"}) * 10, 60)
    walk_run_part = 20 if {"走", "跑"}.issubset(caps) else 0
    idle_part = 10 if "闲置" in caps else 0
    usage_part = min(usage * 2, 10)
    return emotion_part + walk_run_part + idle_part + usage_part


def _ordered(s: set[str], order: list[str]) -> list[str]:
    return [x for x in order if x in s] + sorted(s - set(order))


def _fmt(x: float) -> str:
    return str(int(round(x))) if abs(x - round(x)) < 1e-4 else f"{x:.2f}"


def _size_tier(max_edge: float) -> str:
    if max_edge < 0.3:
        return "超小"
    if max_edge < 1.0:
        return "小"
    if max_edge < 3.0:
        return "中"
    if max_edge < 6.0:
        return "大"
    return "巨"


# ─── 第一步：解析 asset_catalog.md ───────────────────────────────────────────

def parse_catalog(text: str) -> dict[str, dict]:
    """返回 {str_id: record_dict}，record 保存 type/name/course/animations/tags 等字段。"""
    records: dict[str, dict] = {}

    # ---- 场景 ----
    col, rows = _parse_md_table_rows(text, "## 场景", ["## "])
    for cells in rows:
        aid = cells[col.get("AssetId", 0)]
        if not aid.isdigit():
            continue
        records[aid] = {
            "id": int(aid), "name": cells[col.get("名称", 1)],
            "type": "Scene",
            "course": cells[col.get("课程分类", 3)] if len(cells) > col.get("课程分类", 3) else "",
        }

    # ---- 角色 ----
    col, rows = _parse_md_table_rows(text, "## 角色", ["## "])
    for cells in rows:
        aid = cells[col.get("AssetId", 0)]
        if not aid.isdigit():
            continue
        anims_raw = cells[col["已知动画"]] if "已知动画" in col and len(cells) > col["已知动画"] else ""
        anims = [a.strip() for a in anims_raw.split(",") if a.strip()]
        scale_raw = cells[col["常用Scale"]] if "常用Scale" in col and len(cells) > col["常用Scale"] else ""
        records[aid] = {
            "id": int(aid), "name": cells[col.get("名称", 1)],
            "type": "Character",
            "course": cells[col.get("课程分类", 3)] if len(cells) > col.get("课程分类", 3) else "",
            "animations": anims,
            "scale": scale_raw or None,
        }

    # ---- 物件 ----
    col, rows = _parse_md_table_rows(text, "## 物件", ["## "])
    for cells in rows:
        aid = cells[col.get("AssetId", 0)]
        if not aid.isdigit():
            continue
        anims_raw = cells[col["已知动画"]] if "已知动画" in col and len(cells) > col["已知动画"] else ""
        anims = [a.strip() for a in anims_raw.split(",") if a.strip()]
        tags_raw = cells[col["标签"]] if "标签" in col and len(cells) > col["标签"] else ""
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        records[aid] = {
            "id": int(aid), "name": cells[col.get("名称", 1)],
            "type": "MeshPart",
            "course": cells[col.get("课程分类", 3)] if len(cells) > col.get("课程分类", 3) else "",
            "animations": anims,
            "category": cells[col["大类"]] if "大类" in col and len(cells) > col["大类"] else "",
            "subcategory": cells[col["子类"]] if "子类" in col and len(cells) > col["子类"] else "",
            "tags": tags,
            "scale": cells[col["常用Scale"]] if "常用Scale" in col and len(cells) > col["常用Scale"] else None,
        }

    # ---- 2D精灵（按 sprite_set 分组，多帧合并为单条记录）----
    _SPRITE2D_FPS = 24  # Spine 标准帧率
    col, rows = _parse_md_table_rows(text, "## 2D精灵", ["## "])
    # 先按 sprite_set 分桶，保持原始顺序
    _sprite_buckets: dict[str, list[dict]] = {}
    for cells in rows:
        aid = cells[col.get("AssetId", 0)]
        if not aid.isdigit():
            continue
        name_col = "资源名称" if "资源名称" in col else "名称"
        ss = cells[col.get("所属精灵", 1)] if len(cells) > col.get("所属精灵", 1) else ""
        frame = {
            "id":     int(aid),
            "name":   cells[col.get(name_col, 2)],
            "course": cells[col.get("课程分类", 3)] if len(cells) > col.get("课程分类", 3) else "",
        }
        if ss not in _sprite_buckets:
            _sprite_buckets[ss] = []
        _sprite_buckets[ss].append(frame)
    # 合并每个桶
    for ss, frames in _sprite_buckets.items():
        first = frames[0]
        fc = len(frames)
        cat = _classify_sprite2d(ss)
        key = str(first["id"])
        if fc == 1:
            records[key] = {
                "id":              first["id"],
                "name":            first["name"],
                "type":            "Sprite2D",
                "sprite_set":      ss,
                "sprite_category": cat,
                "frame_count":     1,
                "course":          first["course"],
            }
        else:
            records[key] = {
                "id":              first["id"],
                "name":            ss,
                "type":            "Sprite2D",
                "sprite_set":      ss,
                "sprite_category": cat,
                "frame_count":     fc,
                "fps":             _SPRITE2D_FPS,
                "duration_s":      round(fc / _SPRITE2D_FPS, 2),
                "ids":             [f["id"] for f in frames],
                "course":          first["course"],
            }

    # ---- 非视觉资源（Effect / Sound / Music / UI 等）----
    lines = text.splitlines()
    section_type_map = {
        "### 动画特效": "Effect",
        "### 音效": "Sound",
        "### 背景音乐": "Music",
        "### UI 包": "UI",
    }
    cur_type: str | None = None
    header_found = False
    col_idx2: dict[str, int] = {}
    in_nonvis = False

    for line in lines:
        stripped = line.strip()
        if "## 以下资源来自" in stripped:
            in_nonvis = True
            continue
        if not in_nonvis:
            continue
        for marker, t in section_type_map.items():
            if stripped.startswith(marker):
                cur_type = t
                header_found = False
                col_idx2 = {}
                break
        if cur_type is None or not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not header_found:
            if "AssetId" in cells:
                col_idx2 = {c: i for i, c in enumerate(cells)}
                header_found = True
            continue
        if cells[0].startswith("-"):
            continue
        aid = cells[col_idx2.get("AssetId", 0)]
        if not aid.isdigit():
            continue
        name_val = cells[col_idx2["名称"]] if "名称" in col_idx2 and len(cells) > col_idx2["名称"] else ""
        records[aid] = {"id": int(aid), "name": name_val, "type": cur_type}

    return records


# ─── 第二步：解析 object_prefab_meta.md ──────────────────────────────────────

def _parse_clips(clips_str: str) -> list[dict]:
    """解析 'open(2.33s,一次), guan(0.67s,循环), kai' 格式的 clip 列表。

    使用 regex finditer 而非按逗号切分，避免括号内逗号被误切。
    """
    if not clips_str or clips_str.strip() == "-":
        return []
    clips = []
    for m in re.finditer(r'\w+(?:\([^)]+\))?', clips_str):
        token = m.group(0)
        pm = re.match(r'^(\w+)\(([0-9.]+)s,\s*(一次|循环)\)$', token)
        if pm:
            clips.append({"name": pm.group(1), "sec": float(pm.group(2)), "loop": pm.group(3) == "循环"})
        else:
            name_m = re.match(r'^(\w+)', token)
            if name_m:
                clips.append({"name": name_m.group(1)})
    return clips


def _parse_pivot(pivot_str: str) -> str:
    m = re.search(r"\(([^)]+)\)", pivot_str)
    return m.group(1) if m else pivot_str.strip()


def _parse_collider(collider_str: str) -> str:
    m = re.match(r"^(Box|Sphere|Capsule|Mesh|Composite)", collider_str.strip())
    return m.group(1) if m else ""


def _parse_collider_dims(collider_str: str) -> list[float] | None:
    """从 'Box [0.8, 0.7, 0.74]' 提取 [0.8, 0.7, 0.74]，失败返回 None。"""
    m = re.search(r"\[([0-9.,\s]+)\]", collider_str)
    if not m:
        return None
    try:
        vals = [float(x.strip()) for x in m.group(1).split(",")]
        return vals if len(vals) == 3 else None
    except ValueError:
        return None


def _parse_scale_val(scale_str: str) -> list[float] | None:
    """解析默认Scale字段：'[1, 1, 1]' → [1,1,1]；'0.3' → [0.3,0.3,0.3]；失败 None。"""
    if not scale_str:
        return None
    s = scale_str.strip()
    m = re.search(r"\[([0-9.,\s]+)\]", s)
    if m:
        try:
            vals = [float(x.strip()) for x in m.group(1).split(",")]
            return vals if len(vals) == 3 else None
        except ValueError:
            return None
    try:
        v = float(s)
        return [v, v, v]
    except ValueError:
        return None


def parse_prefab_meta(text: str) -> dict[str, dict]:
    """返回 {str_id: {collider, pivot, clips, can_open, default_scale}}

    只解析主表（含 Collider 列的那张表）；文件末尾的动画详情/资源追溯等子表
    会对同一 AssetId 再次出现，用 setdefault 确保只保留主表数据。
    """
    records: dict[str, dict] = {}
    in_main_table = False   # 仅处理含 Collider 列的主表
    col_idx: dict[str, int] = {}

    for line in text.splitlines():
        stripped = line.strip()
        # 遇到新的二级/三级标题则离开主表区域
        if stripped.startswith("##") or stripped.startswith("###"):
            if in_main_table:
                break           # 主表只有一张，遇到下一节就停止
            continue
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not in_main_table:
            if "AssetId" in cells and "Collider" in cells:
                col_idx = {c: i for i, c in enumerate(cells)}
                in_main_table = True
            continue
        if cells[0].startswith("-"):
            continue

        aid = cells[col_idx.get("AssetId", 0)]
        if not aid.isdigit():
            continue

        def _get(key: str, _cells=cells, _idx=col_idx) -> str:
            idx = _idx.get(key)
            if idx is None or len(_cells) <= idx:
                return ""
            return _cells[idx]

        clips_raw = _get("Animator clip (时长/循环)")
        clips = _parse_clips(clips_raw)
        can_open = any(
            c.get("name", "").lower() in {"open", "dakai", "kai", "zhankai", "kaimen"}
            for c in clips
        )
        records.setdefault(aid, {
            "collider":      _parse_collider(_get("Collider")),
            "collider_dims": _parse_collider_dims(_get("Collider")),
            "pivot":         _parse_pivot(_get("轴心偏移")),
            "clips":         clips or None,
            "can_open":      can_open if clips else None,
            "default_scale": _get("默认Scale") or None,
        })
    return records


# ─── 第三步：扫描 ws 文件获取使用次数与物件尺寸 ──────────────────────────────

def _parse_vec3(v) -> tuple[float, float, float] | None:
    if isinstance(v, list) and len(v) == 3:
        try:
            return tuple(float(x) for x in v)  # type: ignore
        except (ValueError, TypeError):
            return None
    return None


def _parse_scale_ws(v) -> tuple[float, float, float] | None:
    if isinstance(v, (int, float)):
        s = float(v)
        return (s, s, s)
    if isinstance(v, str):
        try:
            s = float(v)
            return (s, s, s)
        except ValueError:
            return None
    if isinstance(v, list) and len(v) == 3:
        try:
            return tuple(float(x) for x in v)  # type: ignore
        except (ValueError, TypeError):
            return None
    return None


def scan_ws_files(extracted: Path) -> tuple[dict[str, int], dict[str, int], dict[str, dict]]:
    """扫描 extracted/*/*.ws，返回 (char_usage, obj_usage, obj_sizes)。

    - char_usage: {str_id → 出现关卡数}
    - obj_usage:  {str_id → 出现关卡数}（MeshPart+Effect）
    - obj_sizes:  {str_id → {size, scale, tier, max_edge}}
    """
    char_levels:  dict[str, set[str]] = defaultdict(set)
    obj_levels:   dict[str, set[str]] = defaultdict(set)
    # key = (aid, size_tuple, scale_tuple) → count
    size_counts:  dict[tuple, int] = defaultdict(int)

    for ws_path in sorted(extracted.glob("*/*.ws")):
        level = ws_path.parent.name
        try:
            data = json.loads(ws_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        scene = data.get("scene")
        if not scene:
            continue

        char_aids: set[str] = set()
        obj_aids:  set[str] = set()

        def walk(node: dict):
            if not isinstance(node, dict):
                return
            t = node.get("type")
            props = node.get("props", {}) or {}
            aid = props.get("AssetId")
            if aid is not None:
                aid_str = str(aid)
                if t == "Character":
                    char_aids.add(aid_str)
                elif t in ("MeshPart", "Effect"):
                    obj_aids.add(aid_str)
                    if t == "MeshPart":
                        size  = _parse_vec3(props.get("Size"))
                        scale = _parse_scale_ws(props.get("Scale"))
                        if size and scale:
                            size_counts[(aid_str, size, scale)] += 1
            for child in node.get("children", []) or []:
                walk(child)

        walk(scene)
        for aid in char_aids:
            char_levels[aid].add(level)
        for aid in obj_aids:
            obj_levels[aid].add(level)

    char_usage = {aid: len(levels) for aid, levels in char_levels.items()}
    obj_usage  = {aid: len(levels) for aid, levels in obj_levels.items()}

    # 聚合 MeshPart 主尺寸（出现次数最多的 size×scale 组合）
    total_nodes: dict[str, int] = defaultdict(int)
    for (aid, _s, _sc), cnt in size_counts.items():
        total_nodes[aid] += cnt

    obj_sizes: dict[str, dict] = {}
    for aid in total_nodes:
        combos = [
            (size, scale, cnt)
            for (a, size, scale), cnt in size_counts.items()
            if a == aid
        ]
        combos.sort(key=lambda x: -x[2])
        primary_size, primary_scale, _ = combos[0]
        real = (
            primary_size[0] * primary_scale[0],
            primary_size[1] * primary_scale[1],
            primary_size[2] * primary_scale[2],
        )
        max_edge = max(real)
        obj_sizes[aid] = {
            "size":       [round(primary_size[0], 3), round(primary_size[1], 3), round(primary_size[2], 3)],
            "size_scale": round(primary_scale[0], 3) if primary_scale[0] == primary_scale[1] == primary_scale[2] else [round(x, 3) for x in primary_scale],
            "max_edge_m": round(max_edge, 3),
            "size_tier":  _size_tier(max_edge),
        }

    return char_usage, obj_usage, obj_sizes


# ─── 第四步：合并 & 输出 ──────────────────────────────────────────────────────

def enrich_character(rec: dict, char_usage: dict[str, int]) -> dict:
    aid_str = str(rec["id"])
    usage   = char_usage.get(aid_str, 0)
    anims   = rec.get("animations") or []

    emotions: set[str] = set()
    caps:     set[str] = set()
    for anim in anims:
        e, c = _tag_animation(anim)
        emotions |= e
        caps     |= c

    score   = _compute_score(emotions, caps, usage)
    species = _classify_species(rec["name"])

    return {
        **rec,
        "usage":     usage,
        "emotions":  _ordered(emotions, EMOTION_ORDER),
        "abilities": _ordered(caps, CAP_ORDER),
        "score":     score,
        "species":   species,
    }


def enrich_meshpart(rec: dict, obj_usage: dict[str, int],
                    obj_sizes: dict[str, dict], prefab_meta: dict[str, dict]) -> dict:
    aid_str = str(rec["id"])
    meta    = prefab_meta.get(aid_str, {})
    sizes   = obj_sizes.get(aid_str, {})
    out     = {**rec, "usage": obj_usage.get(aid_str, 0)}
    if meta:
        if meta.get("collider"):
            out["collider"] = meta["collider"]
        if meta.get("pivot"):
            out["pivot"] = meta["pivot"]
        if meta.get("clips") is not None:
            out["clips"] = meta["clips"]
        if meta.get("can_open") is not None:
            out["can_open"] = meta["can_open"]
        if meta.get("default_scale"):
            out.setdefault("scale", meta["default_scale"])
    if sizes:
        out.update(sizes)
    elif meta:
        # 用 prefab collider_dims × default_scale 作为兜底尺寸
        cdims = meta.get("collider_dims")
        dscale = _parse_scale_val(meta.get("default_scale") or "")
        if cdims and dscale:
            real = [cdims[i] * dscale[i] for i in range(3)]
            max_edge = max(real)
            # 只补写 size 相关字段，标注来源为 prefab（非 ws 实测）
            out["size"]         = [round(cdims[i], 3) for i in range(3)]
            out["size_scale"]   = round(dscale[0], 3) if dscale[0] == dscale[1] == dscale[2] else [round(x, 3) for x in dscale]
            out["max_edge_m"]   = round(max_edge, 3)
            out["size_tier"]    = _size_tier(max_edge)
            out["size_source"]  = "prefab"   # 标注来源，与 ws 实测区分
    return out


def build_jsonl(records: dict[str, dict], char_usage: dict[str, int],
                obj_usage: dict[str, int], obj_sizes: dict[str, dict],
                prefab_meta: dict[str, dict]) -> list[dict]:
    out_recs: list[dict] = []
    for aid_str, rec in records.items():
        t = rec.get("type")
        if t == "Character":
            out_recs.append(enrich_character(rec, char_usage))
        elif t == "MeshPart":
            out_recs.append(enrich_meshpart(rec, obj_usage, obj_sizes, prefab_meta))
        else:
            out_recs.append({**rec, "usage": obj_usage.get(aid_str, char_usage.get(aid_str, 0))})
    out_recs.sort(key=lambda r: r["id"])
    return out_recs


def write_jsonl(recs: list[dict], path: Path) -> None:
    lines = []
    for r in recs:
        clean = {k: v for k, v in r.items() if v is not None and v != "" and v != []}
        lines.append(json.dumps(clean, ensure_ascii=False, separators=(",", ":")))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_stats(recs: list[dict], path: Path, level_count: int) -> None:
    by_type: dict[str, list] = defaultdict(list)
    for r in recs:
        by_type[r.get("type", "Unknown")].append(r)

    chars = by_type.get("Character", [])
    protagonist_cands = [c for c in chars if c.get("score", 0) >= 70]
    has_size = [r for r in by_type.get("MeshPart", []) if "size_tier" in r]

    lines = [
        "# resource_index.jsonl 统计报告",
        "",
        f"> 自动由 [scripts/build_resource_index.py](../../../scripts/build_resource_index.py) 生成。",
        f"> 扫描了 {level_count} 个参考关卡的 .ws 文件。",
        "",
        "## 资产数量",
        "",
    ]
    for t, lst in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"- **{t}**: {len(lst)} 条")
    lines.extend([
        f"- **合计**: {len(recs)} 条",
        "",
        "## 角色统计",
        "",
        f"- 主角候选 (score ≥ 70): **{len(protagonist_cands)}** 个",
        f"- 有使用记录 (usage > 0): **{sum(1 for c in chars if c.get('usage',0) > 0)}** 个",
        "",
        "## 物件统计",
        "",
        f"- 有实际尺寸数据: **{len(has_size)}** 个",
    ])
    tier_counts: dict[str, int] = defaultdict(int)
    for r in has_size:
        tier_counts[r["size_tier"]] += 1
    for t in ["超小", "小", "中", "大", "巨"]:
        lines.append(f"  - {t}: {tier_counts.get(t, 0)} 个")

    # ── 2D精灵分类统计 ──────────────────────────────────────
    sprites = by_type.get("Sprite2D", [])
    if sprites:
        from collections import Counter as _Counter
        cat_counter: dict[str, int] = dict(_Counter(
            r.get("sprite_category", "其他/未分类") for r in sprites
        ))
        lines.extend([
            "",
            "## 2D精灵分类统计",
            "",
        ])
        for cat in sorted(cat_counter, key=lambda c: -cat_counter[c]):
            lines.append(f"- **{cat}**: {cat_counter[cat]} 条")

    lines.extend([
        "",
        "## 查询速查（rg 语法）",
        "",
        "```bash",
        "# 按 id 精确查询",
        "rg '\"id\":12156'  .cursor/skills/level-common/resource_index.jsonl",
        "# 按名称模糊查询",
        "rg '小核桃'  .cursor/skills/level-common/resource_index.jsonl",
        "# 所有主角候选",
        "rg '\"score\":[7-9][0-9]'  .cursor/skills/level-common/resource_index.jsonl",
        "# 有特定动画的角色",
        'rg \'"animations".*"beixi"\' .cursor/skills/level-common/resource_index.jsonl',
        "# 可交互物件",
        "rg '\"can_open\":true' .cursor/skills/level-common/resource_index.jsonl",
        "# 中等尺寸物件",
        "rg '\"size_tier\":\"中\"' .cursor/skills/level-common/resource_index.jsonl",
        "# 所有场景",
        "rg '\"type\":\"Scene\"' .cursor/skills/level-common/resource_index.jsonl",
        "```",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ─── 主入口 ───────────────────────────────────────────────────────────────────

def main() -> None:
    print("读取 asset_catalog.md …")
    catalog_text = CATALOG.read_text(encoding="utf-8")
    records = parse_catalog(catalog_text)
    print(f"  解析资产: {len(records)} 条")

    print("读取 object_prefab_meta.md …")
    prefab_meta: dict[str, dict] = {}
    if PREFAB_MD.exists():
        prefab_meta = parse_prefab_meta(PREFAB_MD.read_text(encoding="utf-8"))
        print(f"  prefab 元数据: {len(prefab_meta)} 条")
    else:
        print("  未找到 object_prefab_meta.md，跳过")

    print("扫描 ws 文件 …")
    level_count = 0
    if EXTRACTED.exists():
        level_count = sum(1 for _ in EXTRACTED.glob("*/*.ws"))
        char_usage, obj_usage, obj_sizes = scan_ws_files(EXTRACTED)
        print(f"  关卡数: {level_count}")
        print(f"  角色使用记录: {len(char_usage)} 条")
        print(f"  物件使用记录: {len(obj_usage)} 条")
        print(f"  物件尺寸数据: {len(obj_sizes)} 条")
    else:
        print("  未找到 参考-extracted/，跳过 ws 扫描")
        char_usage, obj_usage, obj_sizes = {}, {}, {}

    print("合并数据 …")
    recs = build_jsonl(records, char_usage, obj_usage, obj_sizes, prefab_meta)

    print(f"写出 {OUT_JSONL} …")
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(recs, OUT_JSONL)
    print(f"  共 {len(recs)} 行")

    print(f"写出 {OUT_STATS} …")
    write_stats(recs, OUT_STATS, level_count)

    print("完成！")
    print(f"  JSONL: {OUT_JSONL}")
    print(f"  Stats: {OUT_STATS}")
    print()
    print("查询示例：")
    print(f"  rg '小核桃' \"{OUT_JSONL}\"")
    print(f"  rg '\"type\":\"Character\"' \"{OUT_JSONL}\"")


if __name__ == "__main__":
    main()
