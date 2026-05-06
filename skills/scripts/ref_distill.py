"""ref_distill.py — 跨包模式挖掘 → suggestions.md

输入：61 个包的 _analysis.json（由 ref_scan 产出）
输出：
  参考-extracted/suggestions.md
  - §1 新桥段候选（Broadcast n-gram, len≥4, ≥2 包复现）
  - §2 新变量/消息族群候选（共现聚类）
  - §3 未命中族的包聚类（可能的新族）
  - §4 骨架必需变量/消息修订建议（当前 L0 列表 vs 全量共现）
  - §5 潜在坑候选（某些包独有的特殊模式）
"""
import json
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRACT_DIR = ROOT / '参考-extracted'

# 与 cinematics.md v0 保持一致
KNOWN_FAMILY_MARKERS = {
    'F.tree':    ['机器人左转', '机器人右转', '生成成长树', '机器人发射'],
    'F.sundial': ['打开日晷', '开启测算', '测算输入', '周期循环', '长老验算'],
    'F.beast':   ['鸡狗对打', '鸡狗大战', '机械狗被伤', '机械狗加血', '机械狗格档'],
    'F.nonstd':  ['判断是否输入', '判断输入数据范围', '能否运行'],
}
# 与 oj_standard_vars.md v0 保持一致
L0_VARS = {'#EVENT', '*OJ-Judge', '*OJ-执行结果', '*OJ-输入信息',
           'cin_cut', 'cmd', 'cout_cut', 'n', 'space-flag',
           'variable', '输入元素', '输出元素'}
L0_EVENTS = {'CMD_NewMessage', 'judge', '传递失败', '传递成功', '初始化', '运行'}


def load_all():
    out = []
    for p in sorted(EXTRACT_DIR.iterdir()):
        if not p.is_dir() or p.name == '_mine':
            continue
        aj = p / '_analysis.json'
        if not aj.exists():
            continue
        try:
            out.append(json.load(open(aj, encoding='utf-8')))
        except Exception:
            pass
    return out


def mine_ngrams(records, min_len=4, max_len=10, min_packs=2):
    """跨包 Broadcast n-gram 挖掘。"""
    all_ng = defaultdict(lambda: defaultdict(int))
    for r in records:
        pack = r.get('pack', '?')
        for seq_rec in r.get('broadcast_sequences') or []:
            seq = seq_rec.get('sequence') or []
            for k in range(min_len, max_len + 1):
                if len(seq) < k:
                    continue
                for i in range(len(seq) - k + 1):
                    ng = tuple(seq[i:i + k])
                    # 跳过全同重复
                    if len(set(ng)) == 1:
                        continue
                    all_ng[ng][pack] += 1

    cross = []
    for ng, pm in all_ng.items():
        if len(pm) < min_packs:
            continue
        cross.append({
            'len': len(ng), 'packs': len(pm),
            'total': sum(pm.values()),
            'sequence': list(ng),
            'pack_map': dict(pm),
        })
    # 按"包数多 → 长度长 → 出现总数" 排序
    cross.sort(key=lambda x: (-x['packs'], -x['len'], -x['total']))

    # 去冗余：一个 n-gram 若是另一个更长 n-gram 的连续子序列且包集合相同，去掉短的
    kept = []
    for item in cross:
        skip = False
        for k_item in kept:
            if item['len'] < k_item['len'] and set(item['pack_map']) == set(k_item['pack_map']):
                kng = k_item['sequence']
                ng = item['sequence']
                for i in range(len(kng) - len(ng) + 1):
                    if kng[i:i + len(ng)] == ng:
                        skip = True
                        break
            if skip:
                break
        if not skip:
            kept.append(item)
    return kept


def global_var_event_stats(records):
    """每个变量/消息出现在多少包里。"""
    vc = Counter()
    ec = Counter()
    per_var_packs = defaultdict(set)
    per_ev_packs = defaultdict(set)
    for r in records:
        pk = r.get('pack', '?')
        for v in (r.get('props2_vars') or []):
            vc[v] += 1
            per_var_packs[v].add(pk)
        for e in (r.get('events') or []):
            ec[e] += 1
            per_ev_packs[e].add(pk)
    return vc, ec, per_var_packs, per_ev_packs


def handlers_stats(records):
    hc = Counter()
    per_handler_packs = defaultdict(set)
    for r in records:
        pk = r.get('pack', '?')
        for msg in (r.get('handlers') or {}).keys():
            hc[msg] += 1
            per_handler_packs[msg].add(pk)
    return hc, per_handler_packs


