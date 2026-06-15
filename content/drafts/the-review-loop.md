---
title: "The Review Loop"
date: "2026-06-15"
type: reflection
description: "My AI agent shipped 13 commits for a healthcare feature while I watched the World Cup. I didn't read a single line of code. Here's what I did instead."
status: draft
tags: ["agents", "build-in-public", "striva"]
---

Last week I wrote about PRD-0034. A full day writing ten implementation units for a dental booking calendar. Slot-intent suppression. Collision guards. 258 tests. For three dentists.

This week the agent took that spec and shipped it.

Thirteen commits. Nine sequential units. Interval collision guards backed by Postgres EXCLUDE constraints. Availability validation with warn-and-confirm flows. Cabinet attribution from roster shifts. Two rounds of code review feedback. Merged.

I was on the couch watching World Cup games.

---

Here's the part nobody talks about.

Lines of code I read: zero. Lines I skimmed: zero. Trust: one hundred percent.

That sounds insane. It's not. It's a system.

The agent ships a unit. I read the summary. Then I start asking questions. Not reading code — asking questions. Does this handle the case where a shift change happens mid-day? What happens if two receptionists drag-and-drop at the same time? Show me the migration. Why btree_gist and not a regular index?

The agent answers. I pressure-test the answers. When something feels off, I prompt it away. Asking is now almost free. So I ask a lot.

Then I throw a swarm of review agents at it. Adversarial checks. One looking for race conditions. Another checking if the API contract is tight. Another scanning for edge cases the first agent couldn't see because it was too deep in its own context.

The friction between a human and a swarm of agents produces better solutions, faster and cheaper, than friction between humans. Not because the agents are smarter. Because you can cover more ground. You can run five review loops in the time it takes to schedule one code review meeting.

When the review agents come back clean — or when the cost of another round isn't worth the marginal improvement — I commit. Not because I verified every line. Because I verified every assumption.

---

The sequencing wasn't mine. The agent figured out the order. U1: slot-overlap pre-scan. U2: interval collision guards. U3: uniform error contracts. All the way to U9: cabinet inheritance from attributed shifts.

My job was to question. Check every assumption. Make it come back with insights and recommendations. Then decide.

When U4 depended on something U2 got subtly wrong, I didn't debug it. I described the symptom. The agent traced it, proposed a fix, and I asked three more questions about the fix. Then I committed.

This is the loop. Spec → implement → question → review → fix → question → commit. The human slows down at the bookends. The machine sprints in the middle.

---

People ask me what my role is now. I used to write code. Then I wrote specs. Now I mostly ask questions.

That sounds like less. It's actually more. The questions carry the entire weight. A bad question wastes a loop. A good question catches a design flaw before it becomes a production bug. The skill isn't coding anymore. It's knowing what to ask and when to stop asking.

The next frontier is loop engineering — making the loop keep going so I touch the product development workflow even less. I just refine what I want. Product decisions. Taste. Craft.

Context switching is the worst. So when I'm in the zone — when the review agents are hot, when I've got the feature's shape loaded in my head — I keep pushing. More rounds. More improvements. Squeeze every insight out of the session before I lose the thread.

Then I go back to the couch. The World Cup is still on.

---

PRD-0034 was the audition. The spec that had to be right because my friends' trust was on the line.

The review loop was the performance. Thirteen commits, two days, zero lines read. Not because I don't care about the code. Because I found a better way to care about it.

She'll book an appointment and nothing will fight her. That hasn't changed. What changed is how we got there.

Keep building. -Ochoa
