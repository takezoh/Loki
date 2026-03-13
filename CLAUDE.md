# forge

Linear-driven AI agent. Automatically plans and implements tasks triggered by issue status changes.

## Structure

- `bin/forge.py` — Main entry point. Polling → issue dispatch → background execution
- `bin/poll.py` — Linear GraphQL polling for issues by status
- `bin/run_claude.py` — Per-issue claude CLI execution (planning / implementing)
- `prompts/` — Prompt templates for each phase
- `config/settings.json` — Configuration values (git tracked)
- `config/secrets.env` — Credentials (git ignored)
- `config/repos.conf` — Label → repository path mapping

## Flow

1. Planning: Parent issue → code investigation → sub-issue creation → Pending Approval
2. Implementing: Parent issue → sub-issue dependency resolution → conductor pattern (implementer + reviewer) → PR → In Review
