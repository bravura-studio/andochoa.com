# Resolve Todos Command

## Usage

```bash
/resolve-todos
```

**Purpose:** Fix ALL pending review findings in `todos/`, then clean up.
**When:** After `/review` and before `/workflows:compound`.

---

## Execution Protocol

### Step 1: Scan
```bash
ls todos/*-pending-*.md 2>/dev/null
```
If no pending files: "No pending todos. Skip to compound." Exit.

### Step 2: Fix Each Finding
For each `*-pending-*.md` file — ALL priorities (p1, p2, p3):
1. Read the finding and acceptance criteria
2. Fix the code
3. Verify the fix meets acceptance criteria
4. Delete the file after fix is committed

### Step 3: Validate
```bash
pnpm typecheck && pnpm lint
```

### Step 4: Commit + Clean
```bash
git add .
git commit -m "fix: resolve all review todos"
rm todos/*-resolved-*.md 2>/dev/null
rm todos/*-pending-*.md 2>/dev/null
```

### Step 5: Report
```
Todos resolved: X items (all fixed, all deleted)
Ready for /workflows:compound.
```

## Rules
- Fix ALL findings. No skipping, no deferring.
- Delete files after fixing. Keep the repo clean.
- If a fix would break other functionality, escalate to Ferro.
