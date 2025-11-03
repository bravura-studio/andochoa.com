---
title: "TBM 369: Sources Of Truth"
source: "https://cutlefish.substack.com/p/tbm-369-sources-of-truth"
author:
  - "[[John Cutler]]"
published: 2025-07-27
created: 2025-11-03
description: "Most 'source of truth' problems in product development aren't really about the source of truth at all."
tags:
  - "world-view"
---
![](https://substackcdn.com/image/fetch/$s_!BSG7!,w_424,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdaeddecf-2de4-4f45-9307-065ba71e7611_1200x960.webp)

Most 'source of truth' problems in product development aren't really about the source of truth at all. They assume that everyone wants the truth, that they can agree on what truth they're seeking, and that they're willing to put in the work to forge coherence when there are different versions of the truth.

Let's explore this by way of example.

Your team has a list of initiatives. Some of those initiatives involve frequent releases. Some of those releases are visible to customers, while others are invisible or behind a feature flag. Some initiatives result in a marketing-supported launch, and those launches are assigned different tiers. Sometimes the relationship is 1:1 (initiative to launch), but sometimes the launch itself is a multi-phased initiative linked to the "phases" of the original initiative. In many cases, initiatives are selectively grouped into a launch. Not all initiatives result in a launch.

Meanwhile, your initiatives are linked to Epics, and you have a whole host of exceptions, like:

1. Some Epics are not linked to initiatives,
2. Sometimes the "end" of the initiative is linked to the completion of the last linked Epic, and sometimes not, and
3. In some cases, the relationship between Epics and Initiatives is 1:1.

Wait, there's more. The company chooses to understand allocation through multiple frames, including capex/opex, strategic pillars, market segments, new capabilities vs. optimizing existing capabilities, and strategic horizons. And throw in goals—some are delivery-based, some are outcome-based. Some are linked to Initiatives (the initiative came first, with the goal being added later). Some preceded the initiative (the goal inspired the initiative).

None of this is bad or wrong.

The variations mimic the wonderful (and helpful) complexity of product work. If you tried to standardize this and force everyone to use Jira the same way, run all launches the same way, etc., you'd either 1) force teams to work around you to do good work, or 2) end up negatively impacting outcomes.

But it presents a classic dilemma.

"We want to stop copy-pasting! We want to agree on our sources of truth!"

To fully capture all the relationships, exceptions, and frames of reference, you quickly end up with 20–30+ entities. Each one makes sense logically: Initiative, Release, Launch, Launch Milestone, Allocation Frame, Strategic Pillar, etc.

From a pure data-modeling perspective, this is "complicated but solvable." With enough junction tables, attributes, and relationships, you can model every nuance. Theoretically, I know this because I used to hack Coda to get close, and now I'm heading up product at a company that does this exceptionally well (happy to give you [a demo](https://www.dotwork.com/demo)).

However, say you do all that. Will anyone fill in all that data? Will they be able to navigate the various interfaces? What do you do about situations where MOST of the time X happens, but sometimes Y happens? Do you design an interface for all the exceptions? How will executives handle being shown the mirror of operational complexity?

Or will someone give in, throw up their hands, and start tacking countless custom fields onto the Initiatives table (to keep things "simple"), or pretend that an Epic means the same thing across 100 teams (when everyone knows that isn't the case)?

Or step back. What would people do with the "truth" of the mess?

1. One leader notices that their "strategic pillar" only accounts for 4% of the total investment, even though they've been arguing that it's a top priority.
2. Another leader realizes that 70% of "customer-visible" launches in their organization were feature-flagged and invisible, despite what they'd been reporting.
3. Executives recognize the significant inconsistency in the definition of "initiative" across teams, as well as the fact that some teams rarely close initiatives at all.
4. The head of marketing notices that half of the launches they're supporting aren't aligned with corporate messaging.

Which brings us to the crux.

Some companies hide the complexity of product work due to a lack of experience. They see product development as more mechanistic and "simple" than it is. Work moves in neat stages, definitions are consistent, and exceptions are just noise. At least that is how they picture it.

Some companies face a different pressure. They are struggling with numerous dependencies between parts of the organization. As a result, they have no choice but to impose a significant amount of standardization, even if it is not locally beneficial. It is the only way they can accomplish anything.

Other companies fully acknowledge the complexity. They see all the nuance and the exceptions. However, they then hit the wall of cognitive load. So they simplify, sometimes cutting away useful nuance, just to make forward progress.

And then there is another type of company entirely. In these companies, there is a knee-jerk reaction to anything that suggests things are harder than they appear. There is a veneer of simplicity, and any suggestion otherwise is quickly tamped down. These companies often reject nuance outright because it threatens the narrative of control and efficiency.

Back to our opening line:

> Most 'source of truth' problems in product development aren't really about the source of truth at all. They assume that everyone wants the truth, that they can agree on what truth they're seeking, and that they're willing to put in the work to forge coherence when there are different versions of the truth.

## Some questions to ponder:

- What reality is being most squashed down at your company, and why?
- Are there opportunities to surface more diverse truths instead of prematurely converging on a single truth?
- How does the way your tools and systems are set up reflect who is in charge and whose preferences dominate?
- Where are your teams doing the most exception handling or juggling between different versions of the truth? What are your sources of truth?
- Are there any low-hanging opportunities to minimize copy-pasting without forcing people to mash down reality?