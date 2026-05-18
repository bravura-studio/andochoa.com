---
title: "The Invisible Work"
date: "2026-05-18"
type: short
description: "I built the AI company everyone's talking about. Most of my time goes into work that doesn't look like building at all."
status: published
word_count: 1050
---

Last week I merged fourteen pull requests.

Not one of them shipped a feature.

Skills architecture. QA gates. Sprint chains. A restart wrapper for my CEO agent. A bootstrap command so new projects don't start from scratch every time. Fourteen PRs. Zero product.

I run four products with an AI agent team. Six agents. A single server. $170 a month. I've [written about the stack before](https://andochoa.com/journal/ai-os-for-one) — what it is, how it feels, why it works.

This is about the part I left out: what I actually spend my time on.

---

Last week I tried to run the first sprint for LocalKit — a new project, real product work. Scrape Google Maps for local businesses, generate template sites, build a lead pipeline. Simple enough.

It fell apart immediately.

Not because the agents couldn't code. They can code. The problem was they couldn't follow the workflow. The development process I'd been refining for months — the sprint planning, the review format, the quality gates — none of it was encoded in a way the agents could pick up on a new project. It lived in my head and in scattered config files that didn't travel.

So I stopped building LocalKit. And I spent the week building the system that would let LocalKit get built.

Sprint planning skills. A roadmap decomposition step. A review process that forces one feature at a time instead of letting agents drift. Quality checkpoints between every task, not just at the end. A bootstrap command that wires all of this up for new projects in one shot.

Fourteen PRs. Foundation work. Invisible.

Then, once the foundation was in place, LocalKit moved. The agents scraped leads, generated HTML templates, built a site generator. Real product. Real progress. But only because the invisible work came first.

---

Seventy percent of my time goes to infrastructure. Thirty percent to product. I'd love to flip that ratio. But every time I start building product, I uncover another gap in the foundation — and the urge to fix it right now is overwhelming. Not because I'm a perfectionist. Because I'm afraid if I don't fix it now, it'll get lost. The next session won't have the context. The agent won't remember why this matters. The learning will evaporate.

That's the hidden tax of working with AI agents. They don't forget because they're careless. They forget because that's the architecture. Every session starts fresh. Every context window fills up and compresses. Your institutional knowledge lives in files, not in people's heads — and if you don't write it down, codify it, encode it into the system, it vanishes.

So you write it down. You create an architecture decision. You refine a persona. You add a rule to the pre-push hook. You build a skill that encodes the workflow you just debugged.

None of this looks like building a product. All of it is required for products to get built.

---

The people in my X feed are shipping features. Showing demos. Posting revenue screenshots. And I'm here writing a formatting spec for how agents should structure their product requirements.

It doesn't look like progress. But I've seen what happens on the other side.

When the foundation holds, things move fast. Not "AI fast" — the breathless, demo-reel kind of fast that looks good in a tweet thread. Real fast. The kind where an agent picks up a task, follows the workflow, hits the QA gate, and ships a clean PR while I'm making coffee.

That moment — when the system works and you didn't have to babysit it — is the payoff. But getting there means spending days on work nobody will ever see.

---

Here's what I keep telling myself: this compounds.

Every rule I write makes the next sprint smoother. Every QA gate I encode catches a failure I'll never debug manually again. Every skill I build is a workflow I'll never have to explain twice. The thirty-seven architecture decisions in my log aren't bureaucracy — they're accumulated judgment that makes the system smarter each week.

But compounding takes time. And I don't feel like I have much time to spare.

That's the tension. I believe in the foundation. I see the evidence that it works. And I'm still anxious that I'm falling behind while building it. The market moves. Other builders ship. And I'm here, pouring concrete that nobody can see.

I don't have a resolution for this. I don't think there is one. It's the tax you pay for building a system instead of building a product. You accept the invisible work or you accept the fragile system. Pick one.

I picked foundations. Ask me in six months if it was the right bet.

Keep building. -Ochoa
