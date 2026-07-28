# Writing Feedback

> Accumulated corrections and learnings from draft reviews.
> Read this before drafting. Each entry is a real correction from a real draft.
> Newest entries at the top.

---

## Voice & Tone

- **Dates in frontmatter must be quoted** — `date: "2025-09-26"` not `date: 2025-09-26`. YAML parses unquoted dates as Date objects, breaks the site build. (Learned: 2026-04-29, Animal Spirit draft)

## Structure

- **Journal drafts go in `content/drafts/journals/`, date-prefixed** — `content/drafts/journals/<YYYY-MM-DD>-<slug>.md`, NOT the top-level `content/drafts/`. The site loader (`lib/posts.ts`) renders `content/published/` recursively; every published article lives at `content/published/journals/<YYYY-MM-DD>-<slug>.md`. Drafts must mirror that path so publishing is a clean move. (Learned: 2026-07-28, House Money draft — deep-dive skill had stale `content/drafts/<slug>.md` path; skill now fixed.)

## Word Choice

- (No entries yet)

## What Works

- Opening with a concrete scene or overheard quote consistently produces the strongest hooks (Freedom Gap, Animal Spirit)
- One-line paragraphs as pivot points between sections ("So the animal spirit wasn't the problem. The cage was.")
- Using the founder's exact phrasing from the deep dive as raw material — don't paraphrase away the energy
- "Two kinds of X" as a framing device works well for contrasting past vs present (Never Felt So Alive)

## What Doesn't Work

- (No entries yet — add when drafts get corrected)
