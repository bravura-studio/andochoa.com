# Generate Tasks Command

## Usage

```bash
/generate-tasks [prd-path]
```

**Purpose:** Convert PRD into self-contained executable task list — each task embeds the PRD context needed to implement it without re-reading the PRD.
**Input:** PRD from `product/prds/NNNN-prd-*.md`
**Output:** `product/tasks/tasks-NNNN-prd-[name].md`

---

## Two-Phase Approach

### Phase 1: Generate Parent Tasks

Read the PRD and:

1. **Extract PRD identifiers** — Scan all sections for FR-N (functional requirements), AC-N (acceptance criteria), §6 technical notes, and inline code snippets (types, schemas, API shapes).
2. **Group FRs into parent tasks** — Each parent task maps to 2-5 FRs. If a task would need >5 FRs, split it.
3. **Write PRD Summary header** — Extract problem (§1), goal (§2), success metric (§2), and out-of-scope (§8) into a 3-5 line summary.

Output format:

```markdown
# Tasks: [Feature Name]

**PRD:** product/prds/NNNN-prd-[name].md
**Created:** [date]
**Status:** Planning

### PRD Summary
> **Problem:** [1-sentence from §1]
> **Goal:** [Key goal from §2]
> **Success:** [Primary metric from §2]
> **Scope:** [What's explicitly out of scope from §8, if relevant]

---

## Parent Tasks

- [ ] 1. [Parent task 1] — FR-1, FR-2, FR-3
- [ ] 2. [Parent task 2] — FR-4, FR-5
...
```

Display:
```
Generated X parent tasks from PRD.
FR/AC mapping: [total FRs] requirements → [X] tasks

1. [Parent task 1] (FR-1, FR-2, FR-3)
2. [Parent task 2] (FR-4, FR-5)
...

Type "Go" to expand into subtasks, or provide feedback.
```

**STOP: Wait for "Go" or feedback**

---

### Phase 2: Expand Subtasks

After "Go", expand each parent into granular subtasks with embedded PRD context:

```markdown
## Task 1: [Parent task name]

### PRD Context
> **FR-1**: [Exact requirement text, condensed if >2 lines]
> **FR-2**: [Exact requirement text]
> **AC-1**: [Acceptance criterion to verify against]
> **Technical**: [Key implementation note from §6, if task-relevant]

### Subtasks:
- [ ] 1.1 [Specific implementation step]
- [ ] 1.2 [Specific implementation step]
- [ ] 1.3 [Specific implementation step]

### Validation:
- `pnpm typecheck` / `pnpm lint`
- Verify: AC-1, AC-2 [specific ACs this task must satisfy]

### Dependencies:
- Requires: [prior tasks if any]
- Enables: [subsequent tasks if any]
```

---

## PRD Context Mapping Rules

### What to embed per task

1. **FR mapping**: Quote directly from PRD — condense if >2 lines but preserve the FR-N identifier.
2. **AC mapping**: Each task maps to 1-3 acceptance criteria. These become the Validation checklist items.
3. **Technical notes**: Pull from §6 only when it contains specific guidance (architecture patterns, file paths, API shapes). Skip generic notes like "use TypeScript strict."
4. **Code snippets**: Include inline if they define types, schemas, or API shapes the task must implement. These are high-value context. If a snippet exceeds 10 lines, reference the PRD section instead.
5. **Non-functional requirements**: Include only if task-specific (e.g., "< 200ms response time" for a performance task).

### What NOT to embed per task

- User stories — they inform task grouping, not execution
- Full problem statement — already in header summary
- Goals/metrics table — already in header summary
- Open questions — must be resolved before task generation
- Generic NFRs that apply to all tasks

### Density rule

Each task's `### PRD Context` section should be **3-10 lines**. If it would exceed 10 lines, the task covers too much — split it.

---

## Task Structure Rules

1. **Parent tasks:** 5-10 high-level chunks, each mapping to 2-5 FRs
2. **Subtasks:** 3-7 steps per parent
3. **Each subtask:** Single, atomic action
4. **Validation:** Every parent task ends with validation referencing specific AC-N items
5. **Dependencies:** Explicit ordering
