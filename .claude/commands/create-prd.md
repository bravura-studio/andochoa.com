# Create PRD Command

## Usage

```bash
/create-prd [feature-name]
```

**Purpose:** Generate PRD with clarifying questions before development
**Output:** `product/prds/NNNN-prd-[name].md`

---

## Execution Protocol

### Step 1: Clarifying Questions

Before writing, ask 5-8 questions:

**Required questions:**
1. What problem does this solve?
2. Who are the target users?
3. What's the expected outcome?
4. Any constraints (timeline, tech, budget)?

**Feature-specific questions:**
- Data: Sources, formats, storage needs?
- UI: Design system, responsive requirements?
- Integration: APIs, auth, third-party services?
- Performance: Load expectations, SLAs?

Display:
```
Before writing the PRD, I need clarity:

1. [Question 1]
2. [Question 2]
...

Please answer all before I proceed.
```

**STOP: Wait for answers**

---

### Step 2: Generate PRD

Create `product/prds/NNNN-prd-[name].md` with 9 sections:

```markdown
# PRD: [Feature Name]

**Created:** [date]
**Status:** Draft
**Author:** Claude + [user]

---

## 1. Problem Statement
[What problem, who has it, why it matters]

## 2. Goals & Success Metrics
- Goal 1 → Metric
- Goal 2 → Metric

## 3. User Stories
- As [persona], I want [action], so that [outcome]

## 4. Functional Requirements
### 4.1 Core Features
- FR-1: [Requirement]

### 4.2 Edge Cases
- [Edge case handling]

## 5. Non-Functional Requirements
- Performance: [targets]
- Security: [requirements]
- Accessibility: [requirements]

## 6. Technical Approach
- Architecture: [approach]
- Dependencies: [new packages if any]
- Integration points: [APIs, services]

## 7. Acceptance Criteria
- AC-1: Given [context], when [action], then [result]

## 8. Out of Scope
- [Explicitly excluded items]

## 9. Open Questions
- [Unresolved items needing decision]
```

---

### Step 3: Save & Confirm

1. Determine next PRD number (check `product/prds/` for existing)
2. Save to `product/prds/NNNN-prd-[name].md`
3. Display summary:

```
PRD created: product/prds/NNNN-prd-[feature-name].md

Next: /generate-tasks product/prds/NNNN-prd-[feature-name].md
```

---

## PRD Numbering

Format: `NNNN-prd-[kebab-case-name].md`

Examples:
- `0001-prd-user-auth.md`
- `0002-prd-dashboard-widgets.md`
