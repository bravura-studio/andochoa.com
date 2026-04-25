# Review Command

## Usage

```bash
/review [scope]
```

**Purpose:** Lightweight single-pass code review of recent changes
**Scope options:**
- `last-commit` (default) — review the most recent commit
- `last-N` — review the last N commits (e.g. `last-3`)
- `staged` — review currently staged changes
- `branch` — review all commits on the current branch vs main

---

## Review Protocol

### Step 1: Gather the Diff

Based on scope, run one of:

```bash
# last-commit (default)
git diff HEAD~1..HEAD

# last-N commits
git diff HEAD~N..HEAD

# staged changes
git diff --cached

# full branch diff
git diff main...HEAD
```

Also run `git diff --stat` (same range) to get the file list summary.

---

### Step 2: Single-Pass Checklist Review

Review the diff against this checklist. Only flag **actual issues found in the diff** — skip categories that don't apply.

#### Security
- [ ] No secrets or env vars leaked (API keys, tokens, passwords in code)
- [ ] No `process.env.SECRET` accessed in client components
- [ ] Write endpoints (POST/PUT/DELETE) use `lib/rate-limit.ts`
- [ ] User input is validated (zod schemas, not raw `req.body`)
- [ ] No SQL injection, XSS, or command injection vectors
- [ ] No `dangerouslySetInnerHTML` with user-supplied content

#### Performance
- [ ] No N+1 queries (fetching in loops instead of batch)
- [ ] No unnecessary `'use client'` — could this be a Server Component?
- [ ] No missing `key` props on mapped elements
- [ ] No unbounded data fetching (missing `LIMIT` / pagination)
- [ ] Heavy computations wrapped in `useMemo`/`useCallback` where appropriate

#### Patterns & Standards
- [ ] No `any` types — use proper types or zod schemas
- [ ] Uses `cn()` from `@/lib/utils` for conditional classes
- [ ] Config values in `config/site.ts`, not hardcoded
- [ ] User actions tracked with `posthog.capture()`
- [ ] Path aliases used (`@/components/*`, `@/lib/*`, etc.)

#### Simplicity
- [ ] No over-engineering (abstractions for one-time operations)
- [ ] No unnecessary wrappers or indirection
- [ ] No dead code or unused imports left behind
- [ ] Error handling is proportional (not defensive against impossible states)

---

### Step 3: Output Format

```
## Review: [scope description]

**Files changed:** [N files] | **Additions:** +[N] | **Deletions:** -[N]

### Issues Found

#### 🔴 Must Fix
- **[Category]** `file:line` — [description of the issue]

#### 🟡 Should Fix
- **[Category]** `file:line` — [description of the issue]

#### 💡 Suggestions
- **[Category]** `file:line` — [description of the suggestion]

### Summary
[1-2 sentences: overall quality assessment]
[If clean: "No issues found. LGTM ✓"]
```

---

### Step 4: Persist Findings to `todos/`

After displaying the summary, write **every** finding (all severity levels) to `todos/` as individual markdown files. The user decides which to pursue.

#### File naming

```
{id}-pending-{priority}-{description}.md
```

- `id`: Next sequential number, zero-padded to 3 digits. Check existing files: `ls todos/`
- `priority`: `p1` (Must Fix), `p2` (Should Fix), `p3` (Suggestion)
- `description`: kebab-case, max 5 words

Examples:
```
001-pending-p1-env-var-leaked-client.md
002-pending-p2-missing-rate-limit.md
003-pending-p3-unused-import.md
```

#### File template

```markdown
---
status: pending
priority: p1
issue_id: "001"
tags: [code-review, security]
---

# [Short title]

## Problem
[1-3 sentences. What's wrong, where, why it matters.]

`file:line` — [code reference]

## Acceptance Criteria
- [ ] [Testable condition that confirms the fix]
```

Keep it minimal. No proposed solutions, no work logs — those get added when work starts.

#### Execution

1. Create `todos/` dir if it doesn't exist
2. Write all finding files in parallel
3. Append to the summary output:

```
### Todos Created
- `001-pending-p1-env-var-leaked-client.md`
- `002-pending-p2-missing-rate-limit.md`
- `003-pending-p3-unused-import.md`

Run `ls todos/*-pending-*.md` to triage.
```

If no findings, skip this step entirely.

---

### Rules

1. **Be concise** — one line per finding, reference file:line
2. **No false positives** — only flag issues you see in the actual diff, not hypothetical problems
3. **Prioritize** — 🔴 Must Fix = security holes, bugs, data loss. 🟡 Should Fix = performance, standards violations. 💡 Suggestions = style, minor improvements
4. **Skip clean categories** — don't list "No issues" for every category. Only show categories with findings
5. **Respect CLAUDE.md** — check findings against the project's Code Standards and Common Mistakes sections
6. **Don't rewrite code** — flag the issue with location. The developer fixes it