def find_new_family_candidates(records, per_ev_packs, known_markers):
    """找候选新族：消息在 ≥3 包共现且不属于已知族的 marker 集合。"""
    # 已被标为已知族的包
    fam_assigned = {}
    for r in records:
        fams = r.get('family') or []
        if fams:
            fam_assigned[r.get('pack')] = [f['code'] for f in fams]
    unassigned = {r.get('pack') for r in records if r.get('pack') not in fam_assigned}

    # 在 unassigned 里找共现高的消息对/三元组
    events_per_pack = {}
    for r in records:
        pk = r.get('pack')
        if pk in unassigned:
            events_per_pack[pk] = set(r.get('events') or [])

    # 忽略骨架消息
    ignore = L0_EVENTS | {'cin判断', 'cout判断'}

    # 消息 → 未分族的包集合
    msg_to_packs = defaultdict(set)
    for pk, evs in events_per_pack.items():
        for m in evs - ignore:
            msg_to_packs[m].add(pk)

    # 只保留 ≥3 个包共现的消息
    hot = {m: p for m, p in msg_to_packs.items() if len(p) >= 3}

    # 聚类：如果两个消息的包集合差异 < 40% 且都有 ≥3 包，认为是同族
    clusters = []
    used_msgs = set()
    msgs_sorted = sorted(hot.keys(), key=lambda m: -len(hot[m]))
    for m in msgs_sorted:
        if m in used_msgs:
            continue
        cluster_msgs = [m]
        base = hot[m]
        for n in msgs_sorted:
            if n == m or n in used_msgs:
                continue
            nb = hot[n]
            if not nb:
                continue
            jac = len(base & nb) / max(len(base | nb), 1)
            if jac >= 0.6:
                cluster_msgs.append(n)
                used_msgs.add(n)
        used_msgs.add(m)
        # pack 交集
        pack_intersect = set.intersection(*[hot[x] for x in cluster_msgs]) if cluster_msgs else set()
        if len(cluster_msgs) >= 3 and len(pack_intersect) >= 2:
            clusters.append({
                'markers': cluster_msgs,
                'packs': sorted(pack_intersect),
                'size': len(cluster_msgs),
            })
    return clusters, unassigned


