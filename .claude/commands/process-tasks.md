# Process Tasks Command

## Usage

```bash
/process-tasks [tasks-path]
```

**Purpose:** Execute tasks one subtask at a time with validation
**Input:** Task list from `product/tasks/tasks-*.md`

---

## Execution Protocol

### Core Rules

1. **PRD Context is your spec** — Each task's `### PRD Context` section contains the exact functional requirements and acceptance criteria from the PRD. Use it as your primary implementation guide. Do NOT re-read the full PRD unless context is missing.
2. **Code snippets are requirements** — If PRD Context includes type definitions, schemas, or API shapes, implement them as specified. These are requirements, not suggestions.
3. **One subtask at a time** — Never work on multiple subtasks
4. **Validate against ACs** — After completing a parent task, verify against the AC-N items in the Validation section. These are source-of-truth acceptance criteria from the PRD.
5. **Commit per parent** — One meaningful commit after each parent completes
6. **Update task file** — Mark items complete as you go

---

### Execution Flow

```
Read tasks file
│
├── Read PRD Summary header for overall context
│
├── For each PARENT task:
│   │
│   ├── Read ### PRD Context for requirements
│   │
│   ├── For each SUBTASK:
│   │   ├── Announce: "Working on [X.Y]: [description]"
│   │   ├── Implement the subtask per FR-N specs
│   │   ├── Mark complete in task file
│   │   └── STOP if blocked
│   │
│   ├── Run validation:
│   │   ├── pnpm typecheck
│   │   ├── pnpm lint
│   │   └── Verify AC-N items from Validation section
│   │
│   ├── If validation fails:
│   │   └── Fix before proceeding
│   │
│   ├── Commit parent task:
│   │   └── "feat([scope]): [parent task description]"
│   │
│   └── Post-commit review:
│       ├── Run /review last-commit (lightweight single-pass)
│       ├── If 🔴 Must Fix issues found:
│       │   ├── Fix the issues immediately
│       │   ├── Amend the commit: git commit --amend
│       │   └── Re-run /review last-commit to verify
│       └── If only 🟡/💡 or clean: proceed to next parent
│
└── Report completion
```

---

### Validation Commands

Run after completing each parent task:

```bash
pnpm typecheck
pnpm lint
```

Then check each AC-N item listed in the task's Validation section. These are the measurable acceptance criteria from the PRD — the task is not done until they pass.

---

### Commit Protocol

After each parent task passes validation:

```bash
git add [relevant files]
git commit -m "feat([scope]): [parent task description]

- [subtask 1.1]
- [subtask 1.2]

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Post-Commit Review

After each parent task commit, run a lightweight review of that commit:

1. Execute `/review last-commit` — single-pass checklist (security, performance, patterns, simplicity)
2. All findings are persisted to `todos/` as pending items
3. If **🔴 Must Fix** (p1) issues are found: fix them immediately, amend the commit, re-run review
4. If only **🟡 Should Fix** (p2) or **💡 Suggestions** (p3): persisted to `todos/` but non-blocking — proceed
5. If clean: proceed to next parent task

This catches issues incrementally (small diffs, in context) instead of reviewing the entire feature at the end, saving significant review time and tokens.

---

### Handling Blockers

If blocked on a subtask:

```
BLOCKED on [X.Y]: [subtask description]

Issue: [what's blocking]
Options:
1. [Option A]
2. [Option B]

Which approach should I take?
```

If PRD Context is insufficient for a subtask (missing FR or ambiguous requirement), check the PRD path in the task file header before asking the user.

---

### Completion Report

```
All tasks complete!

Summary:
- Parent tasks: X completed
- Subtasks: Y completed
- Commits: Z created

Validation: TypeScript ✓, ESLint ✓, ACs verified ✓

Files changed: [list key files]
```
