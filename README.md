# forge

Linear-driven AI agent. Automatically plans and implements tasks triggered by issue status changes.

## Setup

```bash
./setup.sh
```

### Prerequisites

- Python 3.10+
- [Claude Code](https://claude.com/claude-code) CLI
- [GitHub CLI](https://cli.github.com/) (`gh`)
- `bubblewrap` and `socat` (for sandbox)

```bash
# Ubuntu/Debian
sudo apt-get install bubblewrap socat
```

### Configuration

1. Copy example configs:
   ```bash
   cp config/forge.env.example config/forge.env
   cp config/repos.conf.example config/repos.conf
   ```

2. Edit `config/forge.env` — set `LINEAR_API_KEY`, `FORGE_TEAM_ID`, etc.

3. Edit `config/repos.conf` — map labels to repository paths:
   ```
   myproject=/home/user/dev/myproject
   ```

4. Add the Linear MCP server to Claude Code:
   ```bash
   claude mcp add linear-server -- npx -y @anthropic-ai/linear-mcp-server
   ```

## Usage

```bash
python bin/forge.py
```

Or via the wrapper script:

```bash
bin/main.sh
```

## Architecture

```
forge.py
  ├── Poll "Planning" issues → dispatch to planning prompt
  ├── Poll "Implementing" issues (parent) → fetch sub-issues + dependency check
  │   ├── Filter ready sub-issues (blockers resolved, not terminal)
  │   └── Dispatch each to implementing prompt
  └── Wait for all processes

run_claude.py
  ├── Load prompt template + substitute variables
  ├── Create worktree (implementing only)
  ├── Write sandbox settings
  └── Execute claude CLI in sandboxed environment

Planning (prompts/planning.md)
  ├── Analyze issue via Linear MCP
  ├── Delegate code investigation to Plan agent
  ├── Create plan document + sub-issues
  ├── Validate dependency cycle
  └── Update status → Pending Approval

Implementing (prompts/implementing.md)
  ├── Conductor fetches issue + parent context + plan
  ├── Launch implementer agent (Sonnet)
  ├── Launch reviewer agent (Opus)
  ├── Feedback loop (max 2 rounds)
  └── Commit → Push → Draft PR → Linear update
```

## Workflow

```
Backlog → Planning → Pending Approval → Implementing → In Review → Done
```

| Status | Actor | Description |
|--------|-------|-------------|
| Backlog | Human | Not started |
| Planning | Agent | Creating sub-issues and plan |
| Pending Approval | Human | Reviewing the plan |
| Implementing | Agent | Building + PR creation |
| In Review | Human | Reviewing PRs |
| Done | Auto | Completed |

## File Structure

| Path | Description |
|------|-------------|
| `bin/forge.py` | Main entry point — polling, dispatch, concurrency |
| `bin/poll.py` | Linear GraphQL polling + sub-issue dependency resolution |
| `bin/run_claude.py` | Per-issue claude CLI execution with sandbox |
| `bin/check_cycle.py` | Dependency cycle detection CLI |
| `bin/main.sh` | Shell wrapper for forge.py |
| `prompts/planning.md` | Planning phase prompt template |
| `prompts/implementing.md` | Implementing phase prompt (conductor pattern) |
| `config/forge.env` | Environment configuration (gitignored) |
| `config/repos.conf` | Label → repo path mapping (gitignored) |
| `setup.sh` | Environment setup and validation script |

## Models

| Role | Model | Rationale |
|------|-------|-----------|
| Planner | Opus | High reasoning for codebase analysis and task decomposition |
| Conductor | Sonnet | Procedural orchestration, cost-efficient |
| Implementer | Sonnet | Code generation, speed and cost balance |
| Reviewer | Opus | Deep reasoning for bug and design issue detection |

## Sandbox

Each claude CLI execution runs with Claude Code's native sandbox:

- **Filesystem**: Write restricted to work directory + logs. `~/.ssh`, `~/.aws`, `~/.gnupg` denied.
- **Network**: `allowManagedDomainsOnly` — only `api.linear.app`, `github.com`, `api.anthropic.com` allowed.
- **Escape hatch disabled**: `allowUnsandboxedCommands: false`
