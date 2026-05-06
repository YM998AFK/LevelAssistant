# ⚠️ 离线维护工具：直接修改 character_tags.md 的角色大类列。
# character_tags.md 是 build_character_tags.py 的输出（可再生中间产物），
# Agent 查询请使用 resource_index.jsonl，无需读 character_tags.md。
import re

path = r"c:\Users\Hetao\Desktop\公司\.cursor\skills\level-common\character_tags.md"

SPECIES_TO_CLASS = {
    "Q版人类": "人形角色",
    "神话": "人形角色",
    "动物": "非人形角色",
    "动物-鸟类": "非人形角色",
    "其他/待定": "非人形角色",
    "机械": "机械生物",
}

def get_class(species, score):
    base = SPECIES_TO_CLASS.get(species.strip(), "非人形角色")
    try:
        s = int(score.strip())
        if s >= 70:
            return f"主角/{base}"
    except:
        pass
    return base

with open(path, encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
inserted_count = 0

for line in lines:
    stripped = line.rstrip("\n")

    # 分隔行（------|------）
    if re.match(r'^\|[-| ]+\|$', stripped):
        cols = stripped.split("|")
        if len(cols) == 11:  # 旧格式10列 = 11 parts
            cols.insert(4, "------")
            new_lines.append("|".join(cols) + "\n")
        else:
            new_lines.append(line)
        continue

    # 数据行判断
    parts = stripped.split("|")
    if len(parts) == 11 and parts[1].strip().isdigit():
        # 旧格式（10列 = 11 parts），parts[3]=物种, parts[4]=情绪, parts[9]=分数
        species = parts[3].strip()
        score = parts[9].strip()
        role_class = get_class(species, score)
        parts.insert(4, f" {role_class} ")
        new_lines.append("|".join(parts) + "\n")
        inserted_count += 1
    else:
        new_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Done! Total lines: {len(new_lines)}, Rows updated: {inserted_count}")
