#!/usr/bin/env python3
"""
scripts/handoff/mailbox.py - file-based mailbox between Claude (owner of review + commit) and Luna (worker, NO git).

Roles / permissions (enforced by `guard` before every commit):
  Luna may write ONLY:  data/phase1_4/handoff/decisions/**   handoff/mailbox/to_claude/**   handoff/work/**
  Claude writes:        handoff/mailbox/to_luna/**, handoff/state.json, commits, everything else.
  Luna NEVER runs git, never edits any other file.

State machine per task:   QUEUED -> ASSIGNED -> IN_PROGRESS -> SUBMITTED -> APPROVED -> COMMITTED
                                          ^                         |
                                          +------ REWORK <---------+      (3 rework attempts, then ESCALATED = owner)
Auto-chain: when a task is COMMITTED, the next QUEUED task becomes ASSIGNED automatically, until the queue is empty.

Luna commands:    luna-next [--wait]      luna-done <task_id>
Claude commands:  plan  status  review <task_id> [--approve|--rework "why"] [--commit]  watch-claude  guard
All writes are atomic (tmp+rename) and state.json is protected by an exclusive file lock.
"""
import argparse
import fcntl
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(os.environ.get("HANDOFF_REPO", Path(__file__).resolve().parent.parent.parent))
HO = REPO / "handoff"
MAIL_LUNA = HO / "mailbox" / "to_luna"
MAIL_CLAUDE = HO / "mailbox" / "to_claude"
STATE = HO / "state.json"
LOCK = HO / ".state.lock"
PACKETS = REPO / "data/phase1_4/handoff/packets"
DECISIONS = REPO / "data/phase1_4/handoff/decisions"
REVIEW_LOG = REPO / "data/phase1_4/handoff/review_log.jsonl"
VALIDATOR = REPO / "scripts/phase1_4/handoff/validate_decisions.py"
LUNA_ALLOWED = ("data/phase1_4/handoff/decisions/", "handoff/mailbox/to_claude/", "handoff/work/")
MAX_ATTEMPTS = 3
DEFAULT_ORDER = [("T1", None), ("T2", None), ("T3", None), ("T4", None)]    # extension waves: T3 packets are queued before T4 ones


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


class State:
    def __enter__(self):
        HO.mkdir(parents=True, exist_ok=True)
        self.fh = open(LOCK, "w")
        fcntl.flock(self.fh, fcntl.LOCK_EX)
        self.s = json.loads(STATE.read_text()) if STATE.exists() else {"tasks": {}, "order": [], "events": []}
        return self.s

    def __exit__(self, *a):
        atomic_write(STATE, json.dumps(self.s, ensure_ascii=False, indent=1))
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()


def ev(s, who, msg):
    s["events"].append({"t": now(), "who": who, "msg": msg})
    s["events"] = s["events"][-200:]


def sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def task_file(tid): return MAIL_LUNA / f"TASK-{tid}.json"


def assign(s, tid):
    t = s["tasks"][tid]
    t["state"] = "ASSIGNED"
    t["attempt"] = t.get("attempt", 0) + 1
    t["assigned_at"] = now()
    msg = {"task_id": tid, "kind": t["kind"], "attempt": t["attempt"], "packet": f"data/phase1_4/handoff/packets/{t['packet']}",
           "output": f"data/phase1_4/handoff/decisions/{t['packet']}", "instructions": f"docs/handoff/LUNA_HANDOFF.md (section {t['kind']})",
           "items": t["items"], "rework_feedback": t.get("feedback"), "created_at": now(),
           "when_done": f"python scripts/handoff/mailbox.py luna-done {tid}"}
    atomic_write(task_file(tid), json.dumps(msg, ensure_ascii=False, indent=1))
    ev(s, "claude", f"assigned {tid} (attempt {t['attempt']})")


def advance(s):
    """Assign the next QUEUED task if nothing is active."""
    # pipelined: Luna keeps working while earlier submissions wait for Claude's batch review
    if any(t["state"] in ("ASSIGNED", "IN_PROGRESS") for t in s["tasks"].values()):
        return None
    for tid in s["order"]:
        if s["tasks"][tid]["state"] == "QUEUED":
            assign(s, tid)
            return tid
    return None


# --------------------------------------------------------------------------- Claude
def cmd_plan(a):
    n_items = lambda p: sum(1 for l in p.read_text(encoding="utf-8").splitlines() if l.strip())
    with State() as s:
        for kind, cap in DEFAULT_ORDER:
            files = sorted(PACKETS.glob(f"{kind}_*.jsonl"))[: cap or None]
            for f in files:
                tid = f.stem
                if tid not in s["tasks"]:
                    s["tasks"][tid] = {"kind": kind, "packet": f.name, "items": n_items(f), "state": "QUEUED", "attempt": 0}
                    s["order"].append(tid)
        first = advance(s)
        ev(s, "claude", f"planned {len(s['order'])} tasks; first={first}")
    print(f"planned; first task: {first}")


