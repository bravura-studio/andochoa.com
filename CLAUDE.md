# Scripta — andochoa.com

Personal brand content engine and website for andochoa.com.
4th product in the BUILD.FUN.FREE portfolio.

## Content Pipeline

```
content/raw-ideas/    -> Founder captures (voice notes, observations, insights)
content/nuggets/      -> Extracted one-liners, metrics, user stories
content/drafts/       -> Synthesized long-form articles
content/published/    -> Final articles (MDX, ready for website)
```

## Knowledge

- Training data lives in qmd vault "scripta" (NOT in this repo)
- Search with: `qmd search "topic" -c scripta`
- 9 writing style references (Tim Urban essays)
- 115 business strategy docs

## Architecture

- Part of BUILD.FUN.FREE holding company
- Charter: `build-fun-free/projects/scripta/CHARTER.md`
- 3-layer architecture: CEO -> Coder -> QA (see AD-001)

## Rules

- Content voice: authentic, founder-perspective, build-in-public transparency
- Tone: conversational but substantive, complex ideas made accessible
- Anti-patterns: humble bragging, generic advice, clickbait, AI-sounding prose
- Never publish under the founder's name without board approval

## Future (not yet built)

- Next.js personal site (app/ directory)
- Voice capture workflow
- Social media repurposing
- Vercel deployment
