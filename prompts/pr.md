Generate a pull request title and body for the following changes.

## Parent Issue
{{PARENT_ISSUE_DETAIL}}

## Plan
{{PLAN_DOCUMENTS}}

## Sub-issues
{{SUB_ISSUES}}

## Diff Stats
{{DIFF_STAT}}

## Output Format

Output EXACTLY in this format (no extra text before or after):

```
TITLE: <concise PR title without issue identifier prefix>
---
<PR body in markdown>
```

PR body guidelines:
- Start with `## Summary` section with 2-4 bullet points
- Add `## Changes` section listing what each sub-issue implemented
- Link to parent Linear issue using identifier
- Keep it concise but informative
