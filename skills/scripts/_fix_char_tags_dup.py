"""离线维护工具：修复 character_tags.md 中重复的角色大类列。
character_tags.md 是 build_character_tags.py 的输出（可再生中间产物），
Agent 查询请使用 resource_index.jsonl，无需读 character_tags.md。
"""
path = r"c:\Users\Hetao\Desktop\公司\.cursor\skills\level-common\character_tags.md"

ROLE_CLASSES = {"主角", "人形角色", "非人形角色", "机械生物",
                "主角/人形角色", "主角/非人形角色", "主角/机械生物"}

with open(path, encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
fixed = 0

for line in lines:
    stripped = line.rstrip("\n")
    parts = stripped.split("|")
    # 检测数据行
    if len(parts) >= 8 and parts[1].strip().isdigit():
        col4 = parts[4].strip()
        col5 = parts[5].strip()
        # 如果 col4 和 col5 都是角色大类值（重复）
        if col4 in ROLE_CLASSES and col5 in ROLE_CLASSES:
            # 删除 col5（重复列）
            parts.pop(5)
            new_lines.append("|".join(parts) + "\n")
            fixed += 1
            continue
    new_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Fixed {fixed} duplicate rows. Total lines: {len(new_lines)}")
