# Linear Status Design & AI Agent Workflow

## Workflow Overview

```
1. Human creates parent issue (Backlog)
        ↓ Change issue status to Planning
2. Agent fetches and analyzes issue via MCP
3. Agent creates sub-issues (planning)
4. Agent changes status to Pending Approval
        ↓ Slack notification → human reviews plan
5. Human changes status to Implementing (approval)
        ↓
6. Agent implements sub-issues sequentially, creates PRs
7. Agent changes status to In Review
        ↓ Slack notification → human reviews and merges PRs
8. Human changes status to Done
        ↓
9. All sub-issues Done → parent issue auto-Done
```

---

## Issue Status Design

Customized per team (Settings → Teams → Issue statuses & automations)

| Status | Category | Actor | Description |
|--------|----------|-------|-------------|
| `Backlog` | Backlog | Human | Not started |
| `Planning` | Started | Agent | Creating sub-issues |
| `Pending Approval` | Started | Human | Awaiting plan approval |
| `Implementing` | Started | Agent | Building |
| `In Review` | Started | Human | PR under review |
| `Done` | Completed | Auto | Completed |
| `Cancelled` | Cancelled | Human | Cancelled |

```
Backlog → Planning → Pending Approval → Implementing → In Review → Done
                                                                  ↘ Cancelled
```

---

## Project Status Design

Humans manage the roadmap and high-level progress. Agents do not modify project status.

| Status | Description |
|--------|-------------|
| `Planned` | Planned, not started |
| `In Progress` | Issues in progress |
| `Completed` | All issues completed |
| `Cancelled` | Cancelled |

```
Planned → In Progress → Completed
        ↘ Cancelled
```

---

## Separation of Concerns

| Layer | Purpose | Operator |
|-------|---------|----------|
| Project Status | Roadmap, high-level progress | Human |
| Issue Status | Agent-human workflow | Agent + Human |
| Sub-issue | Implementation task breakdown | Agent |
| Label | Classification (repo:xxx, Bug, Feature, etc.) | Agent + Human |

---

## Webhook Trigger Design

| Issue Status Change | Detection | Action |
|---------------------|-----------|--------|
| `Backlog` → `Planning` | Webhook | Agent starts planning |
| `Planning` → `Pending Approval` | Webhook | Slack notification to human |
| `Pending Approval` → `Implementing` | Webhook | Agent starts implementation |
| `Implementing` → `In Review` | Webhook | Slack notification to human |

---

## Sub-issue Automation Settings

Enable the following in Settings → Teams → Workflow:

- **Auto-complete parent issue when all sub-issues are Done**
- **Auto-cancel all sub-issues when parent issue is Cancelled**
