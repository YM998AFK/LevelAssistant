#!/usr/bin/env python3
"""
两个操作：
1. 把 object_tags.md 的 大类/子类/标签集合 列合并到 asset_catalog.md MeshPart 表
2. 清理 SKILL.md：删除 第1~10步 workflow 框架（保留 视角配置规则/主角推荐流程/物件选取规则 等实质内容）
"""

import re
from pathlib import Path

BASE = Path(__file__).parent.parent / '.cursor' / 'skills' / 'level-common'


# ─────────────────────────────────────────────────
# 操作 1：合并标签列到 asset_catalog.md
# ─────────────────────────────────────────────────

def load_tag_map():
    tags_file = BASE / 'object_tags.md'
    tag_map = {}  # int(AssetId) -> (大类, 子类, 标签集合)
    for line in tags_file.read_text(encoding='utf-8').splitlines():
        # 匹配数据行：| AssetId | 名称 | prefab | 课程分类 | 大类 | 子类 | 标签集合 |
        m = re.match(r'\|\s*(\d+)\s*\|[^|]*\|[^|]*\|[^|]*\|([^|]+)\|([^|]+)\|([^|]*)\|', line)
        if m:
            asset_id = int(m.group(1))
            dacl = m.group(2).strip()
            subcat = m.group(3).strip()
            tags = m.group(4).strip()
            tag_map[asset_id] = (dacl, subcat, tags)
    print(f"[tags] 从 object_tags.md 载入 {len(tag_map)} 条标签")
    return tag_map


def merge_tags_into_catalog(tag_map):
    catalog_file = BASE / 'asset_catalog.md'
    lines = catalog_file.read_text(encoding='utf-8').splitlines(keepends=True)

    in_meshpart = False
    header_done = False
    sep_done = False
    matched = 0
    unmatched = 0
    new_lines = []

    for line in lines:
        stripped = line.rstrip('\n').rstrip('\r')

        # 进入 MeshPart 节
        if stripped == '## 物件 (MeshPart)':
            in_meshpart = True
            header_done = False
            sep_done = False
            new_lines.append(line)
            continue

        # 离开 MeshPart 节（遇到下一个 ## ）
        if stripped.startswith('## ') and in_meshpart and stripped != '## 物件 (MeshPart)':
            in_meshpart = False

        if not in_meshpart:
            new_lines.append(line)
            continue

        # ── 表头行 ──
        if not header_done and '| AssetId |' in stripped and '| 名称 |' in stripped:
            # 追加三列（若已有则跳过）
            if '| 大类 |' not in stripped:
                line = stripped.rstrip('|').rstrip() + ' | 大类 | 子类 | 标签 |\n'
            header_done = True
            new_lines.append(line)
            continue

        # ── 分隔行（---|---）──
        if header_done and not sep_done and re.match(r'\|[-| ]+\|', stripped):
            if '---|---|---|' not in stripped:
                line = stripped.rstrip('|').rstrip() + '---|---|---|\n'
            sep_done = True
            new_lines.append(line)
            continue

        # ── 数据行 ──
        m = re.match(r'\|\s*(\d+)\s*\|', stripped)
        if m and header_done:
            asset_id = int(m.group(1))
            # 若行尾已有 3 列标签，跳过
            if stripped.count('|') >= 9:
                new_lines.append(line)
                continue
            if asset_id in tag_map:
                dacl, subcat, tags = tag_map[asset_id]
                line = stripped.rstrip('|').rstrip() + f' | {dacl} | {subcat} | {tags} |\n'
                matched += 1
            else:
                line = stripped.rstrip('|').rstrip() + ' |  |  |  |\n'
                unmatched += 1
            new_lines.append(line)
            continue

        new_lines.append(line)

    catalog_file.write_bytes(''.join(new_lines).encode('utf-8'))
    print(f"[catalog] MeshPart 行：{matched} 已标注，{unmatched} 暂无标签")
    print(f"[catalog] asset_catalog.md 已更新")


# ─────────────────────────────────────────────────
# 操作 2：清理 SKILL.md
# ─────────────────────────────────────────────────

