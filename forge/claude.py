import json
import os
import subprocess
from pathlib import Path

from .config import FORGE_ROOT, load_config
from .git import detect_default_branch, diff_stat
from .linear import fetch_issue_detail, fetch_sub_issues


def setup_sandbox(work_dir: Path, *, log_dir: Path | None = None,
                  extra_write_paths: list[str] | None = None):
    user_config = load_config()
    settings = user_config.get("claude", {})

    sandbox_settings = settings.get("sandbox")
    if sandbox_settings:
        sandbox_settings.setdefault("filesystem", {})
        fs = sandbox_settings["filesystem"]
        if log_dir is not None:
            fs.setdefault("allowWrite", [])
            path_str = "/" + str(log_dir)
            if path_str not in fs["allowWrite"]:
                fs["allowWrite"].append(path_str)

        if extra_write_paths:
            fs.setdefault("allowWrite", [])
            for p in extra_write_paths:
                path_str = "/" + str(p) + "/"
                if path_str not in fs["allowWrite"]:
                    fs["allowWrite"].append(path_str)

    claude_dir = work_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)
    settings_file = claude_dir / "settings.local.json"
    settings_file.write_text(json.dumps(settings, indent=2))


def run(prompt: str, work_dir: Path, *,
        model: str, max_turns: str, budget: str = "1.00",
        allowed_tools: list[str] | None = None,
        disallowed_tools: list[str] | None = None,
        log_file: Path | None = None,
        capture_output: bool = False,
        allow_write: list[str] | None = None):
    setup_sandbox(work_dir,
                  log_dir=log_file.parent if log_file else None,
                  extra_write_paths=allow_write)

    # run_env = {**os.environ}
    # run_env.pop("CLAUDECODE", None)

    cmd = [
        "claude", "--print",
        "--no-session-persistence",
        "--max-budget-usd", budget,
        "--max-turns", max_turns,
        "--model", model,
        "-p", prompt,
        "--output-format", "json",
    ]
    if allowed_tools:
        cmd.extend(["--allowedTools", ",".join(allowed_tools)])
    if disallowed_tools:
        cmd.extend(["--disallowedTools", ",".join(disallowed_tools)])

    if capture_output:
        ret = subprocess.run(
            cmd,
            capture_output=True, text=True,
            cwd=work_dir, #env=run_env,
        )
    else:
        with open(log_file, "w") as log:
            ret = subprocess.run(
                cmd,
                stdout=log, stderr=subprocess.STDOUT,
                cwd=work_dir, #env=run_env,
            )

    return ret


def generate_pr_body(parent_id: str, parent_identifier: str, repo_path: str,
                     sub_issues: list[dict], env: dict,
                     work_dir: str | None = None) -> tuple[str, str]:
    prompt_file = FORGE_ROOT / "prompts" / "pr.md"
    prompt = prompt_file.read_text()

    parent_detail = fetch_issue_detail(parent_id)
    prompt = prompt.replace("{{PARENT_ISSUE_DETAIL}}", json.dumps(parent_detail, indent=2, ensure_ascii=False))

    parent_data = fetch_sub_issues(parent_id)
    prompt = prompt.replace("{{PLAN_DOCUMENTS}}", json.dumps(parent_data.get("documents", []), indent=2, ensure_ascii=False))

    sub_summary = []
    for s in sub_issues:
        sub_summary.append(f"- {s['identifier']}: {s['title']} ({s.get('state', '')})")
    prompt = prompt.replace("{{SUB_ISSUES}}", "\n".join(sub_summary))

    default_branch = detect_default_branch(repo_path)
    prompt = prompt.replace("{{DIFF_STAT}}", diff_stat(repo_path, default_branch, parent_identifier))

    ret = run(prompt, Path(work_dir or repo_path),
              model=env.get("FORGE_MODEL_PR", env["FORGE_MODEL"]),
              max_turns="1", capture_output=True)
    if ret.returncode != 0:
        return parent_detail.get("title", parent_identifier), f"Parent issue: {parent_identifier}\n\nAll sub-issues completed."

    output = ret.stdout.strip()
    title = parent_detail.get("title", parent_identifier)
    body = output

    if "TITLE:" in output and "---" in output:
        parts = output.split("---", 1)
        for line in parts[0].splitlines():
            if line.startswith("TITLE:"):
                title = line.removeprefix("TITLE:").strip()
                break
        body = parts[1].strip()
        if body.startswith("```"):
            body = body.split("\n", 1)[1] if "\n" in body else body
        if body.endswith("```"):
            body = body.rsplit("\n", 1)[0] if "\n" in body else body

    return title, body
