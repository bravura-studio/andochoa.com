---
title: "TBM 377: Time Allocation ≠ Capacity Allocation"
source: "https://cutlefish.substack.com/p/tbm-377-time-allocation-capacity"
author:
  - "[[John Cutler]]"
published: 2025-09-05
created: 2025-11-03
description: "Spoiler: the concept of capacity allocation is fraught with misunderstanding, and companies waste a lot of money (and do a lot of damage) by mistaking time allocation for capacity allocation."
tags:
  - "world-view"
---
![](https://substackcdn.com/image/fetch/$s_!1fxK!,w_424,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F18d60643-eec3-4268-b19d-9866a1d66f8f_2607x1533.png)

***Before we jump in: September Conferences!***

*I’m heading to [Enterprise Tech Leadership Summit](https://members.itrevolution.com/etls25?utm_source=email&utm_medium=sponsor&utm_campaign=etls2025&utm_content=dotwork) in Las Vegas: September 23–25, 2025. I’m a huge fan of Gene Kim’s work and the community he has created. Dotwork is sponsoring, so I’ll be “working the booth.” Drop by if you’re around.*

*I’ll also be in Cleveland next week (9th and 10th) for [Industry](https://www.industryconference.com/). Would love to meet people in person.*

---

Lately, I’ve been researching the mental models, mechanisms, and reporting practices behind ‘capacity’ allocation. At the day-job I have to figure out how to walk a tightrope between what our customers ask for, and what will ultimately help companies.

***Spoiler: the concept of capacity allocation is fraught with misunderstanding, and companies waste a lot of money (and do a lot of damage) by mistaking time allocation for capacity allocation.***

The time-as-capacity mental model is straightforward: ‘Where do we put our time?’ Five people working 40 hours equals 200 hours to divide up. Go! You *allocate capacity* by deciding where to spend your time, and you report on capacity allocation by tagging the time spent by theme, bucket, category, etc.

**But capacity allocation is much more nuanced.**

A team (and the technology it relies on) holds a kind of potential energy that can be directed in different ways and shaped by context. From this perspective, capacity allocation is not about tallying hours, but about deciding and continually improving how we direct that energy.

This view has a strong foundation in lean manufacturing and the theory of constraints.

In a manufacturing context, capacity usually starts with the theoretical maximum output under ideal conditions (known as design capacity). But what matters more in practice is effective capacity, which takes into account factors like scheduled maintenance, breaks, supply chain delays, changeovers, quality checks, and staffing fluctuations.

Lines are also optimized for certain products, and shifting that mix can be costly. So if you asked, ‘Where did we allocate capacity?’ the answer would look less like counting hours and more like how we balanced product mix, changeovers, downtime, equipment availability, and demand fluctuations. Let’s be clear: there’s ALSO a strong emphasis on efficiency, analyzing how people spend their time and where that time gets wasted, but it is put in a broader context.

Here’s what is hard to explain to the well-meaning finance person slacking you with “I just need to know where we allocated our time/salaries in the last quarter!”

When you pay the salaries of a product team, you’re not just buying hours; you’re investing in a system. You’re funding the design, upkeep, and improvement of the ‘factory’ that produces outcomes. Who you hire, the scope and evolution of the team, how you build and maintain your codebase, how you mentor and train people, and the decisions made over the last three years all shape the team’s true capacity.

And importantly, capacity today is the result of past investments coming to bear. A stable codebase, good tooling, healthy team dynamics, and accumulated product knowledge make today’s work possible. Looking only at this quarter’s time allocation misses both the investments that built current capacity and the investments being made now to improve future capacity.

I’ve concluded that the only way to address this is to be very clear about the distinction.

**TIME allocation** is simply where the team invested its hours, or predictions about where those hours might go. That’s it. It tells us nothing about the quality of that investment.

**Capacity allocation** is a more nuanced discussion about the team’s true ability to deliver outcomes. It is shaped by interruptions, rework, dependencies, team composition, and the investments that build or erode long-term capacity.

Time is only one input. Capacity allocation considers the whole system.

Also, critically, you need to be honest! Most efforts to understand time allocation focus on only 1-3 of the categories below and call that “100%”:

- Dedicated Projects. Focused work on a defined project for weeks.
- Request Streams. Steady flow of repeatable requests.
- Streak of Stories. Small independent (releasable) tasks aligned to a bigger initiative.
- Firefighting / Stabilization. Fixes and incidents post-release.
- Maintenance / Upkeep. Routine system hygiene and fixes.
- Exploration / Spikes. Short research or experiments.
- “While You’re There”. Opportunistic cleanup during other work.
- Helping / Informing Others. Answering questions and unblocking peers.
- Customer Interaction. Research, support, or user contact.
- Meetings / Admin. Rituals and administrative overhead.
- Deployment / Release. Shipping software to production.
- Reviews. Feedback on code, designs, or docs.
- Tooling / Setup. Environment and pipeline setup.
- Context Switching / Waiting. Lost time from juggling or delays.

For example, on paper Irene was ‘allocated’ to a project for 80% of the week. In reality, much of her time vanished into waiting for CI/CD pipelines to run, wrestling with confusing code, interrupting others because of outdated documentation, struggling with her tooling and environment, and retraining her focus after constant low-level interruptions. As she put it, ‘Nowhere in the spreadsheet did I have an opportunity to tell people that those 30 theoretical hours were terribly ineffective.’

In another example I’ve shared often, these two teams in the same company had very, very different profiles in terms of actual time allocation.

![tweetfullsize_1204721911386624002_0.jpg](https://substackcdn.com/image/fetch/$s_!k0-D!,w_424,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe6d4067e-4d2b-4546-9d52-d8bf88dfa9a0_2048x1174.jpeg)

So, in short, after thinking about this for a while, I think the only real solution is to make a conscious effort to decouple time allocation from capacity allocation. Use different words. Then, and only then, can we start having honest discussions about impact, efficiency, and productivity.

Don’t say capacity allocation when you mean time allocation.

And when you start having honest discussions about impact, efficiency, and productivity, then outside of maybe high level breakdowns for accounting purposes, you start worrying way less about time allocation.