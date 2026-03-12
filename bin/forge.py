#!/usr/bin/env python3
"""forge メインエントリポイント: Linear ポーリング → Issue 振り分け → バックグラウンド実行。"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORGE_ROOT / "bin"))

from poll import load_env, poll

def load_repos() -> dict[str, str]:
    repos = {}
    conf = FORGE_ROOT / "config" / "repos.conf"
    with open(conf) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            k, _, v = line.partition("=")
            if k and v:
                repos[k.strip()] = v.strip()
    return repos

def resolve_repo(labels: list[str], repos: dict[str, str]) -> str | None:
    for label in labels:
        if label.startswith("repo:"):
            key = label.removeprefix("repo:")
            return repos.get(key)
    return None

def count_locks(lock_dir: Path) -> int:
    return len(list(lock_dir.glob("*.lock")))

def clean_stale_locks(lock_dir: Path, timeout_min: int):
    now = time.time()
    for lock in lock_dir.glob("*.lock"):
        age_min = (now - lock.stat().st_mtime) / 60
        if age_min > timeout_min:
            lock.unlink(missing_ok=True)

def log(msg: str):
    print(f"[{datetime.now():%H:%M:%S}] {msg}")

def main():
    env = load_env()
    log_dir = Path(env["FORGE_LOG_DIR"])
    lock_dir = Path(env["FORGE_LOCK_DIR"])
    max_concurrent = int(env["FORGE_MAX_CONCURRENT"])
    lock_timeout = int(env["FORGE_LOCK_TIMEOUT_MIN"])

    log_dir.mkdir(parents=True, exist_ok=True)
    lock_dir.mkdir(parents=True, exist_ok=True)

    repos = load_repos()

    clean_stale_locks(lock_dir, lock_timeout)

    log("=== forge started ===")

    log("Polling Planning issues...")
    planning_issues = poll("Planning")

    log("Polling Implementing issues...")
    implementing_issues = poll("Implementing")

    processes: list[subprocess.Popen] = []

    for phase, issues in [("planning", planning_issues), ("implementing", implementing_issues)]:
        if not issues:
            continue
        log(f"{len(issues)} {phase} issue(s) found")

        for issue in issues:
            issue_id = issue["id"]
            identifier = issue["identifier"]
            title = issue["title"]
            labels = issue.get("labels", [])

            lock_file = lock_dir / f"{issue_id}.lock"
            if lock_file.exists():
                log(f"  Skip {identifier} (locked): {title}")
                continue

            if count_locks(lock_dir) >= max_concurrent:
                log(f"  Skip {identifier} (max concurrent): {title}")
                break

            repo_path = resolve_repo(labels, repos)
            if not repo_path:
                log(f"  Skip {identifier} (no repo label): {title}")
                continue
            if not Path(repo_path).is_dir():
                log(f"  Skip {identifier} (repo not found: {repo_path}): {title}")
                continue

            log(f"  Start {identifier} ({phase}): {title}")
            lock_file.write_text(identifier)

            p = subprocess.Popen(
                [sys.executable, str(FORGE_ROOT / "bin" / "run_claude.py"), phase, issue_id, identifier, repo_path],
            )
            processes.append(p)

    for p in processes:
        p.wait()

    log("=== forge finished ===")

if __name__ == "__main__":
    main()
