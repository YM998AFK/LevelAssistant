"""
build_meshpart_tags.py
为 resource_index.jsonl 中所有 MeshPart 条目自动添加三个新 tag 维度：
  - style       （风格，所有 1065 条）
  - level_role  （关卡角色，所有 1065 条）
  - subcategory （补全，仅针对 subcategory 为空的 486 条）
同时更新 category 字段（当 subcategory 被补全时）。
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
JSONL_PATH = ROOT / ".cursor/skills/level-common/resource_index.jsonl"
UNCLASSIFIED_PATH = ROOT / "scripts/_unclassified_meshpart.txt"

# ──────────────────────────────────────────────────
# 1. STYLE 推断规则（按优先级，取第一个命中的关键词）
# ──────────────────────────────────────────────────
STYLE_RULES = [
    (
        [
            "魔法", "法袍", "法阵", "魔镜", "魔杖", "坩埚", "咒", "符咒", "神笔", "锦囊",
            "魔药", "丹炉", "乾坤", "法宝", "魔女", "魔植",
            "仙", "妖", "鬼", "神器", "宝典", "秘籍", "传说", "奇幻", "传奇", "魔力",
            "灵芝", "灵药", "法力", "法术", "神秘", "神奇",
            "穿梭", "时空", "仙草",
            "符", "术", "阵", "杖", "袍", "镜", "宝", "壶", "鼎", "丹", "炉", "釜",
        ],
        "魔法奇幻",
    ),
    (
        [
            "朱雀", "白虎", "青龙", "梼杌", "九婴", "饕餮", "貔貅", "神兽", "毕方",
            "鲲", "凤", "麒麟", "神羽", "龙", "龙蛋", "龙鳞",
            "九转", "还魂", "天书", "神笔造", "乾坤袋", "五彩", "玉砚", "玉墨",
            "八面玲珑", "时日环", "天穹仪", "寻龙", "分金尺",
            "定水神针", "发光时空", "时空之眼",
        ],
        "神话",
    ),
    (
        [
            "芯片", "EMP", "脑机", "脑电波", "能源探头", "进化芯片", "电磁", "雷达",
            "传感", "等离子", "虚拟屏幕", "科技", "蒸汽",
            "无人机", "机甲", "机器", "齿轮", "管道", "电路", "激光", "脉冲",
            "太阳能", "蓄电池", "核心电池", "能源", "智慧核心",
            "科幻", "赛博", "电子", "数字", "超级", "漫波", "脑电", "清道夫",
            "检测", "探测", "红外", "pad",
        ],
        "科幻蒸汽",
    ),
    (
        [
            "马车", "牛车", "古风", "铜", "算盘", "圣旨", "腰牌", "竹", "壁画",
            "鼎", "瓮", "营地", "古代", "宫廷", "王朝", "皇族",
            "毛笔", "玉", "墨", "笔墨", "帝", "将军", "账本", "卷轴", "令牌",
            "古", "旧", "木", "草", "纸", "布", "麻", "绳",
            "青铜", "铸铁", "茶", "陶", "瓷", "竹简", "奏折", "诏书",
            "枪", "刀", "剑", "盾", "弓", "棍", "叉", "锤",
        ],
        "中国古风",
    ),
    (
        ["西方", "城堡", "骑士", "魔龙", "精灵", "矮人", "维京", "欧式", "欧风"],
        "西方奇幻",
    ),
]

# tags 字段里已有风格词 → 直接映射
TAG_STYLE_MAP = {
    "魔法": "魔法奇幻",
    "科幻": "科幻蒸汽",
    "古风": "中国古风",
    "现代": "现代通用",
}


def infer_style(record: dict) -> str:
    tags = record.get("tags") or []
    for tag in tags:
        if tag in TAG_STYLE_MAP:
            return TAG_STYLE_MAP[tag]

    name = record.get("name", "")
    for keywords, style in STYLE_RULES:
        if any(kw in name for kw in keywords):
            return style

    return "现代通用"


# ──────────────────────────────────────────────────
# 2. LEVEL_ROLE 推断规则
# ──────────────────────────────────────────────────

def infer_level_role(record: dict) -> str:
    name = record.get("name", "")
    can_open = record.get("can_open", False)
    collider = record.get("collider", "") or ""
    clips = record.get("clips") or []
    subcategory = record.get("subcategory", "") or ""
    tags = record.get("tags") or []

    if any(k in name for k in ["挂点", "锚点", "空挂点"]):
        return "逻辑锚点"

    if any(k in name for k in ["路线", "路径", "立体路径", "传送履带", "箭头", "指示"]):
        return "路径标记"

    if any(k in name for k in ["传送", "传送门", "传送阵", "传送光柱"]):
        return "传送机关"

    if can_open or "结构件/门" in subcategory or "门" in name:
        return "开门障碍"

    if any(k in subcategory for k in ["桥板", "平台", "地面", "地表"]):
        return "跳跃平台"
    if any(k in name for k in ["桥板", "平台", "跳台", "地板", "地砖"]):
        return "跳跃平台"

    if any(k in tags for k in ["奖品"]) or any(
        k in name for k in ["宝石", "金币", "奖杯", "宝箱", "领奖台", "金蛋", "宝藏"]
    ):
        return "收集目标"

    if not collider:
        return "环境装饰"

    return "阻挡障碍"


# ──────────────────────────────────────────────────
# 3. SUBCATEGORY 补全规则
# ──────────────────────────────────────────────────
SUBCAT_RULES = [
    # CHR3D 角色
    (["_3D精灵", "3D精灵版", "精灵版", "_3D"], "CHR3D", "角色/配角NPC_3D"),
    # 神话神兽
    (["朱雀", "白虎", "青龙", "梼杌", "大鹏", "九婴", "饕餮", "貔貅", "神兽", "虎身人面"], "DECO", "装饰/神话神兽"),
    # 科技装置
    (
        [
            "脑电波", "能源探头", "EMP", "芯片", "进化芯片", "脑机", "电磁板",
            "清道夫", "检测狗", "景王喂食机", "景王电脑", "景王种植机", "智慧核心",
            "自动投喂机", "探头", "探测器", "脑机接口", "传感", "虚拟屏幕",
            "红外遥控器", "pad",
        ],
        "PROP",
        "道具/科技装置",
    ),
    # 材料零件
    (
        [
            "合金", "碎片", "矿石", "碳粉", "硅合金", "铜合金", "硼砂", "妖精金属",
            "建材", "材料条", "材料板", "核心材料", "核心电池", "九婴碎片",
            "意识碎片", "龙鳞", "字母龙鳞",
        ],
        "PROP",
        "道具/材料零件",
    ),
    # 药品丹药
    (
        ["还魂丹", "解毒丹", "蒙汗药", "镇定剂", "魔药", "毒液", "药剂", "生物编码药剂", "绝缘体装甲片"],
        "PROP",
        "道具/药品丹药",
    ),
    # 书籍文件
    (
        [
            "圣旨", "腰牌", "手册", "日记本", "借阅记录", "通关文牒", "账本", "借阅",
            "日记", "地图碎片", "桃源山全图", "记录", "备忘录", "卷", "文书",
            "观光手册", "重生之", "逆袭之", "刺客机关",
        ],
        "PROP",
        "道具/书籍文件",
    ),
    # 钥匙锁
    (
        [
            "密码锁", "鲁班锁", "密码备忘", "令牌", "朋友一生", "不一定唤龙笛",
            "唤龙笛", "鲁班", "锁链", "铁链", "铁锁",
        ],
        "PROP",
        "道具/钥匙锁具",
    ),
    # 武器弹药
    (
        [
            "炮弹", "飞箭", "箭雨", "毒刺", "大炮", "祈雨大炮", "榴莲大炮",
            "蘑菇炮", "蘑菇弹", "子弹", "脉冲弹", "魅惑蘑菇弹", "银制匕首",
            "锄头", "小铲子", "小锄头", "冰箭", "凝胶弹", "发射", "投射",
        ],
        "PROP",
        "道具/武器弹药",
    ),
    # 地砖地面
    (
        ["地砖", "地板", "地毯", "土块", "红土块", "黑土块", "水泥地砖", "营地地砖", "测试灰地砖", "红线框", "绿线框"],
        "NAT",
        "地面/地表",
    ),
    # 平台桥板
    (["立体路径", "传送履带", "线框", "桥板", "搭桥"], "BLD", "基础设施/平台桥板"),
    # 路径标记
    (
        ["空挂点", "运输路线", "路线图", "箭头", "自动行驶路线图", "取货送货路线图", "路线"],
        "BLD",
        "基础设施/路径标记",
    ),
    # 横幅标识
    (["旗子", "横幅", "条幅", "标识", "马撕客旗"], "DECO", "装饰/横幅标识"),
    # 饮品
    (["蜜雪冰牛奶茶", "咖啡杯", "冰沙", "奶茶", "饮料"], "FOOD", "食物/饮品"),
    # 水果
    (
        [
            "香蕉", "榴莲", "西瓜", "菠萝", "芒果", "橙", "草莓", "柠檬", "苹果",
            "凸凹曼西瓜", "超级菠萝", "好大的芝麻", "胡萝卜", "芝麻", "果实",
            "自食奇果", "长生果", "心想事橙",
        ],
        "FOOD",
        "食物/水果",
    ),
    # 加工食品
    (["芒果派", "饼干", "压缩饼干", "茶饮"], "FOOD", "食物/加工食品"),
    # 容器箱子
    (["盲盒", "胶囊存储器", "空盒子", "碎盲盒", "漫波记忆硬盘"], "PROP", "器皿/箱柜"),
    # 装饰光效
    (["影子", "焦黑痕迹", "挣扎痕迹", "空白", "重点区域", "带解锁区域"], "DECO", "装饰/纯视觉"),
    # 神话法器
    (
        [
            "神羽", "五彩神羽", "蜻蜓之翼", "时日环", "发光时空之眼", "待机时空之眼",
            "时空之眼", "天穹仪", "天穹仪破碎版", "定水神针", "乾坤袋",
            "八面玲珑眼", "神笔造墨锦囊", "发光神笔", "神笔-", "乾坤神笔",
        ],
        "PROP",
        "道具/魔法道具",
    ),
    # 岩石矿物
    (
        ["火晶", "燃烧的火晶", "陨石", "时空之石", "混沌星核", "神星核", "星核"],
        "NAT",
        "岩石/矿物",
    ),
    # 特殊食材
    (["金蛋", "木咋特鸟蛋", "鸟蛋", "珍珠", "贝壳"], "FOOD", "食物/特殊食材"),
    # 水体
    (["毒水池", "水池盖子", "游动浮光鲤", "待机浮光鲤", "浮光鲤"], "NAT", "水体/水坑"),
    # 围栏/牢笼
    (["陷阱", "牢笼", "黄牛铁链", "母龙锁链", "牢", "笼"], "BLD", "基础设施/围栏"),
    # 灯光照明
    (
        ["彩灯", "灯光绿色", "灯光紫色", "灯珠", "蜡烛", "石头路灯", "魔法三色灯", "火堆", "小乌云", "大乌云"],
        "DECO",
        "装饰/照明灯具",
    ),
    # 生活道具
    (
        ["雨伞架", "泥便便", "碎布", "纸张", "纸团", "皇族套装", "布", "脆脆红蛋",
         "小鸡吃的药", "小鸡的装药碗", "尖叫鸡"],
        "PROP",
        "道具/生活用品",
    ),
]


def infer_subcategory(name: str) -> tuple[str, str] | None:
    """返回 (category, subcategory) 或 None（无法推断）"""
    for keywords, cat, subcat in SUBCAT_RULES:
        if any(kw in name for kw in keywords):
            return cat, subcat
    return None


# ──────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────

def main():
    lines = JSONL_PATH.read_text(encoding="utf-8").splitlines()

    total_mesh = 0
    style_added = 0
    role_added = 0
    subcat_filled = 0
    subcat_still_empty = 0
    unclassified_names: list[str] = []

    out_lines: list[str] = []

    for raw in lines:
        raw = raw.strip()
        if not raw:
            out_lines.append(raw)
            continue

        obj = json.loads(raw)

        if obj.get("type") != "MeshPart":
            out_lines.append(json.dumps(obj, ensure_ascii=False))
            continue

        total_mesh += 1

        # ── style
        obj["style"] = infer_style(obj)
        style_added += 1

        # ── level_role
        obj["level_role"] = infer_level_role(obj)
        role_added += 1

        # ── subcategory 补全
        if not obj.get("subcategory"):
            result = infer_subcategory(obj.get("name", ""))
            if result:
                cat, subcat = result
                obj["category"] = cat
                obj["subcategory"] = subcat
                subcat_filled += 1
            else:
                subcat_still_empty += 1
                unclassified_names.append(obj.get("name", ""))

        out_lines.append(json.dumps(obj, ensure_ascii=False))

    # 写回 JSONL
    JSONL_PATH.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    # 写未分类名单
    UNCLASSIFIED_PATH.write_text(
        "\n".join(unclassified_names) + "\n", encoding="utf-8"
    )

    # ── 统计报告
    print("=" * 60)
    print("MeshPart 标签补全统计")
    print("=" * 60)
    print(f"总 MeshPart 条目:         {total_mesh}")
    print(f"style       字段覆盖率:   {style_added}/{total_mesh} ({style_added/total_mesh*100:.1f}%)")
    print(f"level_role  字段覆盖率:   {role_added}/{total_mesh} ({role_added/total_mesh*100:.1f}%)")
    print(f"subcategory 补全成功:     {subcat_filled} 条")
    print(f"subcategory 仍为空:       {subcat_still_empty} 条")
    print(f"未分类名单已写入:         {UNCLASSIFIED_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
