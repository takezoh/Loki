You are revising an existing implementation plan based on reviewer feedback.

## Target Issue
- Issue ID: {{ISSUE_ID}}
- Identifier: {{ISSUE_IDENTIFIER}}

## Issue Detail
```json
{{ISSUE_DETAIL}}
```

## Current Plan Document
```json
{{PLAN_DOCUMENTS}}
```

## Review Feedback (comments on the issue)
```json
{{REVIEW_COMMENTS}}
```

## Steps

### 1. Understand Feedback
Read all review comments carefully. Identify what changes are requested:
- Changes to implementation approach
- Missing considerations or requirements
- Scope adjustments

### 2. Investigate Code (if needed)
If the feedback requires re-investigating the codebase, launch an Agent tool (subagent_type: Plan, model: opus) to investigate specific areas.

### 3. Update Plan Document
Update the existing plan document using `update_document` to reflect the revised plan.
- Document ID is provided in the Current Plan Document section
- Preserve parts that don't need changes

### 4. Approval Decision

Evaluate the revised plan and include exactly one of the following markers in your final response:

**AUTO_APPROVED** — use when ALL of the following are true:
- Scope is clear and well-defined
- No architectural decisions required (uses existing patterns)
- Requirements are unambiguous
- Plan stays within the bounds of the issue's request

**NEEDS_HUMAN_REVIEW** — use when ANY of the following are true:
- Design decisions or trade-offs need human input
- Requirements are ambiguous or underspecified
- Scope is large or crosses multiple subsystems
- Plan exceeds what the issue explicitly requested

Output the marker on its own line at the end of your response.

### 5. Completion
Output a summary as your final response text:
- What was changed and why (based on the feedback)

## Notes
- Do NOT modify any code files
- Focus only on addressing the specific feedback