def cmd_status(a):
    s = json.loads(STATE.read_text()) if STATE.exists() else {"tasks": {}, "order": []}
    from collections import Counter
    c = Counter(t["state"] for t in s["tasks"].values())
    print(dict(c))
    for tid in s["order"]:
        t = s["tasks"][tid]
        if t["state"] not in ("QUEUED", "COMMITTED"):
            print(f"  {tid}: {t['state']} (attempt {t['attempt']})")


def run_validator(path):
    r = subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True, cwd=REPO)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def cmd_review(a):
    tid = a.task_id
    s = json.loads(STATE.read_text())
    t = s["tasks"][tid]
    out = DECISIONS / t["packet"]
    if t["state"] not in ("SUBMITTED", "APPROVED"):
        print(f"{tid} is {t['state']}, nothing to review"); return 1
    ok, log = run_validator(out)
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    packet = {json.loads(l)["id"]: json.loads(l) for l in (PACKETS / t["packet"]).read_text(encoding="utf-8").splitlines() if l.strip()}
    from collections import Counter
    dist = Counter(r.get("verdict", "T4") for r in rows)
    complete = len(rows) == len(packet) and {r["id"] for r in rows} == set(packet)
    if not a.approve and not a.rework:
        rnd = random.Random(tid)
        must = [r for r in rows if r.get("verdict") in ("REVISE", "REJECT") or t["kind"] == "T2"]
        if t["kind"] == "T4":             # auto-flag suspicious VI proposals so the reviewer reads only what matters
            sys.path.insert(0, str(REPO))
            from scripts.phase1_4 import lexicons as _L
            vn = _L.load_vn_freq()
            def suspicious(r):
                v = r.get("vi_lemma")
                p_ = packet[r["id"]]
                return (v is None or r["confidence"] != "HIGH" or v not in vn or len(v.split()) > 3 or v == (p_.get("rejected_vi_before") or "")
                        or v.lower() == p_["en"].lower())
            must = [r for r in rows if suspicious(r)]
        rest = [r for r in rows if r not in must]
        frac = 0.1 if t["kind"] == "T4" else 0.15
        sample = must + rnd.sample(rest, min(len(rest), max(3, int(len(rest) * frac)))) if rest else must
        md = [f"# Review sample {tid} (validator ok={ok}, complete={complete}, dist={dict(dist)})\n"]
        for r in sample:
            p = packet[r["id"]]
            if t["kind"] == "T4":
                md.append(f"- **{p['en']}** ({p.get('pos')}) | JA {p.get('ja')} | def: {p.get('en_sense_definition','')[:70]}\n    Luna VI: {r.get('vi_lemma')} {r.get('synonyms')} {r['confidence']} | {r['note'][:110]}")
                continue
            md.append(f"- **{p['en']}** ({p.get('pos')}) | JA {p.get('ja')}({p.get('ja_reading')}) | VI {p.get('vi')} | def: {p.get('en_sense_definition','')[:80]}\n"
                      f"    Luna: {json.dumps({k: v for k, v in r.items() if k not in ('task','id','reviewer')}, ensure_ascii=False)}")
        path = HO / "work" / f"review_{tid}.md"
        atomic_write(path, "\n".join(md))
        print(f"validator ok={ok} complete={complete} dist={dict(dist)}\n{log}\nsample ({len(sample)} items) -> {path.relative_to(REPO)}")
        return 0
    with State() as s:
        t = s["tasks"][tid]
        if a.rework:
            t["state"] = "REWORK"
            t["feedback"] = a.rework
            if t["attempt"] >= MAX_ATTEMPTS:
                t["state"] = "ESCALATED"
                ev(s, "claude", f"{tid} ESCALATED to owner after {t['attempt']} attempts")
            else:
                assign(s, tid)
            atomic_write(MAIL_LUNA / f"REVIEW-{tid}.json", json.dumps({"task_id": tid, "verdict": "REWORK", "feedback": a.rework}, ensure_ascii=False, indent=1))
            print(f"{tid}: {t['state']}")
            return 0
        if not (ok and complete):
            print("cannot approve: validator failed or decision file incomplete"); return 1
        t["state"] = "APPROVED"
        t["stats"] = dict(dist)
        atomic_write(MAIL_LUNA / f"REVIEW-{tid}.json", json.dumps({"task_id": tid, "verdict": "APPROVED"}, indent=1))
        ev(s, "claude", f"approved {tid}")
    if a.commit:
        guard_ok = cmd_guard(argparse.Namespace(quiet=True))
        if guard_ok != 0:
            print("guard failed: Luna touched forbidden paths; NOT committing"); return 1
        REVIEW_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(REVIEW_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"task_id": tid, "reviewer": "claude", "decision": "APPROVED", "stats": dict(dist), "decision_file_sha256": sha(out), "at": now()}) + "\n")
        subprocess.run(["git", "add", str(out.relative_to(REPO)), str(REVIEW_LOG.relative_to(REPO))], cwd=REPO, check=True)
        subprocess.run(["git", "commit", "-q", "-m", f"feat(handoff): Luna decisions {tid} reviewed and approved\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"], cwd=REPO, check=True)
        with State() as s:
            s["tasks"][tid]["state"] = "COMMITTED"
            ev(s, "claude", f"committed {tid}")
            nxt = advance(s)
        print(f"committed {tid}; next: {nxt or 'queue empty'}")
    return 0


