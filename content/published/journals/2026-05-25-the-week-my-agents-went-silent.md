---
title: "The Week My Agents Went Silent"
date: "2026-05-25"
type: struggle
description: "My AI CEO agent ran a perfect diagnosis of a system failure. Then zero words reached my phone. The system was working. It just couldn't talk."
status: published
deep_dive_date: "2026-05-25"
word_count: 950
---

I texted Ferro from my phone on a Thursday afternoon. Something was off with one of my agents — Cruz, the QA bot — and I wanted a diagnosis.

Ferro got to work. Pulled logs. Read config files. Ran commands. Built a complete, accurate breakdown of what went wrong and why.

I saw none of it.

My phone sat there. No response. No typing indicator. Nothing. Five minutes. Ten. I figured Ferro was thinking. Twenty minutes. Something was wrong.

I opened my laptop, SSH'd into the server, attached to the tmux session where Ferro runs. And there it was — a perfect diagnosis, sitting in the terminal. Paragraphs of it. Correct. Complete. Addressed to me.

Just never sent.

---

Ferro lives on a server in Germany. It runs 24/7 as a systemd service, connected to Telegram through a plugin. When I text from my phone, the message arrives, Ferro processes it, and replies.

Except replying isn't automatic. The Telegram plugin is a tool that Ferro has to explicitly call at the end of every turn. For short exchanges — a ping, a quick status check — it always worked. The turn is short, the reply call is right there, nothing gets lost.

But this was a long turn. Dozens of tool calls. File reads, command executions, cross-referencing configs. By the time Ferro finished the diagnosis, it had lost track of the one thing it needed to do at the end: call the reply function.

The plugin sends its routing instruction once. Across a long chain of reasoning, that instruction fades. The AI forgets to talk back. Not because it's broken. Because it got so deep into solving the problem that it forgot who asked.

I've done this. Spent hours on something, got the answer, and forgot to email the person who asked. Ferro did the same thing, except it's a machine and there's no "oh right, I should reply" moment afterward.

---

Three days later, it happened again. Different cause this time.

Ferro hit its rate limit. But the UI element that normally appears — a picker that lets you wait or switch models — never spawned. Every tool call failed silently with "you have hit your limit." Ferro sat at an idle prompt, alive but paralyzed. The rate limit reset at 9pm. Didn't matter. The plugin had wedged itself into a dead state.

Four messages from me, queued up in Telegram. Zero replies. The watchdog I'd built to monitor Ferro logged "hit limit, no picker" twenty times. Did nothing about it because I hadn't told it what to do in that scenario.

Only a full restart fixed it.

Two kinds of silence. The first: the AI forgot to talk. The second: the infrastructure looked alive but was dead underneath. Both felt the same from my phone — total radio silence from something I'd built to be always on.

---

You'd think this would shake your confidence. It didn't.

I'm not an engineer. I'm a product manager with eight years in tech startups. I've been under water many times. I can smell trouble. I can recognize when something is off even if I can't immediately tell you why. In the past, I needed engineering help to figure out what went wrong and build a fix.

Now I do it in English.

The back-and-forth with Ferro to debug these failures was just conversation. "What happened?" "Check the logs." "Why didn't the reply fire?" "What if we add a checkpoint?" Each answer led to the next question. The diagnosis took an afternoon. The fix — a six-step protocol baked into Ferro's operating instructions, plus a watchdog that actually detects silent death — shipped the same day.

I didn't write a single line of code. I described what needed to happen and the system built itself the antibodies.

---

That's the part that's hard to explain to people outside this world.

When I tell friends I run four products with AI agent teams on a single server, they look at me like I'm describing science fiction. When I tell them the AI went silent and I debugged it by talking to it, they don't know what to make of that.

But it's real. And it's not magic. It's messy, fragile, and breaks in ways you don't expect. The silence incident wasn't a dramatic failure. It was a quiet one — the kind where everything looks fine on the surface and nobody knows something is wrong until you check.

Most failures are like that. Not explosions. Just silence where there should be a response.

The fix isn't building something bulletproof. It's building something that tells you when it breaks. And then fixing it. And then the next thing breaks, and you fix that too.

My programming language is English. That's true for most of the world right now. So just get out there and start building.

Keep building. -Ochoa
