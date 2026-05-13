---
title: "Building the System That Builds the Company"
date: "2026-05-12"
type: wisdom
description: "I'm no longer building products. I'm building the system that builds them. It runs on a single server for $158 a month."
status: published
word_count: 2100
---

I'm a hoarder.

Not the physical kind. The knowledge kind. I read obsessively. I bookmark everything. I save threads, articles, repos, podcast timestamps — anything that sparks something. For years, all of it went into cold storage. Folders I'd never open again. Bookmarks I'd never revisit. A growing archive of things I found interesting but could never actually use.

That hoarding instinct is what started all of this. Not "I want to deploy AI agents." Not "I need an orchestration layer." Just: I have all this knowledge and no way to make it useful.

So I built knowledge vaults. Five of them, one per project. 6,800 documents, searchable via hybrid keyword and semantic retrieval. When I bookmark something on X at midnight, an automated workflow scores it with a local language model and routes it to the right vault. By morning, that knowledge is available to every agent in the system.

The cold storage became a living brain. The hoarding became useful.

And then, piece by piece, the rest of the system grew around it.

---

## The real problem

Here's what nobody in the "build your AI agent team" threads will tell you: the architecture wasn't the hard part. The hard part was time.

I have four products across three markets. I have kids. I have a life that pulls me away from the keyboard constantly. The quiet hours in front of the screen — the hours where real building happens — are rare and precious.

I felt the FOMO. I could see what other builders were doing. I could see what was possible. And I knew that if I could only build when I was physically at my desk, I'd never get there.

So the question became: how do I keep building even when I'm away from the keyboard?

The answer wasn't "work harder" or "wake up earlier." The answer was: build a system that compounds, learns, and evolves — so that building happens whether I'm at the desk or not.

---

## What it actually feels like

I text Ferro — my CEO agent — from my phone. Plain English. From the couch, from a café, wherever.

And it builds. Not toys. Not demos. Working software. Real systems. Actual improvements to real products.

That still feels magical. I won't pretend otherwise. You describe what you want in plain English and you get results. Sometimes it feels unreal. Is this actually happening?

But here's the thing about living inside two worlds at the same time.

When I'm inside the X tech bubble, I feel behind. Everyone seems further ahead. More agents, better setups, faster shipping. The pace is relentless and the FOMO is constant.

When I talk to people outside the bubble — friends, family, other founders in Portugal — I'm the weird guy living in the future. They look at me like I'm describing science fiction.

Two completely different realities. Both true simultaneously.

---

## The pattern nobody planned

Here's what's strange: at least three of us built the same architecture independently, without talking to each other, starting from completely different problems.

Elvis Sun builds a B2B SaaS alone. His orchestrator spawns coding agents, monitors progress, pings him on Telegram when PRs are ready. 94 commits in a day. He doesn't open his editor anymore.

A tech consultant in California — not a programmer, 43 years old — built a chief of staff system over a weekend. Six parallel agents handle his entire operational overhead. Cost beyond what he was already paying: maybe $10 a month.

And mine. A holding company with four products, run by agent teams coordinated through an open-source orchestration layer that models organizations, not pipelines.

Three different businesses. Three different skill levels. The same architecture every time:

**A coordination layer that holds business context. Specialized agents below it that hold task context. A knowledge system that feeds both. Humans at the top making decisions, not doing assembly.**

That's not a coincidence. That's a pattern. And the insight I keep coming back to is this:

You are no longer building the product or company. You are building the system that builds the product and company.

That shift changes everything.

---

## What the system actually is

Three layers, clear separation.

The CEO layer doesn't code. Ferro runs 24/7 on my VPS, connected to Telegram. It holds strategy, delegates work, tracks progress. When something breaks, it files a ticket, assigns it, and only escalates to me if I defined it as urgent. I set the rules for what "urgent" means. The system follows them.

The coding layer doesn't strategize. Each agent gets an isolated environment and a focused task. They write code, run tests, create PRs. They don't know about the other products. They don't need to.

The review layer doesn't build. Three AI reviewers check every PR from different angles. Nothing ships without passing all gates.

Underneath: Paperclip for org charts and task queues. n8n for workflow automation. Ollama running a local model for free inference. Caddy as reverse proxy. Systemd services that restart on failure.

The whole thing: a Hetzner VPS at €38, a Claude Max subscription at $100, and a Codex subscription at $20 that I'm thinking about cancelling. $158 a month. That's it.

---

## It is a craft

This is where the viral threads lie to you. "Build your AI agent team in a weekend." "Set up autonomous agents in 10 minutes."

No. It is a craft. There is no silver bullet, even for building these systems.

You read. You create. You test. You break. Rinse and repeat. This takes time. It takes patience. It takes the willingness to feel stupid when something that looked perfect on the surface turns out to be broken underneath.

Because LLMs sound too confident. That's the trap. Everything looks fine on the surface. The responses are articulate, the code compiles, the system reports green. And then three days later you discover it's been doing the wrong thing confidently the whole time.

You course correct. You build guardrails. You create rules and test whether they stick from one session to the next. Sometimes they hold. Sometimes the system changes underneath you and something breaks somewhere you didn't expect.

The system is always changing. That is the one constant.

I have an architecture decisions log with 31 entries. Each one is a failure that became a permanent rule. That log — not the code, not the agents, not the vaults — is the real product. It's the accumulated judgment about what works.

---

## The ceiling, honestly

Let me be honest about what doesn't work.

Knowledge compounds across sessions. Context doesn't. Every time an agent starts fresh, it rebuilds its understanding from configuration and knowledge vaults. It's like having a brilliant employee with amnesia who reads the manual every morning.

Agent coordination is still mostly manual orchestration. I define the flows, the handoffs, the escalation rules. The agents don't spontaneously decide to collaborate. They do what they're told to do, very well, within the boundaries I set. That's powerful, but it's not emergent intelligence. It's well-designed automation.

And I'm one VPS failure away from everything stopping. No redundancy. No failover. I know this is fragile. It's a tradeoff I've made deliberately because the cost of proper redundancy exceeds the cost of a few hours of downtime in a portfolio that's still pre-revenue.

When I look back at what the system has achieved, the leverage is obvious. It's at minimum a 10x. You can do things that were not possible before. Time compresses.

But somehow you still feel behind. You still feel the need to push harder and faster. The 10x is real and the urgency is real and they coexist.

---

## The shark

My kids will grow up in a world where all of this is normal. AI agents everywhere. Autonomous systems running everything. They won't remember a time before it.

What I want them to understand about this moment is simple:

We are all learning. We are all discovering. Nobody has the answers yet. The people who look like they're ahead? They're just in motion.

Be curious. Be sharp. Keep building. Keep moving. Don't stand still. Like the shark — if you stop, you die. The path forward reveals itself through motion, not through planning. If you stand still, you don't create the energy that propels you forward. You get left behind.

The system I built isn't impressive because of the technology. It's impressive because it moves. It compounds. It learns. It evolves. Every failure becomes a rule. Every rule makes it smarter. Every bookmark becomes knowledge. Every session builds on the last.

That's the OS. Not the servers, not the agents, not the vaults. The motion itself.

You can build it on a single server. I know because I did. And tomorrow it'll be different than it is today.

Keep building. -Ochoa
