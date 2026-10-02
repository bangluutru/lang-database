"""End-to-end test of the Claude<->Luna mailbox in a throw-away git repo (no real data touched)."""
import json, os, shutil, subprocess, sys
from pathlib import Path
import pytest

REAL = Path(__file__).resolve().parent.parent
MB = REAL / "scripts/handoff/mailbox.py"


@pytest.fixture()
def repo(tmp_path):
    r = tmp_path / "repo"
    (r / "scripts/phase1_4/handoff").mkdir(parents=True)
    shutil.copy(REAL / "scripts/phase1_4/handoff/validate_decisions.py", r / "scripts/phase1_4/handoff/")
    pk = r / "data/phase1_4/handoff/packets"; pk.mkdir(parents=True)
    for n, ids in (("T1_001", ["c-a", "c-b"]), ("T1_002", ["c-c"]), ("T2_001", ["c-z"])):
        (pk / f"{n}.jsonl").write_text("".join(json.dumps({"id": i, "en": "x", "pos": "noun"}) + "\n" for i in ids))
    subprocess.run(["git", "init", "-q"], cwd=r, check=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t", "add", "-A"], cwd=r, check=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-qm", "init"], cwd=r, check=True)
    return r


def mb(repo, *args):
    env = dict(os.environ, HANDOFF_REPO=str(repo), GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="a@b", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="a@b")
    return subprocess.run([sys.executable, str(MB), *args], cwd=repo, capture_output=True, text=True, env=env)


def decision(i, verdict="ACCEPT"):
    d = {"task": "T1", "id": i, "reviewer": "gpt-6-luna", "verdict": verdict, "en_ja": "OK", "en_vi": "OK", "ja_vi": "OK",
         "naturalness": "NATURAL", "confidence": "HIGH", "revision": None, "note": "Exact and idiomatic in all three languages."}
    return d


def write_out(repo, name, ids):
    out = repo / "data/phase1_4/handoff/decisions"; out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.jsonl").write_text("".join(json.dumps(decision(i)) + "\n" for i in ids))


def test_full_cycle_with_autochain_rework_and_guard(repo):
    assert "first task: T1_001" in mb(repo, "plan").stdout
    # Luna picks up
    r = mb(repo, "luna-next")
    assert json.loads(r.stdout)["task_id"] == "T1_001"
    assert mb(repo, "luna-next").stdout.strip() == "NO_TASK"                     # nothing else is active
    # premature / malformed submission is refused
    assert mb(repo, "luna-done", "T1_001").returncode != 0
    (repo / "data/phase1_4/handoff/decisions").mkdir(parents=True, exist_ok=True)
    (repo / "data/phase1_4/handoff/decisions/T1_001.jsonl").write_text(json.dumps(decision("c-a")) + "\n")   # incomplete
    assert mb(repo, "luna-done", "T1_001").returncode != 0
    write_out(repo, "T1_001", ["c-a", "c-b"])
    assert mb(repo, "luna-done", "T1_001").returncode == 0
    assert (repo / "handoff/mailbox/to_claude/DONE-T1_001.json").exists()
    # Claude asks for rework once -> task is re-assigned with feedback
    assert mb(repo, "review", "T1_001", "--rework", "c-b: vi too broad").returncode == 0
    t = json.loads((repo / "handoff/mailbox/to_luna/TASK-T1_001.json").read_text())
    assert t["attempt"] == 2 and "too broad" in t["rework_feedback"]
    assert json.loads(mb(repo, "luna-next").stdout)["task_id"] == "T1_001"
    write_out(repo, "T1_001", ["c-a", "c-b"])
    assert mb(repo, "luna-done", "T1_001").returncode == 0
    # Luna sneaks in a forbidden edit -> commit is refused
    (repo / "scripts/phase1_4/handoff/evil.py").write_text("x=1")
    assert mb(repo, "guard").returncode == 1
    assert mb(repo, "review", "T1_001", "--approve", "--commit").returncode == 1
    (repo / "scripts/phase1_4/handoff/evil.py").unlink()
    r = mb(repo, "review", "T1_001", "--approve", "--commit")
    assert r.returncode == 0 and "next: T1_002" in r.stdout, r.stdout + r.stderr
    log = subprocess.run(["git", "log", "--oneline"], cwd=repo, capture_output=True, text=True).stdout
    assert "Luna decisions T1_001" in log
    # chain continues to the end
    assert json.loads(mb(repo, "luna-next").stdout)["task_id"] == "T1_002"
    write_out(repo, "T1_002", ["c-c"])
    assert mb(repo, "luna-done", "T1_002").returncode == 0
    assert "next: T2_001" in mb(repo, "review", "T1_002", "--approve", "--commit").stdout


def test_escalates_after_three_rework_attempts(repo):
    mb(repo, "plan")
    for _ in range(3):
        mb(repo, "luna-next")
        write_out(repo, "T1_001", ["c-a", "c-b"])
        mb(repo, "luna-done", "T1_001")
        mb(repo, "review", "T1_001", "--rework", "still wrong")
    st = json.loads((repo / "handoff/state.json").read_text())
    assert st["tasks"]["T1_001"]["state"] == "ESCALATED"
