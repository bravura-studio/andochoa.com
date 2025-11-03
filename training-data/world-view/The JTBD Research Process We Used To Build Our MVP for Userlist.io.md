---
title: "The JTBD Research Process We Used To Build Our MVP for Userlist.io"
source: "https://jtbd.info/the-jtbd-research-process-we-used-to-build-our-mvp-for-userlist-io-e300025ab487"
author:
  - "[[Claire Suellentrop]]"
published: 2018-04-27
created: 2025-11-03
description: "The JTBD Research Process We Used To Build Our MVP for Userlist.io When Jane Portman, Benedikt Deicke and I decided to join forces on Userlist.io, none of us wanted to start a company based on our …"
tags:
  - "world-view"
---
[Sitemap](https://jtbd.info/sitemap/sitemap.xml)

Get unlimited access to the best of Medium for less than $1/week.[Become a member](https://medium.com/plans?source=upgrade_membership---post_top_nav_upsell-----------------------------------------)

[

Become a member

](https://medium.com/plans?source=upgrade_membership---post_top_nav_upsell-----------------------------------------)## [Jobs to be Done](https://jtbd.info/?source=post_page---publication_nav-d5431658f1a6-e300025ab487---------------------------------------)

[![Jobs to be Done](https://miro.medium.com/v2/resize:fill:76:76/1*RGb8qUgoytdVNiVs4GZshw.png)](https://jtbd.info/?source=post_page---post_publication_sidebar-d5431658f1a6-e300025ab487---------------------------------------)

Managed by Alan Klement, [JTBD.info](http://jtbd.info/) is where JTBD practitioners share their experience, tools, and stories of using the theory of Jobs to be Done to become great at creating and selling products that people will buy. Everyone is welcome to submit a contribution.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*dnHiyuadBCBfjLwb.png)

When [Jane Portman](https://twitter.com/uibreakfast), [Benedikt Deicke](https://twitter.com/benediktdeicke) and I [decided to join forces](http://userlist.io/why-another-tool-for-saas-founders/?utm_source=jtbd-info&utm_medium=organic&utm_campaign=organic-promo) on Userlist.io, none of us wanted to start a company based on our personal experiences alone.

We’d each strongly felt the pains of trying to observe users’ behavior within a SaaS product, and communicate with those users at scale based on their individual behaviors. And we were excited at the prospect of building a **combined user admin panel + communication tool** to solve those pain points for other founders.

But we *weren’t* interested in joining the thousands of founders before us who’ve launched a product to scratch their own itch… and no one else’s.

So before Jane designed a single piece of our UI, and before Benedikt wrote a single line of code, I went into research mode to understand whether other self-funded founders experience the problems Jane and Benedikt faced when building their previous product.

**Here’s the 4-step process I used to gather the data, distill the important insights, and turn our findings into an MVP:**

1. Define our ideal customer
2. Conduct interviews to understand existing struggles
3. Organize interview transcripts to find insights
4. Build, test, learn

*This article* [*originally appeared*](https://userlist.io/customer-research-process?utm_source=jtbd-info&utm_medium=organic&utm_campaign=organic-promo) *on Userlist.io.*

## Step 1. Define our ideal customers

Defining your *ideal* customer means getting much more specific than saying you serve “SMBs” or “founders.” If you’re B2B, what company model does your ideal customer own or work in? What industry or niche? How mature is their business? Is it profitable? Well-funded? Lean? Rapidly expanding? What challenges do they face in doing their work well (or better)?

For us, defining our ideal customer was relatively easy, since Jane and Benedikt are already active members of the community they wanted to serve — and I have several friends who fit the mold, as well.

We knew we wanted to focus on founders of small-to-medium SaaS companies:

- …who are self-funded;
- …who are running their company completely solo;
- …or whose teams are small, and probably wearing many hats

My goal was to get at least 20 phone calls booked with folks who fit these criteria, and to conduct at least 10–15 actual calls. Booking at least 20 would help account for people who had technical difficulties, or had to cancel last minute.

While it would’ve been lovely to speak with 50 or even 100 ideal customers at this stage, our goal was to get just enough information to work with — those key details that would help us release an MVP, after which we could iterate and improve.

To my great appreciation, Jane and Benedikt sourced the majority of interviewees — mostly through their personal networks, Slack groups, and Twitter (a huge benefit of building a product for an audience you already know and interact with).

I set up a Calendly event called “Userlist.io Call,” shared that link with Jane and Benedikt, and watched as the calls rolled into my calendar. All in all, I ended up with 16 calls booked, and 12 actually held (after accounting for cancellations). Not bad!

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*IQgy39vsky_4UdKe.png)

My calendar, full of research calls for Userlist.io.

## Step 2. Conduct interviews to identify existing struggles

With 16 calls on the calendar, it was time to assemble some interview questions.

**What’s important: the questions I chose for these interviews were slightly different than the questions I’d use when speaking with paying customers of an existing product.**

The goal of these interviews *wasn’t* to decide on specific features to build, or even to get feedback on our idea. Instead, the goal was simply to understand:

1. What pains exist in our ideal customer’s day
2. What causes those pains
3. How those pains are currently solved… (or if they are solved at all)

Gaining this understanding would pull us out of the weeds of the problem we’d identified from our experience, and help us see more clearly whether it was the right problem to pursue, or whether a much bigger problem existed that was worth tackling.

This approach was, of course, based on Jobs To Be Done.

Since Userlist.io is a combined user admin panel + communication tool (for observing user behavior, then communicating at scale based on that behavior), I needed to understand:

- How do our ideal customers currently organize, observe, and leverage their users’ behavioral data?
- How do they communicate with users at scale, based on users’ behavior?
- Are their existing solutions perfectly fine? Or…
- Did we indeed have an opportunity to solve a pain point?

So I had to take each interviewee back in time, to the moments they made decisions about how they would accomplish these tasks.

Apart from confirming that interviewees met our ideal customer criteria (self-funded, running their company solo, or working with a very small team), we did very little pre-qualifying. **Our goal was to hear from founders at many different stages of company growth: problem-solution fit, product-market fit, growth, and scale.**

At the end of the process, our interviewees all fell into one of those first three stages: problem-solution fit, product-market fit, or growth. So…how were these founders observing their users’ behavior, and communicating with those users?

For the most part, the founders I spoke with were custom-building a user admin panel, which (of course) didn’t integrate with any communication tool directly. So to communicate with their users at scale, those founders had the following options available…

- Push user data from their product into a service like Drip or Intercom
- Send custom emails with something like Postmark or Sendgrid
- Manually keep track of new user signups, trial endings, etc., and send batch-send emails through their personal address every morning or evening (which sounds terrible)

Let’s say I was on a call with someone using a custom-built user admin panel plus Intercom.

**Here are some of the research questions I’d ask:**

- “Let’s go back to the point in time when you were working on your product, and you chose Intercom. Tell me about that.”
- “Did you consider any other solutions? Which ones?”
- “Okay, so you considered MailChimp and Drip. What happened that made you decide *not* to use MailChimp or Drip?”
- “What happened that eventually made you say, ‘Okay, Intercom is going to work for us’?”
- “Now that you’re in Intercom, what is working well? What are the pros?”
- “What’s still really painful at this point?”
- “Are there new problems that have popped up, or are there some problems that you thought Intercom was going to solve that it never actually solved for you? What are those?”

***\*\* By the way:*** Want the entire list of questions I used to run these customer interviews? [**Get all my interview questions + a spreadsheet template to organize your data.**](https://www.getdrip.com/forms/690487994/submissions/new) **\*\***

Essentially, I was trying to create *a mental timeline* of our ideal customers’ decision-making process:

- What events or situations led up to the problem we want to solve?
- How do people decide to solve that problem right now?
- What’s still not working about existing solutions?

Based on interviewees’ emotional reactions to their current ways of observing and communicating with users, it was clear we were on to *something*.

**Here are just a few of the ways founders described the problems with their existing solutions:**

> “The problem with every custom built system is that every time you need to tweak something, you’re too lazy to go actually code something to make a change. You have no time for that.”
> 
> “When you start out as a bootstrapped founder…at least, when I did…I didn’t know how to get enough user data to understand how people were really using the product, and what features I still needed to build to get to product-market fit. There’s this concept of a ‘minimum path to awesome,’ but how do you figure out what that path is, when you’re in the really early days and you don’t have very many customers?”
> 
> “For my last product, all my emails were custom and they’d go through Mandrill. I definitely don’t want to do that for this new product, because it’s not efficient to code emails, and there’s no way to keep track of them or see how they performs.”
> 
> “What I love about Intercom is the user dashboard. It’s like an admin panel, and one thing that’s painful about having your own product is that you need to have that admin panel. But Intercom’s dashboard is too limited. Intercom is a generalist, so all their different features are just…okay. They’re not really strong in any one category.”

I recorded every call, which allowed me to give each interviewee my full attention, and then uploaded each recording to Rev.com. In 24 hours or less, I’d have the transcript back — and with 12 calls complete, I was ready to settle in for a month of deep data review.

## Step 3. Organize raw transcripts into meaningful data

Based on the conversations held with these 12 founders (plus one [audio rant](https://soundcloud.com/user-539369312/asasw1) Amy Hoy recorded and published, which happened to be extremely timely and relevant to us), we could’ve started building our MVP with 25 different features. Different people needed different things, at all different levels of urgency.

So, how did we figure out what mattered most?

By distilling dozens of pages of qualitative data into… a very unsexy spreadsheet. Below are the three questions I used to organize our data.

### Question 1. Are enough people motivated to solve this pain? Or is there a stronger pain somewhere else?

The first step was to make a list of all the various pain points interviewees had shared during calls. My goal was to identify which pain points interviewees were *most often* motivated to solve, and which pain points could be excluded as edge cases.

Here are just a few motivations our ideal customers felt, color coded by which came up most frequently during interviews (dark red = came up most often, dark blue = came up least often):

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*K9z71z5rQr3w0mIJ.png)

A few motivations our ideal customers felt, color coded by which came up most frequently during interviews (dark red = came up most often, dark blue = came up least often)

As you can see, many interviewees wanted to improve how well they guided users through their product — which validated that the pain point Jane, Benedikt and I are trying to solve is real, and commonly felt by our ideal customers.

While the blue problems are no less legitimate (or important to a successful business) than the dark red, relatively few founders in our sample size were as concerned about the blue problems as they were about the red.

With validation that the pain point we’re trying to solve — *“I want to nudge users to use the product in a way that makes them successful”* — is real and widely-felt, we could safely narrow our focus to just this pain point, and ignore the others for now.

Now, I was ready to figure out:

- What events / situations most often trigger this pain?
- What’s the “better life” founders envision for themselves as they try various solutions?

### Question 2. What common events or situations trigger this pain point?

Next, we needed to figure out which events or situations were occurring in founders’ workflows, that most frequently *cause* this pain point to arise. This would help us understand what events along a founder’s journey would most likely trigger that founder to seek out (and adopt) a new solution.

Remember: during my interviews with founders, I was trying to create a mental timeline of each founder’s decision-process. So I reviewed the transcripts in which our chosen pain point came up frequently, and looked for patterns in those founders’ stories.

**Some of the common situations that pushed founders to worry about properly communicating with their users:**

- Trying to quickly ship an MVP, and reserving all possible time/energy for building core product features (as opposed to spending time on “extracurricular” marketing and communication)
- Trying to implement an analytics tool to understand user behavior, but getting overwhelmed by the process, not knowing what to measure, or having insufficient data to understand which user behaviors lead to subscriptions vs. which lead to churn
- Wanting to switch from time-triggered customer communication to event-triggered communication
- Wanting to send product updates, but only to a certain segment of users (those who would care the most)
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*kcE1iUadv0vWncvj.png)

Red: situations that cause founders pain (“struggling moments”). Orange: motivating factors pushing founders to seek a new solution. Green: desired outcome, and existing solutions for achieving that outcome.

**Some key learnings we took away from this:**

1. If we get our product on founders’ radar while they’re still in ideation phase, before they’ve begun building their product, we could save people TONS of time/effort — which many of them are currently spending building admin panels by hand
2. If we provide foundational analytics about user behavior, founders may never need to bother with bulky analytics tools designed for much larger, mature companies. On the other hand, if they’re already a power-user of a tool like KISSmetrics or Mixpanel, they may not be a fit for Userlist.io.
3. Even founders who de-prioritize user communication in the early days of their product (e.g. in favor of concierge onboarding) will eventually want to optimize the messages they send to users. If we can help a founder publish their first basic time-based onboarding email, then collect user data in the background for a while, that founder will have everything they need to send super-effective event-based emails down the road.

**This was helpful not just for early product development, but from a marketing and overall business perspective, as well.**

For example, we know we’ll need to make founders aware of Userlist.io extremely early on in their product-building journey — otherwise, we could miss the boat, and they’ll become too comfortable with a homegrown user admin panel + other email solution… and both of these require lots of effort to migrate away from.

With these learnings in mind, we were ready to examine the existing solutions founders use in these situations.

*\*\*Sidenote. Some of the founders I interviewed expressed* ***no*** *pain points related to building their own user admin panel, and actually preferred to build as much as possible by hand — including emails, analytics tools, etc. We chose to exclude data from interviews with these founders, intentionally creating a sampling bias.*

*While we recognize some founders may never see the value of a done-for-you tool, we believe — based on the quantity of founders who* ***did*** *want to avoid hand-coding everything — that a healthy percentage will!*

### Question 3. What existing solutions do we not want to compete with?

We know the customer communication space is a large one, and believe many competitive solutions can co-exist. However, we wanted to avoid going up directly against the clearly incumbent products that it would be most difficult to pull users away from.

That meant analyzing the feature sets of solutions founders currently use, figuring out what founders love and hate about those solutions, and being *extremely* selective about which features our MVP would include.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*VJPMFLiv3oWJr3PX.jpg)

Frustrations our ideal customers feel with custom-coding emails to users.

Ultimately, we decided *not* to focus on…

- *Pre-signup marketing communications.* With umpteen email marketing tools already available, we’re not interested in building yet another way for people to capture leads outside of their products, and nurture those leads into trials.However, many founders currently force pre-signup marketing tools (e.g., Mailchimp, Drip) into their users’ post-signup experience, with much frustration — and we’re very interested in solving that problem.
- *Robust analytics.* There’s no way we can (or want to) compete with powerful analytic tools like KISSmetrics, Mixpanel, or FullStory. Our ultimate goal is to create a tool that sends relevant messages well, so our analytics features will most likely be “necessary and sufficient” to provide quality event triggers.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*or9LOiimsPZs-dZT.jpg)

Frustrations our ideal customers feel with existing analytics tools.

***\*\* By the way:*** Want a copy of this spreadsheet I used to sort our customer data? [**Get all my interview questions + this spreadsheet template above to organize your data.**](https://www.getdrip.com/forms/690487994/submissions/new) **\*\***

## Step 4. Build, test & learn

We’re extremely close to launching our MVP, and we can’t wait to invite folks in. Feedback from our first users will help us validate — or rethink — whether Userlist.io has the right mix of core features to truly deliver value.

Even at this early stage, though, we’re hopeful that our focus on founders’ most common situations, struggles, and motivations leads to a product that makes self-funding a SaaS company 10x easier.

## Get your free research templates

Want a copy of the interview questions & spreadsheet template I used for Userlist.io’s customer research? [**Get both here.**](https://www.getdrip.com/forms/690487994/submissions/new)

[*Claire Suellentrop*](https://twitter.com/clairesuellen) *is the co-founder + head of marketing at* [*Userlist.io*](http://userlist.io/)*, alongside Jane Portman and Benedikt Deicke. Previously, consulted on customer insights and marketing for Wistia, MeetEdgar, Death to the Stock Photo, and many other fun SaaS companies.*

*Before jumping into the world of consulting and co-founding, Claire was Director of Marketing and #2 employee at Calendly.*

[![Jobs to be Done](https://miro.medium.com/v2/resize:fill:96:96/1*RGb8qUgoytdVNiVs4GZshw.png)](https://jtbd.info/?source=post_page---post_publication_info--e300025ab487---------------------------------------)

[![Jobs to be Done](https://miro.medium.com/v2/resize:fill:128:128/1*RGb8qUgoytdVNiVs4GZshw.png)](https://jtbd.info/?source=post_page---post_publication_info--e300025ab487---------------------------------------)

[Last published Feb 18, 2021](https://jtbd.info/getting-started-with-jobs-to-be-done-e73bbfae0c3c?source=post_page---post_publication_info--e300025ab487---------------------------------------)

Managed by Alan Klement, [JTBD.info](http://jtbd.info/) is where JTBD practitioners share their experience, tools, and stories of using the theory of Jobs to be Done to become great at creating and selling products that people will buy. Everyone is welcome to submit a contribution.

SaaS Marketing & Growth Advisor. Co-Founder, [ForgetTheFunnel.com](http://forgetthefunnel.com/)

## More from Claire Suellentrop and Jobs to be Done

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--e300025ab487---------------------------------------)