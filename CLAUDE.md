# Scripta — andochoa.com

Personal brand content engine and website for Andre Ochoa.
Part of the BUILD.FUN.FREE portfolio (Bravura Studio).

## Project

- **Repo:** bravura-studio/andochoa.com (public)
- **Stack:** Next.js 15, TypeScript strict, Tailwind CSS, Geist Mono, MDX
- **Deploy:** Vercel (founder's personal account) at andochoa.com
- **Domain:** andochoa.com (Porkbun DNS → Vercel)

## Design System — Cursor IDE Shell

The site is wrapped in a Cursor IDE-inspired shell. Same shell on ALL pages.

### Shell anatomy
- Title bar: Mac chrome (traffic lights + "andochoa.com — Cursor")
- Activity bar: 42px, far left, icon strip (Home, Posts, Vault, About)
- Sidebar: 220px, content varies per page
- Tab bar: shows current "file" as IDE tab
- Breadcrumbs: path navigation
- Editor: main content area
- Status bar: 24px, "Keep building. -Ochoa" + context info

### Colors (black + white ONLY)
- Background: #0a0a0a
- Surface: #111111
- Surface elevated: #161616
- Text: #e0e0e0
- Text dim: rgba(255,255,255,0.42)
- Text muted: rgba(255,255,255,0.22)
- Border: rgba(255,255,255,0.07) — solid for shell chrome, dashed for content cards
- Active: rgba(255,255,255,0.06)
- Hover: rgba(255,255,255,0.04)
- NO color accents anywhere except #33ff33 in vault terminal

### Typography
- Font: Geist Mono everywhere (via next/font or Google Fonts)
- Headings: 20-28px, weight 700
- Body: 13-14px, line-height 1.8
- Labels: 9-10px, uppercase, letter-spacing 2-3px
- Max reading width: 65ch

### Components
- Borders: dashed at low opacity for content cards, solid for shell chrome
- Radius: 4-8px (shell elements), 6-8px (content cards)
- Glass: backdrop-filter blur(12px) on content cards
- Terminal: Mac window chrome (traffic lights), used in vault + 404

### Mobile
- Activity bar → bottom tab bar (4 icons)
- Sidebar → hidden, hamburger/drawer
- Tab bar + breadcrumbs → collapse or hide
- Status bar stays
- Posts: single panel with back navigation

## Content Pipeline

```
content/raw-ideas/    → Founder captures (voice notes, deep dives)
content/nuggets/      → Extracted one-liners, metrics, user stories
content/drafts/       → Synthesized long-form articles
content/published/    → Final articles (MDX, rendered on site)
```

### MDX Frontmatter
```yaml
title: "Post Title"
date: 2026-04-24
type: reflection  # struggle | win | observation | brainstorm | reflection
description: "One-liner for post list"
status: published
word_count: 380
```

## Brand Guide

- Voice: like talking to a friend over wine on a Friday night
- Interesting > Profound. Raw > Polished. Hard stuff > Easy wins.
- Sign-off: **Keep building. -Ochoa**
- Mantra: BUILD · FUN · FREE
- Zero corporate speak, jargon, or AI-sounding prose
- Full brand guide: build-fun-free/projects/scripta/brand-guide.md

## File Structure

```
app/                  → Next.js pages (layout.tsx is the IDE shell)
  page.tsx            → Homepage (welcome tab)
  posts/              → IDE split view
  about/              → About page (about.md tab)
  vault/              → Knowledge vault
  not-found.tsx       → 404 page
components/           → React components (site-shell, typing, etc.)
config/
  projects.ts         → Project data (Tmaker, Scripta, Tycoon, Striva)
  cv.ts               → CV data for about page
content/              → Content pipeline (see above)
lib/
  content.ts          → MDX reading utilities
  posts.ts            → Post helpers
public/
  profile.jpg         → Founder profile photo
  logo.jpg            → ANDOCHOA dot-matrix wordmark
.claude/commands/     → Workflow commands (review, resolve-todos, compound)
todos/                → Review findings (temporary, cleaned after resolve)
```

## Development Workflow

Every issue follows this sequence. No skipping.

1. **Build:** One subtask at a time → typecheck + lint → commit per parent
2. **Review:** `/review last-commit` → findings go to `todos/`
3. **Resolve:** `/resolve-todos` → fix ALL findings → delete todo files
4. **Compound:** `/workflows:compound` → learnings to CLAUDE.md (HOT) + qmd vault (WARM)
5. **Handoff:** Set status to in_review. Include in comment:
   - "Review: X findings found, all resolved"
   - "Compound: {rule added / pattern written / nothing new}"

## Rules (HOT layer — max 50)

1. ALL pages must render inside the Cursor IDE shell. No page has its own nav.
2. Geist Mono everywhere. No fallback fonts visible.
3. No color accents except vault terminal green (#33ff33).
4. All borders on content cards are dashed, low opacity.
5. Shell chrome borders are solid, not dashed.
6. Every post ends with "Keep building. -Ochoa"
7. Status bar always shows "Keep building. -Ochoa" on the left.
8. Tab bar always shows current "file" name.
9. Profile photo is circular with dashed border on homepage.
10. config/projects.ts: Tmaker (paused), Scripta (active), Tycoon (planned), Striva (planned).
11. Never push to main. Feature branches + PRs only.
12. Never add features beyond the issue spec.
13. Mobile: activity bar becomes bottom tab bar, sidebar becomes drawer.
14. Always run typecheck + lint before committing.
15. Always base PRs on main, never on feature branches.
16. Never work in /tmp mirrors. Work directly in /opt/bff/scripta/repos.
17. NEVER merge PRs. Create the PR, hand off to QA. After QA passes, the FOUNDER merges. Agents do not merge.
18. NEVER push directly to main. All work goes through feature branch → PR → QA → founder merge.
19. Mobile sidebar drawer must close when any filter/folder item is selected. Always call setMobileSidebarOpen(false) in sidebar onClick handlers alongside the filter state changes.
20. Cards that link externally must show explicit affordances: ArrowUpRight icon (muted, brightens on hover), cursor-pointer, title underline on group-hover, domain badge that brightens on hover.
21. ALWAYS create a PR for every issue. Push branch → `gh pr create` → hand off to QA. Never mark an issue done without a PR link in the handoff comment.

## Knowledge

- qmd vault "scripta" — 431 docs of reference material
- Search: `qmd search "topic" -c scripta`
- Contains: writing style references, business strategy, brand training data
- Write patterns: `qmd add -c scripta -t "Pattern: {title}" -f /path/to/file.md`
