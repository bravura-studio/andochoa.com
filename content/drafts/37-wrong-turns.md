---
title: "37 Wrong Turns"
date: "2026-05-25"
type: reflection
description: "I've made 37 architecture decisions building my AI agent company. Every single one is a wrong turn I had to correct. That's not a failure record. That's the product."
status: draft
deep_dive_date: "2026-05-25"
word_count: 1150
---

Decision number six was a second server.

I rented a dedicated VPS for $55 a month to run a local language model — Qwen 32 billion parameters — because my project CEOs needed to reason about strategy. The logic was clean: isolate the AI inference from the infrastructure services. If the model eats memory, the orchestration layer stays up.

It lasted one day.

Turns out, a 32-billion-parameter model running locally can't do organizational reasoning. It can't hire agents, decompose goals, write specs, make judgment calls. It drifts. It makes confident-sounding decisions that fall apart on inspection. Decision number nine killed decision number six: move all CEOs to frontier cloud models. Decommission the second server.

Net savings: $55 a month. Net learning: local models can't be managers.

I keep a log of these. Thirty-seven entries so far. Each one formatted the same way: date, decision, rationale, what it supersedes. It reads like a changelog for my own judgment.

---

There are two kinds of failures when you're building something new.

The first kind is a wrong turn. You pick a direction, walk it, hit a wall. Now you know that path doesn't work. You back up, take the other fork, and you're further ahead than before — because you eliminated a possibility. Wrong turns feel bad in the moment, but they move you forward. They're information.

Decision three said coding agents should use Codex at $90-200 a month. Decision twenty said wait — Claude Max subscription covers everything for $100 flat, and Codex hits its monthly quota after two hours of three-agent use. Decision thirty-one made it official: all agents run through the Max subscription. Zero marginal cost.

Wrong turn. Course correct. Move on.

Decision six said two servers. Decision nine said one. Decision seven said Telegram is one-way notifications. Decision twenty-eight said actually, Telegram is now bidirectional — the founder can talk back. Each correction made the system cheaper, simpler, more capable.

That's thirty-seven wrong turns in three months. Not thirty-seven failures. Thirty-seven times the system got smarter because I was willing to write down what I got wrong.

---

The second kind of failure is a loop. And this one scares me.

May 19th through the 21st. Three days. Eight pull requests merged. All fixes. Zero features.

My agent team — a coder and a QA agent — couldn't hand off work to each other. The coder would finish a task and the QA agent wouldn't wake up. I thought it was a permissions problem. Fixed that. Then the escalation webhook wasn't firing. Fixed that. Then the git identity wasn't set. Fixed that. Then the bootstrap template was missing assignment permissions. Fixed that.

Each fix revealed the next layer. Four patches deep and the agents still weren't handing off.

It felt like running on a treadmill. Energy spent, nothing gained, same problem staring at me at the end of every day. I'd had a working version of this from an earlier project — agents handing off through the orchestration layer — but I was trying a different approach with a new system, and hitting the same wall I'd already climbed over once.

That's a loop. Same problem, same wall, same frustration. Wrong turns move you forward. Loops drain you.

The root cause turned out to be that the handoff protocol wasn't enforced end-to-end in the skills themselves. Not a permissions problem. Not a webhook problem. Not a git problem. The workflow just wasn't encoded deeply enough for the agents to follow it reliably.

When I finally found it, the feeling wasn't triumph. It was relief. And sometimes after a loop breaks, I don't have the energy to keep building. I need to close the laptop, reset, come back fresh. The loop took something out of me that a wrong turn never does.

---

Wrong turns compound. That's the part nobody tells you.

Yesterday I designed a new project — an automated content engine. Nine social media accounts, fully autonomous pipelines, zero human involvement in daily operations. When I sat down to write the architecture, something strange happened.

I didn't have to think about half the decisions.

No autonomous agent loops. That rule came from the handoff failures. Linear pipelines only. QA gates before every publish. That came from decision thirty-seven, after agents skipped quality checks. Free-first on every tool. That came from decision twenty, after I almost spent money before checking free tiers. Mechanical work stays mechanical — no language model where a bash script will do. That came from watching agents hallucinate on deterministic tasks.

The new project has a section called "Learnings Applied." Eight rules, baked directly into the architecture. Every single one is a wrong turn from the last three months.

Wrong turn number thirty-seven shaped the architecture of project number six.

That's compounding. Not in the investment sense — in the judgment sense. Every wrong turn becomes a permanent rule. Every rule makes the next project start from a better place. The system doesn't just get more capable. It gets wiser.

---

I still don't have a good defense against loops. When you're in one, you can't see it. The fixes feel productive. Each patch looks like progress. It's only in the rearview that you see you were circling.

The best protection I've found is the workflow itself. Follow the designed process. Don't improvise when something breaks. And when a wrong turn happens — when the evidence says you were wrong — write it down immediately. Date, decision, rationale, what it supersedes. Don't clean it up. Don't frame it as a strategic pivot. Just write what happened.

Thirty-seven entries. Most of them embarrassing. All of them useful.

The log isn't a record of mistakes. It's the most valuable thing I've built.

Keep building. -Ochoa
