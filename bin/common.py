import json
import os
import subprocess
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parent.parent


def load_env():
    config_dir = FORGE_ROOT / "config"

    with open(config_dir / "settings.json") as f:
        cfg = json.load(f)

    env = {
        "FORGE_TEAM": cfg["team"],
        "FORGE_TEAM_ID": cfg["team_id"],
        "FORGE_MODEL": cfg["model"]["default"],
        "FORGE_LOG_DIR": cfg["log_dir"],
        "FORGE_LOCK_DIR": cfg["lock_dir"],
        "FORGE_WORKTREE_DIR": cfg["worktree_dir"],
        "FORGE_MAX_CONCURRENT": str(cfg["max_concurrent"]),
        "FORGE_LOCK_TIMEOUT_MIN": str(cfg["lock_timeout_min"]),
    }
    for phase, val in cfg.get("budget", {}).items():
        env[f"FORGE_BUDGET_{phase.upper()}"] = str(val)
    for phase, val in cfg.get("max_turns", {}).items():
        env[f"FORGE_MAX_TURNS_{phase.upper()}"] = str(val)
    for phase, val in cfg.get("model", {}).items():
        if phase == "default":
            continue
        env[f"FORGE_MODEL_{phase.upper()}"] = str(val)

    secrets_path = config_dir / "secrets.env"
    if secrets_path.exists():
        with open(secrets_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                k, _, v = line.partition("=")
                env[k] = v.strip('"').strip("'")

    return env


def detect_default_branch(repo_path: str) -> str:
    ret = subprocess.run(
        ["git", "-C", repo_path, "symbolic-ref", "refs/remotes/origin/HEAD"],
        capture_output=True, text=True,
    )
    if ret.returncode != 0:
        subprocess.run(
            ["git", "-C", repo_path, "remote", "set-head", "origin", "--auto"],
            capture_output=True,
        )
        ret = subprocess.run(
            ["git", "-C", repo_path, "symbolic-ref", "refs/remotes/origin/HEAD"],
            capture_output=True, text=True,
        )
    if ret.returncode == 0:
        return ret.stdout.strip().split("/")[-1]
    return "main"


def get_api_key(env=None):
    if env:
        key = env.get("LINEAR_API_KEY")
        if key:
            return key
    return os.environ.get("LINEAR_API_KEY", "")


def parse_labels(label_nodes) -> list[str]:
    labels = []
    for label in label_nodes:
        parent = label.get("parent")
        name = label["name"]
        labels.append(f"{parent['name']}:{name}" if parent else name)
    return labels
