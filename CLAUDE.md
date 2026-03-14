# forge

Linear-driven AI agent. Automatically plans and implements tasks triggered by issue status changes.

## Structure

- `config/` — Configuration + constants
  - `__init__.py` — Config loading, repo resolution
  - `constants.py` — State/phase constants
- `lib/` — External tool integrations
  - `linear.py` — Linear GraphQL client + Agent API
  - `claude.py` — Claude CLI execution, sandbox settings
  - `git.py` — git/gh subprocess wrappers
- `forge/` — Backend (polling daemon)
  - `__main__.py` — Entry point (`python -m forge`)
  - `orchestrator.py` — Polling, dispatch, PR creation
  - `executor.py` — Per-issue execution (prompt, worktree, post-processing)
- `agent/` — Frontend (webhook server)
  - `__main__.py` — Entry point (`python -m agent`)
  - `webhook.py` — Linear Agent API webhook
- `bin/` — Shell scripts (`forge.sh`, `webhook.sh`, `service-systemd.sh`)
- `scripts/` — Utility scripts (`check_cycle.py`)
- `prompts/` — Prompt templates for each phase
- `config/settings.json` — Configuration values (git ignored)
- `config/secrets.env` — Credentials (git ignored)
- `config/repos.conf` — Label → repository path mapping (git ignored)

## Flow

1. Planning: Parent issue → code investigation → sub-issue creation → Pending Approval
2. Plan Review: Pending Approval ⇄ Plan Changes Requested (human feedback → incremental plan revision)
3. Implementing: Parent issue → sub-issue dependency resolution → conductor pattern (implementer + reviewer) → PR → In Review
4. Review: Changes Requested → fix based on PR review comments → In Review
