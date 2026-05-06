"""分析 agent transcript，看关卡生成过程中时间/token/工具调用分布。

用法:
  python scripts/_analyze_level_gen_transcript.py <uuid>
  python scripts/_analyze_level_gen_transcript.py --list

功能:
  1. 列出 parent transcripts（按修改时间倒序）
  2. 给定 uuid，扫 jsonl：
     - 首/末消息时间戳 -> 端到端耗时
     - role 分布（user/assistant/tool/...）
     - 按 tool 名统计调用次数 + 累计参数 bytes + 累计结果 bytes
     - 各轮次之间的时间间隔（找出"等很久没动静"的位置）
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from glob import glob
from pathlib import Path

TRANSCRIPT_ROOT = Path(
    r"C:\Users\Hetao\.cursor\projects\c-Users-Hetao-Desktop\agent-transcripts"
)


def list_parents(limit: int = 20) -> None:
    items = []
    for path in glob(str(TRANSCRIPT_ROOT / "*" / "*.jsonl")):
        p = Path(path)
        if p.parent.name == "subagents":
            continue
        if p.parent.parent != TRANSCRIPT_ROOT:
            continue
        if p.stem != p.parent.name:
            continue
        items.append((p.stat().st_mtime, p))
    items.sort(reverse=True)
    for mt, p in items[:limit]:
        size_kb = p.stat().st_size // 1024
        print(
            f"{datetime.fromtimestamp(mt).strftime('%Y-%m-%d %H:%M:%S')}  "
            f"{size_kb:>5} KB  {p.parent.name}"
        )


def _iter_events(path: Path):
    with path.open(encoding="utf-8") as fh:
        for i, raw in enumerate(fh):
            raw = raw.strip()
            if not raw:
                continue
            try:
                yield i, json.loads(raw)
            except Exception as exc:
                print(f"[warn] line {i} parse error: {exc}")


def _extract_ts(evt: dict):
    msg = evt.get("message") or {}
    for key in ("createdAt", "timestamp", "ts", "time"):
        v = msg.get(key) or evt.get(key)
        if isinstance(v, (int, float)):
            if v > 1e12:
                return v / 1000.0
            return float(v)
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
            except Exception:
                pass
    return None


def _extract_tool_calls(evt: dict):
    """Return list of dicts: {name, args_len, result_len}."""
    result = []
    msg = evt.get("message") or {}
    content = msg.get("content")
    if isinstance(content, list):
        for blk in content:
            if not isinstance(blk, dict):
                continue
            t = blk.get("type")
            if t in ("tool_use", "toolUse", "function_call"):
                name = blk.get("name") or blk.get("tool") or blk.get("functionName") or "?"
                inp = blk.get("input") or blk.get("arguments") or {}
                try:
                    inp_len = len(json.dumps(inp, ensure_ascii=False))
                except Exception:
                    inp_len = -1
                result.append({"kind": "call", "name": name, "bytes": inp_len})
            elif t in ("tool_result", "toolResult", "function_call_output"):
                name = blk.get("name") or blk.get("tool") or "?"
                body = blk.get("content") or blk.get("output") or blk.get("result")
                if isinstance(body, (list, dict)):
                    try:
                        b_len = len(json.dumps(body, ensure_ascii=False))
                    except Exception:
                        b_len = -1
                else:
                    b_len = len(str(body) if body is not None else "")
                result.append({"kind": "result", "name": name, "bytes": b_len})
    return result


def _extract_text(evt: dict) -> int:
    """Return text bytes from assistant/user message (not tool calls)."""
    msg = evt.get("message") or {}
    content = msg.get("content")
    total = 0
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        for blk in content:
            if not isinstance(blk, dict):
                continue
            if blk.get("type") in ("text", "output_text", "input_text"):
                total += len(blk.get("text") or "")
    return total


def analyze(uuid: str, include_subagents: bool = True) -> None:
    path = TRANSCRIPT_ROOT / uuid / f"{uuid}.jsonl"
    if not path.exists():
        print(f"transcript not found: {path}")
        sys.exit(1)

    events = list(_iter_events(path))
    print(f"== {uuid} ==")
    print(f"events: {len(events)}")

    role_counts: dict[str, int] = defaultdict(int)
    tool_call_counts: dict[str, int] = defaultdict(int)
    tool_call_bytes: dict[str, int] = defaultdict(int)
    tool_result_bytes: dict[str, int] = defaultdict(int)
    timestamps: list[tuple[int, float, str]] = []
    user_text_bytes = 0
    assistant_text_bytes = 0

    prev_ts = None
    biggest_gaps: list[tuple[float, int, str]] = []

    for i, evt in events:
        role = evt.get("role") or (evt.get("message") or {}).get("role") or "unknown"
        role_counts[role] += 1

        tb = _extract_text(evt)
        if role == "user":
            user_text_bytes += tb
        elif role == "assistant":
            assistant_text_bytes += tb

        ts = _extract_ts(evt)
        if ts is not None:
            timestamps.append((i, ts, role))
            if prev_ts is not None:
                gap = ts - prev_ts
                if gap > 0:
                    biggest_gaps.append((gap, i, role))
            prev_ts = ts

        for call in _extract_tool_calls(evt):
            if call["kind"] == "call":
                tool_call_counts[call["name"]] += 1
                tool_call_bytes[call["name"]] += max(0, call["bytes"])
            else:
                tool_result_bytes[call["name"]] += max(0, call["bytes"])

    print("\n-- role distribution --")
    for k, v in sorted(role_counts.items(), key=lambda x: -x[1]):
        print(f"  {k:20s} {v}")

    if timestamps:
        first = timestamps[0][1]
        last = timestamps[-1][1]
        dur_s = last - first
        print(
            f"\n-- wall-clock --"
            f"\n  first event: {datetime.fromtimestamp(first).strftime('%Y-%m-%d %H:%M:%S')}"
            f"\n  last  event: {datetime.fromtimestamp(last).strftime('%Y-%m-%d %H:%M:%S')}"
            f"\n  duration   : {dur_s/60:.1f} min ({dur_s:.0f} s)"
        )

        biggest_gaps.sort(reverse=True)
        print("\n-- top-10 time gaps between consecutive events --")
        for gap, i, role in biggest_gaps[:10]:
            print(f"  +{gap:>7.1f}s  line {i:>4d}  role={role}")
    else:
        print("\n(no timestamps found in events; cannot compute duration)")

    print(
        f"\n-- conversational bytes --"
        f"\n  user  text: {user_text_bytes/1024:>7.1f} KB  (≈ {user_text_bytes} chars)"
        f"\n  asst  text: {assistant_text_bytes/1024:>7.1f} KB  (≈ {assistant_text_bytes} chars)"
    )

    if tool_call_counts:
        print("\n-- tool calls (top 20 by count) --")
        for name, n in sorted(tool_call_counts.items(), key=lambda x: -x[1])[:20]:
            in_kb = tool_call_bytes.get(name, 0) / 1024
            out_kb = tool_result_bytes.get(name, 0) / 1024
            print(
                f"  {name:30s} calls={n:>4d}  in={in_kb:>8.1f}KB  out={out_kb:>8.1f}KB  "
                f"avg_in={in_kb*1024/max(1,n):>7.0f}B"
            )

        total_in = sum(tool_call_bytes.values()) / 1024
        total_calls = sum(tool_call_counts.values())
        print(f"\n  TOTAL calls={total_calls}  arg-bytes={total_in:.1f}KB")

    if include_subagents:
        sub_dir = TRANSCRIPT_ROOT / uuid / "subagents"
        sub_files = sorted(glob(str(sub_dir / "*.jsonl")))
        if sub_files:
            print(f"\n-- subagents ({len(sub_files)}) --")
            for sf in sub_files:
                spath = Path(sf)
                events_sub = list(_iter_events(spath))
                sub_tools: dict[str, int] = defaultdict(int)
                sub_user = 0
                sub_asst = 0
                for _, evt in events_sub:
                    role = evt.get("role") or (evt.get("message") or {}).get("role")
                    tb = _extract_text(evt)
                    if role == "user":
                        sub_user += tb
                    elif role == "assistant":
                        sub_asst += tb
                    for c in _extract_tool_calls(evt):
                        if c["kind"] == "call":
                            sub_tools[c["name"]] += 1
                top_tools = ", ".join(
                    f"{n}×{v}" for n, v in sorted(sub_tools.items(), key=lambda x: -x[1])[:5]
                )
                print(
                    f"  {spath.stem[:8]}  evts={len(events_sub):>3d}  "
                    f"user={sub_user//1024}KB  asst={sub_asst//1024}KB  "
                    f"tools=[{top_tools}]"
                )


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("--list", "-l"):
        list_parents()
        return
    analyze(sys.argv[1])


if __name__ == "__main__":
    main()