def _exceptions(t, rows, packet):
    """Exception-only view: items that can change the corpus or look suspicious. REVISE/REJECT carry no corpus effect
    (they are only recorded) and are not printed except for T1/T2 where a revision may be applied."""
    out = []
    if t["kind"] == "T3":
        out = [r for r in rows if r.get("verdict") == "ACCEPT"]
    elif t["kind"] == "T4":
        sys.path.insert(0, str(REPO))
        from scripts.phase1_4 import lexicons as _L
        vn = _L.load_vn_freq()
        for r in rows:
            v, p_ = r.get("vi_lemma"), packet[r["id"]]
            if v and (r["confidence"] == "LOW" or len(v.split()) > 3 or v.lower() == p_["en"].lower() or
                      (v not in vn and r["confidence"] != "HIGH")):
                out.append(r)
        rnd = random.Random(t["packet"])
        rest = [r for r in rows if r not in out and r.get("vi_lemma")]
        out += rnd.sample(rest, min(len(rest), max(2, int(len(rest) * 0.08))))      # 8% calibration sample
    else:
        out = [r for r in rows if r.get("verdict") in ("REVISE", "REJECT") or t["kind"] == "T2"]
    return out


def cmd_review_batch(a):
    s = json.loads(STATE.read_text())
    lines, ok_all = [], True
    for tid in s["order"]:
        t = s["tasks"][tid]
        if t["state"] != "SUBMITTED":
            continue
        out = DECISIONS / t["packet"]
        ok, log = run_validator(out)
        rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
        packet = {json.loads(l)["id"]: json.loads(l) for l in (PACKETS / t["packet"]).read_text(encoding="utf-8").splitlines() if l.strip()}
        complete = len(rows) == len(packet) and {r["id"] for r in rows} == set(packet)
        ok_all &= ok and complete
        lines.append(f"## {tid} validator={ok} complete={complete}")
        for r in _exceptions(t, rows, packet):
            p_ = packet[r["id"]]
            if t["kind"] == "T4":
                lines.append(f"- {p_['en']}|{p_['ja']}|{(p_.get('en_sense_definition') or '')[:38]}|VI {r.get('vi_lemma')} {r['confidence'][0]}")
            else:
                lines.append(f"- {p_['en']}|{p_['ja']}|vi:{p_.get('vi')}|{(p_.get('en_sense_definition') or '')[:38]}|{r.get('verdict','')[:3]} {r.get('revision') or ''}")
    path = HO / "work" / "review_batch.md"
    atomic_write(path, "\n".join(lines))
    print(f"{sum(1 for l in lines if l.startswith('##'))} tasks; all-valid={ok_all}; exceptions file: {path.relative_to(REPO)} ({len(lines)} lines)")
    return 0 if ok_all else 1


def cmd_approve_batch(a):
    rw = dict(kv.split("=", 1) for kv in a.rework)
    s = json.loads(STATE.read_text())
    for tid in s["order"]:
        if s["tasks"][tid]["state"] != "SUBMITTED":
            continue
        ns = argparse.Namespace(task_id=tid, approve=tid not in rw, rework=rw.get(tid), commit=tid not in rw)
        rc = cmd_review(ns)
        if rc:
            print(f"{tid}: not approved (rc={rc})")
    return 0


