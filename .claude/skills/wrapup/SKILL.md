---
name: wrapup
description: End-of-session wrapup — updates worklog and CLAUDE.md with session summary
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep
---

# End-of-Session Wrapup

Perform an end-of-session wrapup by completing both steps below. Review the full conversation to understand what was accomplished.

## Step 1: Update WORKLOG.md (Session Logbook)

Read `WORKLOG.md` in the project root. If it doesn't exist, create it with a `# Work Log` header.

Append a new entry at the **top** of the log (below the header, above previous entries) using this format:

```
## YYYY-MM-DD

### Work Done
- (bullet list of what was accomplished this session)

### Decisions Made
- (any architectural, product, or technical decisions — omit section if none)

### Issues Encountered
- (bugs, blockers, workarounds — omit section if none)

### Next Steps
- (what to pick up in the next session)

---
```

Guidelines:
- Be concise but specific — future-you should understand what happened
- Include file paths for new files or major changes
- Keep previous entries untouched (this is an append-only log)

## Step 2: Update CLAUDE.md (Long-Term Context)

Read `CLAUDE.md` in the project root. From this session's work, identify **only durable information** that will help in future sessions:

**DO update:**
- `## Current Status` — refresh to reflect where the project stands now
- `## Next Steps` — refresh to reflect the actual next priorities
- Architecture/tech stack sections — if new patterns, components, or tools were added
- Data model — if schema changed
- Any new sections needed for decisions that affect future work

**DO NOT add:**
- Session-specific debugging steps or workarounds
- Transient issues (install problems, port conflicts, etc.)
- Anything already adequately covered in the worklog
- Verbose descriptions — keep CLAUDE.md scannable

The goal: a new Claude session reading CLAUDE.md should have everything it needs to be productive, without wading through session history.
