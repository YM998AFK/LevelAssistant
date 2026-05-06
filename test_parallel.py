# -*- coding: utf-8 -*-
"""
Realistic GUI-like parallel session test.
Mimics what happens when:
  1. Session 1 starts a task
  2. While session 1 is running, switch to session 2 and start another task
  3. Switch back to session 1 while both are running
  4. Wait for both to complete
  5. Verify NO cross-contamination and both completed independently
"""
import sys, os, time, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from app.agent import AgentWorker
from app.config import DEFAULT_MODEL, workspace_dir
from app.logger import setup_task_logging
import uuid

app = QApplication.instance() or QApplication(sys.argv)

# Simulate per-session state (like MainWindow.mode_state)
sessions = {
    1: {"messages": [], "ai_buf": [], "tool_calls": [], "done": False, "err": None, "worker": None},
    2: {"messages": [], "ai_buf": [], "tool_calls": [], "done": False, "err": None, "worker": None},
}
active = [1]   # which session is "active" (shown in UI)

def is_active(idx):
    return active[0] == idx

def start_session(idx: int, task: str, delay_s: float = 0):
    def _start():
        ws = workspace_dir() / f"sim_{idx}_{uuid.uuid4().hex[:4]}"
        ws.mkdir(parents=True, exist_ok=True)
        tlog = setup_task_logging(ws)
        prompt = (
            "You are a concise assistant. "
            "Use at most 2 tool calls, reply in Chinese."
        )
        messages = [{"role": "user", "content": task}]
        sessions[idx]["messages"] = messages

        w = AgentWorker(
            messages=messages, system_prompt=prompt, workspace=ws,
            skill_dir=None, uploaded_files=[], model=DEFAULT_MODEL, task_logger=tlog,
        )
        sessions[idx]["worker"] = w

        # ── Signal routing (mirrors _route_* in MainWindow) ──
        def on_chunk(chunk, i=idx):
            sessions[i]["ai_buf"].append(chunk)
            if is_active(i):
                print(f"  [S{i} live] {chunk[:40].strip()}", flush=True)

        def on_tool(name, params, i=idx):
            sessions[i]["tool_calls"].append(name)
            print(f"[S{i}] tool_start: {name}", flush=True)

        def on_done(i=idx):
            sessions[i]["done"] = True
            # sync final messages back (mirrors _route_done)
            sessions[i]["messages"] = list(sessions[i]["worker"].messages)
            print(f"[S{i}] DONE  msgs={len(sessions[i]['messages'])} "
                  f"tools={sessions[i]['tool_calls']}", flush=True)

        def on_err(msg, i=idx):
            sessions[i]["err"] = msg
            print(f"[S{i}] ERROR: {msg}", flush=True)

        w.text_chunk.connect(on_chunk)
        w.tool_call_start.connect(on_tool)
        w.finished_turn.connect(on_done)
        w.error.connect(on_err)
        w.start()
        print(f"[S{idx}] started: {task[:60]}", flush=True)

    if delay_s > 0:
        QTimer.singleShot(int(delay_s * 1000), _start)
    else:
        _start()

def switch_to(idx: int):
    old = active[0]
    active[0] = idx
    print(f"[UI] switch session {old} → {idx}  "
          f"(S{old} running={sessions[old]['worker'] and sessions[old]['worker'].isRunning()})", flush=True)

start = time.time()

# Step 1: Start session 1 with a tool-heavy task
start_session(1, "用write_file写文件task1.txt内容='TASK1_SECRET'，然后用read_file读回确认，并告诉我文件内容")

# Step 2: After 2s, simulate "switch to session 2 and start another task"
def step2():
    switch_to(2)
    start_session(2, "用run_python计算斐波那契数列前15项并输出")

QTimer.singleShot(2000, step2)

# Step 3: After 5s, switch back to session 1 to "watch it live"
def step3():
    switch_to(1)
    print(f"[UI] Switched back to S1 — buffered {len(sessions[1]['ai_buf'])} chunks so far", flush=True)

QTimer.singleShot(5000, step3)

def check():
    elapsed = time.time() - start
    both_done = sessions[1]["done"] and sessions[2]["done"]
    if both_done or elapsed > 120:
        print("\n===== FINAL RESULTS =====", flush=True)
        for idx in [1, 2]:
            s = sessions[idx]
            status = "DONE" if s["done"] else ("ERROR" if s["err"] else "TIMEOUT")
            text = "".join(s["ai_buf"]).strip()
            print(f"\nSession {idx} [{status}]", flush=True)
            print(f"  tools: {s['tool_calls']}", flush=True)
            print(f"  final msgs in history: {len(s['messages'])}", flush=True)
            print(f"  output snippet: {text[:120]}", flush=True)
            if s["err"]:
                print(f"  ERROR: {s['err']}", flush=True)

        if sessions[1]["done"] and sessions[2]["done"]:
            # Verify no cross-contamination
            s1_text = "".join(sessions[1]["ai_buf"])
            s2_text = "".join(sessions[2]["ai_buf"])
            cross = "TASK1_SECRET" in s2_text or "斐波那契" in s1_text
            print(f"\nCross-contamination: {'YES - BUG!' if cross else 'NO - clean'}", flush=True)
            print("PASS - both sessions completed in parallel", flush=True)
        else:
            pending = [i for i in [1,2] if not sessions[i]["done"]]
            print(f"\nFAIL/TIMEOUT - pending sessions: {pending}", flush=True)

        app.quit()

timer = QTimer()
timer.timeout.connect(check)
timer.start(3000)
sys.exit(app.exec())