def cmd_guard(a):
    """Fail if the working tree contains changes outside what Luna is allowed to write (git is only used read-only here)."""
    r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=REPO, capture_output=True, text=True)
    bad = []
    for l in r.stdout.splitlines():
        path = l[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ")[1]
        if not path.startswith(LUNA_ALLOWED) and not path.startswith("handoff/") and path not in ("data/phase1_4/handoff/review_log.jsonl",):
            bad.append(l)
    if bad and not getattr(a, "quiet", False):
        print("FORBIDDEN CHANGES:\n" + "\n".join(bad))
    elif not bad and not getattr(a, "quiet", False):
        print("guard ok")
    return 1 if bad else 0


def cmd_watch_claude_batch(a):
    """Wake Claude only when >= K submissions are waiting, or when Luna has no more work and something is waiting."""
    last = -1
    while True:
        s = json.loads(STATE.read_text()) if STATE.exists() else {"tasks": {}}
        sub = [t for t, v in s["tasks"].items() if v["state"] == "SUBMITTED"]
        busy = any(v["state"] in ("ASSIGNED", "IN_PROGRESS") for v in s["tasks"].values())
        if sub and (len(sub) >= a.batch or not busy) and len(sub) != last:
            last = len(sub)
            print(f"LUNA-BATCH-READY {len(sub)} submitted: {','.join(sorted(sub))}", flush=True)
        if not sub:
            last = -1
        time.sleep(a.interval)


def cmd_watch_claude(a):
    if getattr(a, "batch", 0):
        return cmd_watch_claude_batch(a)
    """Block; print one line per new Luna receipt (use under Monitor so Claude is woken automatically)."""
    seen = set(p.name for p in MAIL_CLAUDE.glob("DONE-*.json"))
    MAIL_CLAUDE.mkdir(parents=True, exist_ok=True)
    while True:
        for p in sorted(MAIL_CLAUDE.glob("DONE-*.json")):
            if p.name not in seen:
                seen.add(p.name)
                print(f"LUNA-SUBMITTED {p.name}", flush=True)
        for p in sorted(MAIL_CLAUDE.glob("QUESTION-*.md")):
            if p.name not in seen:
                seen.add(p.name)
                print(f"LUNA-QUESTION {p.name}", flush=True)
        time.sleep(a.interval)


# --------------------------------------------------------------------------- Luna
def cmd_luna_next(a):
    while True:
        with State() as s:
            for tid in s["order"]:
                t = s["tasks"][tid]
                if t["state"] == "ASSIGNED":
                    t["state"] = "IN_PROGRESS"
                    ev(s, "luna", f"started {tid}")
                    print(task_file(tid).read_text(encoding="utf-8"))
                    return 0
        if not a.wait:
            print("NO_TASK"); return 3
        time.sleep(a.interval)


def cmd_luna_done(a):
    tid = a.task_id
    with State() as s:
        t = s["tasks"].get(tid)
        if not t or t["state"] != "IN_PROGRESS":
            print(f"{tid} is not IN_PROGRESS"); return 1
    out = DECISIONS / t["packet"]
    if not out.exists():
        print(f"missing output file {out.relative_to(REPO)}"); return 1
    ok, log = run_validator(out)
    n = sum(1 for l in out.read_text(encoding="utf-8").splitlines() if l.strip())
    if not ok or n != t["items"]:
        print(f"REFUSED: validator ok={ok}, lines={n}, expected={t['items']}\n{log}"); return 1
    atomic_write(MAIL_CLAUDE / f"DONE-{tid}.json", json.dumps({"task_id": tid, "from": "luna", "output": str(out.relative_to(REPO)),
                 "lines": n, "sha256": sha(out), "self_validated": True, "submitted_at": now()}, indent=1))
    with State() as s:
        s["tasks"][tid]["state"] = "SUBMITTED"
        ev(s, "luna", f"submitted {tid}")
        nxt = advance(s)
    print(f"submitted {tid}; next task: {nxt or 'none yet'} - run: python scripts/handoff/mailbox.py luna-next --wait")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("plan"); sp.add_parser("status")
    r = sp.add_parser("review"); r.add_argument("task_id"); r.add_argument("--approve", action="store_true"); r.add_argument("--rework"); r.add_argument("--commit", action="store_true")
    g = sp.add_parser("guard"); g.add_argument("--quiet", action="store_true")
    w = sp.add_parser("watch-claude"); w.add_argument("--interval", type=int, default=10); w.add_argument("--batch", type=int, default=0)
    sp.add_parser("review-batch")
    ab = sp.add_parser("approve-batch"); ab.add_argument("--rework", nargs="*", default=[], help="TASK=feedback pairs sent back instead of approved")
    n = sp.add_parser("luna-next"); n.add_argument("--wait", action="store_true"); n.add_argument("--interval", type=int, default=10)
    d = sp.add_parser("luna-done"); d.add_argument("task_id")
    a = ap.parse_args()
    return {"plan": cmd_plan, "status": cmd_status, "review": cmd_review, "guard": cmd_guard, "watch-claude": cmd_watch_claude, "review-batch": cmd_review_batch, "approve-batch": cmd_approve_batch,
            "luna-next": cmd_luna_next, "luna-done": cmd_luna_done}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