def delete_between(text, start, end_exclusive, label=''):
    """删除 [start, end_exclusive) 区间的内容（end_exclusive 保留）"""
    si = text.find(start)
    if si == -1:
        print(f"  [SKIP] 未找到起点: {start[:60]!r}")
        return text
    ei = text.find(end_exclusive, si)
    if ei == -1:
        print(f"  [WARN] 未找到终点: {end_exclusive[:60]!r}")
        return text
    lines_removed = text[si:ei].count('\n')
    tag = label or start[:40]
    print(f"  [DEL] {lines_removed} 行  ← {tag!r}")
    return text[:si] + text[ei:]


def clean_skill():
    skill_file = BASE / 'SKILL.md'
    content = skill_file.read_text(encoding='utf-8')
    before_size = len(content)

    # 1. 删除"生成流程 compat note"+ 参数槽强制校验 mini-note
    #    （保留后面的"📖 13 条设计规则速查"）
    content = delete_between(
        content,
        '\n### 生成流程（新建关卡）\n',
        '\n### 📖 13 条设计规则速查',
        '生成流程 compat note + 参数槽强制校验 mini'
    )

    # 2. 删除 第1步 的 AskQuestion 提问区块 + 默认角色参数行
    #    （保留 ### 设计师输入角色名… 及后续子节）
    content = delete_between(
        content,
        '\n## 第1步：主角\n',
        '\n### 设计师输入角色名时的动画谱校验流程\n',
        '第1步：主角 提问区块'
    )

    # 3. 删除 第2步 + 第3步（含前面的 --- 分隔符）
    content = delete_between(
        content,
        '\n---\n\n## 第2步：关卡运行模式',
        '\n## 第4步：视角配置\n',
        '第2步 + 第3步'
    )

    # 4. 重命名 第4步：视角配置
    content = content.replace(
        '\n## 第4步：视角配置\n',
        '\n## 视角配置规则（物件数与摄像机预设）\n'
    )
    print("  [REN] 第4步：视角配置 → 视角配置规则（物件数与摄像机预设）")

    # 5. 删除 第5步：关卡流程说明（含前面的 ---）
    content = delete_between(
        content,
        '\n---\n\n## 第5步：关卡流程说明\n',
        '\n## 第5步后：主角推荐流程（强制）\n',
        '第5步：关卡流程说明'
    )

    # 6. 重命名 第5步后：主角推荐流程
    content = content.replace(
        '\n## 第5步后：主角推荐流程（强制）\n',
        '\n## 主角推荐流程\n'
    )
    print("  [REN] 第5步后：主角推荐流程（强制）→ 主角推荐流程")

    # 7. 删除 第6~10步 + AI自动处理（含前面的 ---，到 坐标系统 前）
    content = delete_between(
        content,
        '\n## 第6步：特别关注\n',
        '\n## 坐标系统（重要）\n',
        '第6~10步 + AI自动处理'
    )

    # 8. 删除 ## 生成输出（含前后 ---，到 代码块参数槽规则 前）
    content = delete_between(
        content,
        '\n## 生成输出\n',
        '\n---\n\n## 代码块参数槽规则（必读）\n',
        '生成输出 section'
    )

    after_size = len(content)
    skill_file.write_text(content, encoding='utf-8')
    print(f"[skill] SKILL.md 清理完成：{before_size//1024}KB → {after_size//1024}KB")


# ─────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────

if __name__ == '__main__':
    print("=== 步骤 1：合并 object_tags 标签到 asset_catalog ===")
    tag_map = load_tag_map()
    merge_tags_into_catalog(tag_map)

    print("\n=== 步骤 2：清理 SKILL.md（删除 第1~10步 workflow framing）===")
    clean_skill()

    print("\n完成。")
    print("后续手动操作：")
    print("  - 确认 asset_catalog.md MeshPart 表头已含 大类/子类/标签 列")
    print("  - 确认 SKILL.md 主角推荐流程/物件选取规则/视角配置规则 保留完整")
    print("  - 删除 object_tags.md（若结果满意）")
    print("  - 更新 SKILL.md 文件目录表（object_tags 引用改为 asset_catalog 标注）")