def render(records):
    L = []
    L.append("# 跨包挖掘建议 (suggestions)\n")
    L.append(f"> 由 `scripts/ref_distill.py` 生成。包数={len(records)}。")
    L.append(f"> 本文件是**建议**，不直接合入 skill；人工审阅勾选后再改 cinematics / oj_standard_vars / pitfalls。\n")
    L.append("")

    # §1 新桥段候选
    L.append("## §1 新桥段候选（Broadcast n-gram, len≥4, ≥2 包）\n")
    ngrams = mine_ngrams(records, min_len=4, max_len=10, min_packs=2)
    L.append(f"总 {len(ngrams)} 条候选（已去冗余），展示 Top 40：\n")
    for i, ng in enumerate(ngrams[:40]):
        pm = ', '.join(f"{k}×{v}" for k, v in ng['pack_map'].items())
        seq = ' → '.join(ng['sequence'])
        L.append(f"{i+1}. **[L{ng['len']}]×{ng['packs']}包({ng['total']}次)**  `{seq}`")
        L.append(f"    _来源: {pm}_")
    L.append("")

    # §2 变量/消息 / handler 的全量共现分布
    vc, ec, per_var_packs, per_ev_packs = global_var_event_stats(records)
    hc, per_handler_packs = handlers_stats(records)
    total = len(records)

    L.append(f"## §2 骨架必需（L0）复核 · 当前 vs 实际共现\n")
    L.append(f"基准：{total} 包中出现率。\n")
    L.append("### 2.1 变量\n")
    L.append("| 变量 | 出现包数 | 出现率 | v0 L0 里？ |")
    L.append("|---|---|---|---|")
    for v, c in vc.most_common():
        if c < total * 0.6:
            continue
        inL0 = '✅' if v in L0_VARS else ''
        L.append(f"| `{v}` | {c} | {c*100//total}% | {inL0} |")
    L.append("")
    # 建议新增
    near_all = [v for v, c in vc.items() if c >= total * 0.9 and v not in L0_VARS]
    if near_all:
        L.append(f"**建议加入 L0 的变量（≥90% 共现）**：`{', '.join(near_all)}`\n")
    # v0 的 L0 有没有低覆盖的
    low = [v for v in L0_VARS if vc.get(v, 0) < total * 0.8]
    if low:
        L.append(f"**v0 L0 里覆盖率<80% 的变量（是否该降级？）**：")
        for v in low:
            L.append(f"- `{v}`：{vc.get(v,0)}/{total}")
        L.append("")

    L.append("### 2.2 消息\n")
    L.append("| 消息 | 出现包数 | 出现率 | v0 L0 里？ |")
    L.append("|---|---|---|---|")
    for e, c in ec.most_common():
        if c < total * 0.6:
            continue
        inL0 = '✅' if e in L0_EVENTS else ('🟡(L1)' if e in {'cin判断','cout判断'} else '')
        L.append(f"| `{e}` | {c} | {c*100//total}% | {inL0} |")
    L.append("")
    near_all_e = [e for e, c in ec.items() if c >= total * 0.9 and e not in L0_EVENTS]
    if near_all_e:
        L.append(f"**建议加入 L0 的消息（≥90% 共现）**：`{', '.join(near_all_e)}`\n")
    low_e = [e for e in L0_EVENTS if ec.get(e, 0) < total * 0.8]
    if low_e:
        L.append(f"**v0 L0 里覆盖率<80% 的消息**：")
        for e in low_e:
            L.append(f"- `{e}`：{ec.get(e,0)}/{total}")
        L.append("")

    # §3 新族候选
    L.append("## §3 未命中族的包聚类（新族候选）\n")
    clusters, unassigned = find_new_family_candidates(records, per_ev_packs, KNOWN_FAMILY_MARKERS)
    L.append(f"未命中已知族的包：{len(unassigned)} 个\n")
    L.append(f"候选新族（消息集合 Jaccard≥0.6、≥3 消息、≥2 包共享）：{len(clusters)} 个\n")
    for i, cl in enumerate(clusters[:20]):
        L.append(f"\n### 候选新族 #{i+1}  (markers={cl['size']}, packs={len(cl['packs'])})\n")
        L.append(f"- **markers**: `{', '.join(cl['markers'][:12])}`{'...' if len(cl['markers']) > 12 else ''}")
        L.append(f"- **成员包**: {cl['packs']}")

    # §4 handler 的骨架 vs 实际
    L.append("\n## §4 handlers 全量共现（辅助 cinematics §8 依赖表）\n")
    L.append("| handler 消息 | 覆盖包数 | 出现率 |")
    L.append("|---|---|---|")
    for m, c in hc.most_common(50):
        L.append(f"| `{m}` | {c} | {c*100//total}% |")
    L.append("")

    # §5 潜在坑候选：单包独有 hat / 奇怪消息
    L.append("## §5 单包独有变量 / 消息（可能是题目专属或坑候选）\n")
    uniq_vars = sorted([(v, next(iter(ps))) for v, ps in per_var_packs.items() if len(ps) == 1],
                       key=lambda x: x[1])
    uniq_evs = sorted([(e, next(iter(ps))) for e, ps in per_ev_packs.items() if len(ps) == 1],
                      key=lambda x: x[1])
    L.append(f"单包独有变量：{len(uniq_vars)} 个")
    L.append(f"单包独有消息：{len(uniq_evs)} 个\n")
    L.append("> 在 ≤1 个包里出现，多数为题目专属；若同一包里独有变量/消息很多，该包可能是新族的种子。")
    L.append("")
    # 每包统计
    seed = defaultdict(lambda: {'vars': 0, 'evs': 0})
    for v, pk in uniq_vars:
        seed[pk]['vars'] += 1
    for e, pk in uniq_evs:
        seed[pk]['evs'] += 1
    seed_sorted = sorted(seed.items(), key=lambda x: -(x[1]['vars'] + x[1]['evs']))[:10]
    L.append("| 包 | 独有变量数 | 独有消息数 |")
    L.append("|---|---|---|")
    for pk, st in seed_sorted:
        L.append(f"| `{pk}` | {st['vars']} | {st['evs']} |")

    return '\n'.join(L)


def main():
    records = load_all()
    out = EXTRACT_DIR / 'suggestions.md'
    out.write_text(render(records), encoding='utf-8')
    print(f"[distill] wrote {out}  packs={len(records)}")


if __name__ == '__main__':
    main()
