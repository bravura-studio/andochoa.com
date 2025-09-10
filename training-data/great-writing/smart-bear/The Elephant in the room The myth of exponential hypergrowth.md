---
title: "The Elephant in the room: The myth of exponential hypergrowth"
source: "https://longform.asmartbear.com/exponential-growth/"
author:
  - "[[Jason Cohen]]"
published: 2022-03-05
created: 2025-09-10
description: "Even Facebook and Slack did not grow \"exponentially,\" as frequently described. Here is the correct model that you can use to understand and affect growth."
tags:
  - "smart-bear"
---
by Jason Cohen on March 5, 2022

Even Facebook and Slack did not grow “exponentially,” as frequently described. Here is the correct model that you can use to understand and affect growth.

A startup is growing fast, the journalists marveling at its “meteoric rise.” But don’t meteors fall?

Inevitably it is breathlessly inducted into the class of “hypergrowth” companies that are “growing exponentially.” Especially when the product is “viral.” After all, if every person brings three friends, and each of those brings another three, is that not exponential?

But “exponential” is an incorrect characterization, as we’ll see in real-world data, even for hypergrowth, “viral” companies like Facebook and Slack.

This article suggests an alternate model for how fast-growing companies actually grow. Understanding the model is useful not only for predicting growth, but because understanding the foundational drivers of growth allows us to take smarter actions to create growth in our own companies.

## Dispelling “exponential”

To evaluate whether hypergrowth is properly described as “exponential,” let’s recall what that word means. Here’s an exponential curve (like ), compared to a quadratic one (like ):

**Figure 1**

In exponential growth, values grow by a *multiple*. For example: In year 1 you grow 10, in year 2 by 100, in year 3 by 1000⁠—each time the amount of growth is *multiplied* by ten. The compounding effect of multiplication causes the numbers to grow slowly initially, then skyrocket. The compounding effect gets journalists and VCs justifiably excited.

> Compound interest is the most powerful force in the universe.  
> —Albert Einstein

In quadratic growth, values grow by a *adding* a constant amount more each time-interval, rather than *multiplying* a constant amount more each time-interval. In the same example, growing in year 1 by 10, then in year 2 by 20, in year 3 by 30:

**Figure 2**: Successive values (in blue) are increasing more and more (in green). The green differences are increasing linearly: 10, 20, 30.

Growth is still *accelerating*, so the blue curve slopes upwards, but gently compared to exponential growth.

With these patterns in mind, let’s examine real-world data, and see whether “exponential” is the right model.

---

**Facebook** is the definition of hypergrowth⁠—getting to $50B in revenue [faster](https://www.bnnbloomberg.ca/how-facebook-became-one-of-the-fastest-growing-companies-in-u-s-history-1.1213047?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post) than any company in history. The product is “viral”⁠—friends bring other friends⁠—which theoretically leads to “exponential growth.” But Facebook didn’t grow exponentially in the number of monthly active users:

**Figure 3**: Essentially linear for nearly twenty years, only exponential in the first four years.

**Slack** was [the fastest-growing enterprise software company ever](https://www.forbes.com/sites/johnkoetsier/2018/11/30/how-slack-became-the-fastest-growing-enterprise-software-ever?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post), going from $0 to $10M ARR in their first 10 months, and 0 to 10,000,000 active users in just five years. It’s also a “viral” product⁠—organizations invite their members, who then create their own Slack-groups and invite others. So surely Slack has exponential growth? (Figure 4)

**Figure 4**: Slack’s [own data](https://slack.com/blog/news/work-is-fueled-by-true-engagement?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post) shows initial quadratic growth, followed by years of linear growth.

If you compare Slack’s growth with **Microsoft Team** ’s growth, do you still think Slack’s growth is “exponential?” (Figure 5)

[source](https://www.bemopro.com/cybersecurity-blog/slack-vs.-teams?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 5**

**Dropbox** was another “hypergrowth” company, achieving 100,000,000 registered users five years after being founded in 2007, but it wasn’t exponential, neither in freemium users nor in revenue, early nor later in life (Figure 6) (Figure 7).

[source](https://www.investx.com/deals/dropbox/growth-strategy?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 6**: Early in life, Dropbox registered users grows non-exponentially, nearly exactly 100M per year

[source](https://saasscout.com/statistics/dropbox-statistics/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 7**: Later in life, Dropbox revenue grows linearly, and slows down

**Trello** grew fast too, getting to 10,000,000 registered users in three years. But not exponentially:

[source](https://medium.com/@hnshah/why-trello-failed-to-build-a-1-billion-business-e1579511d5dc?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 8**

Lyft grew in part due to “network effects” according to [their S1](https://www.sec.gov/Archives/edgar/data/1759509/000119312519059849/d633517ds1.htm?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post), but this chart they presented shows that active rider growth isn’t exponential:

**Figure 9**

**HubSpot** ’s revenue curve is astonishingly consistent, despite hitting multiple inflection points <sup>1</sup> in their business:

> <sup>1</sup> e.g. launching new business models like selling through agencies instead of only directly, launching new product lines like sales CRM on top of marketing automation tools, and scaling the number of customers and employees by 10x

[source](https://www.hubspot.com/hubfs/Investor%20Presentation%20Q121%20%281%29.pdf?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 10**

Analyzing this last example, we arrive at a new, non-exponential model.

## Hypergrowth is quadratic

The language we use [can determine](https://en.m.wikipedia.org/wiki/Linguistic_relativity?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post) the thoughts we have.

The HubSpot slide says “41% CAGR.” “CAGR” means annualized growth rate. They’re saying that if you start with the first number on the slide, then from there plot growing 41% per each year, compounding each year upon the previous, for seven years, you would arrive at the last number on the slide. This is exactly the definition of “exponential”⁠—multiplying by a number repeatedly. In general when you use “CAGR” or “percentage growth” as a metric, you are implicitly saying “This is an exponential process.”

But HubSpot didn’t grow by 41% every year; in this time frame, it started at 60% and ended around 30%:

**Figure 11**: Exponential curves have a *constant* year-over-year growth rate, therefore this is *not* exponential growth.

If instead we examine growth in absolute dollars, rather than in percent, a pattern emerges. In the first set of four quarters on this report, they grew $17M. The next set grew $23M. Then $28M. Then $34M. Each year $5-7M more than the previous. This is the definition of a quadratic⁠— *adding* an amount that increases by a constant amount each period, not *multiplying*.

Charting these year-over-year revenue differences *in absolute dollars* rather than *in percent*, it’s clear that indeed the changes were almost completely linear for years, then suddenly changed in 2020 <sup>2</sup> to a new (but still linear) rate:

> <sup>2</sup> Coinciding with the launch of a new product: HubSpot CMS Hub.

**Figure 12**

It is therefore mathematically inevitable that plotting a quadratic curve (rather than exponential) on top of HubSpot’s revenue data will be a perfect fit:

**Figure 13**: When you said “best-fit,” you weren’t kidding!

My thesis is that \*\*High-growth companies grow quadratically, not exponentially.\*\* <sup>3</sup>

> <sup>3</sup> My guess is low-growth companies are similar, but data are more easily available for the runaway-growth companies who publicly flaunt their success.

The consequence of this conclusion is important for operators and analysis and investors. These are all people trying to understand⁠—and possibly change⁠—growth drivers. Getting the right language, and the right model, will lead to right analysis, and right action.

It’s not enough to draw best-fit lines on top of PowerPoint slides. We have to explain *why* this model makes sense, which in turn will create a better understanding of the growth drivers in our own companies.

We’ve been taking a macro view of growth, looking at multi-year trajectories. Now we’ll peer into the microscope instead of the telescope, and consider how growth arises from a single marketing campaign.

In my experience, marketing campaigns follow this pattern:

**Figure 14**

At the foot of the curve, we’ve launched a new campaign, but it’s ineffective; we haven’t figured out the best design and messaging and calls-to-action for this new medium and audience. Sometimes we never figure it out, and abandon the effort.<sup>4</sup>

> <sup>4</sup> It’s hard to distinguish (a) our failure to build effective copy and conversion funnels from (b) channels that are fundamentally a bad fit for our market or product. This uncertainty, together with the rapid evolution of digital marketing, suggests that we should retry campaigns in previously-failed channels every few years.

But in the case that we unlock the secret of efficacy, the campaign rapidly reaches a natural level of contribution; in this example, a number of “sales per week.” The specific level depends on many things: ad inventory, our budget, audience-receptivity, and the consonance between the audience and our target market.

Next we enter the optimization phase. We A/B Test our way to incrementally better results. Also we enjoy the result of multiple exposures⁠—most people need to see the ad more than once before they act.

Finally we enter a phase of decline. There are various causes, all instructive:

- **The audience saturates.** Everyone in the channel has seen the ad more times than is required to act; it’s now falling on deaf ears. Even if the audience is growing, the number of new people is small compared to the number of people that were new-to-us when we began the campaign.
- **The channel declines.** A media site that was popular loses readers through over-monetization. An event that was well-attended loses favor. A newsletter that was frequent and insightful becomes less frequent or other writers take over. A podcast moves to a closed platform and loses many listeners.
- **The auction becomes uneconomical.** For auction-based systems like Google and Facebook advertisements, or other [zero-sum](https://longform.asmartbear.com/startup-beats-incumbent/) programs like affiliates or limited-inventory spots on newsletters or podcasts, the winner is the one who will pay the most. What is cost-effective for one bidder will be laughably overpriced for another, due to better conversion rates, higher revenue per customer, higher profitability per customer, or due to categorization as a “loss leader” or other way of ascribing value beyond immediate pay-back.

This curve leads to actionable ideas for managing marketing (given at the end of this article), but also forms my central thesis about how all sorts of growth works at companies. So I’m giving it a name:

**Figure 15**

The model above shows the number of sales *per week* the campaign contributes. To understand how this looks in terms of revenue growth, let us suppose a simple business model in which all sales are for a recurring revenue product generating $10 per month, with a 1% per month cancellation rate. Revenue grows over time in a certain way:

**Figure 16**

Growth initially accelerates as the campaign is solved, then grows roughly linearly as the campaign is optimized, and then starts sagging (although still growing!) as the campaign declines, and as the now-sizable customer base produces a non-trivial number of cancellations.

### The layer-cake of quadratic growth

Marketing departments don’t stop at a single campaign. They add new ones. Some are bigger than others, some can be optimized more than others, some decline sooner than others, some decline more precipitously than others.

So, let’s model that: A variety of Elephant Curves, with differing parameters, beginning at different times, stacking the revenue-contribution of each to arrive at overall revenue growth for the company:

**Figure 17**: Layered campaigns create a “wavy quadratic.”

Scan your eye across the top of this kaleidoscopic cake, and you trace a wavy quadratic. This makes sense mathematically, because each campaign is essentially linear after it gets going, even if it sags during decline. “Adding more linear things over time” is the definition of a quadratic.

The reason it’s “wavy,” is that when we unlock a new campaign we get a burst of growth. Do real-life revenue curves exhibit this waviness? Maybe so; here’s another slide from the HubSpot deck:

[source](https://www.hubspot.com/hubfs/Investor%20Presentation%20Q121%20%281%29.pdf?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 18**

HubSpot didn’t just add new marketing channels, however, but also layered on new geographies and new products. Do those activities have the same effect as marketing campaigns?

So far we’ve assumed a single product, driven by marketing campaigns. High-growth companies who want to continue growing quickly after their first product reaches scale, must launch new products into new markets.

Is the Elephant Curve also the shape of an entire product line? After all, products often have an initial slow-growth period (because only cutting-edge early adopters are eager to pay to “be first” with bugs and missing features), followed by a faster expansion period, then reach some sort of natural ceiling, and possibly enter a period of decline (as the market evolves or competition overwhelms).

Indeed, this is what we see with many products, especially those that are marketing-driven, and without recurring-revenue. iPod sales, for example, are a perfect match:

[source](https://www.huffpost.com/entry/ipod-sales_n_4680000?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 19**

It should therefore be unsurprising when we look at the overall revenue chart for Apple, and once again see quadratic growth on the top-line, admittedly with a special one-time bump for the unprecedented <sup>5</sup> success of the iPhone:

> <sup>5</sup> It is rare for a second product to dramatically outpace the first; even juggernauts like Google, Amazon, and Facebook never achieved that.

[source](https://www.statista.com/chart/17862/apples-annual-revenue-by-operating-segment/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 20**

Each product is in a different phase of its lifecycle: The iPod declined to zero, the iPad is still declining; Macs are teetering but essentially flat; iPhones and software services are still increasing.

### The quadratic explanation for “growth decay”

It’s well-known that growth⁠—as a percentage⁠—naturally declines with scale, even when there’s nothing wrong with the company.

This law of nature has been given a name: Growth Decay (or sometimes Growth Persistence). Because of the traditional insistence of talking about growth as a percentage, the concept is articulated this way: If a company grew X% last year, it’s likely to grow a bit less than X% this year. With this formulation, the question becomes: How much less?

The data give us the answer of 85%, although with , this is a tendency but far from a law:

[source](https://www.scalevp.com/blog/predictable-growth-decay-in-saas-companies?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 21**

With our new appreciation that growth isn’t exponential, and therefore “percentage” might be the wrong way to characterize growth, we could ask what curve would best model the idea of Growth Decay? Specifically, let’s plot revenue for an initially-fast-growing company that is subject to the principle of Growth Decay:

**Figure 22**

The first sixteen years of the curve is quadratic. While mathematically not identical, the best-fit quadratic curve <sup>6</sup> has a staggering .

> <sup>6</sup> when fit perfectly; interestingly this is very close to , showing how simple the curve really is.

This is yet another signal that quadratic growth is the correct model.

But some products really do grow exponentially. In theory.

In theory, theory and practice are the same. In practice, they’re not.<sup>7</sup>

> <sup>7</sup> This phrase attributed to Benjamin Brewster.

Some products don’t grow proportionally with marketing and sales, but instead self-propel with a mechanism that theoretically ought to be exponential. There are at least three ways for this to happen:

**Type 1: Virality**

When each user invites on average another users, then each of *those* new users bring in *another* new users, so we end up with more. Then each of *those* brings in another which yields . Then and so on; this is the definition of exponential growth. Biological viruses grow exponentially for a similar reason, justifying the label.  
  
*Examples:* social media, chat clients, peer-to-peer payment platforms, massively-multi-player games, fantasy sports leagues.

**Type 2: Word-of-Mouth**

All products have some word-of-mouth component, but here we’re referring to products that are *primarily* driven this way; this creates a growth process that is similar to viral. Typically the mechanism of “telling others” is built into the product, rather than bolted on by marketing or generated by goodwill. The difference between “word-of-mouth” and “viral,” is that viral products are *unusable* unless you invite others to become users (thus exponential growth is enforced) whereas word-of-mouth products *encourage* sharing. Thus chat clients are viral because without inviting others you can’t chat, whereas Wordle <sup>8</sup> was word-of-mouth, because you play the game alone, but are encouraged to share results on Twitter, which in turn brings in new users.  
  
*Examples:* gamified products that generate significant sharing (self-improvement, game-results), consumer-to-consumer marketplaces where being a buyer plants the idea of becoming a seller (eBay, Airbnb, Uber); organizations with a cause that creates on-going buzz (brazenly unique cultures, a passionate higher purpose, something people feel is linked to their personal identity).

**Type 3: Hot Trend**

Products that “everyone” (in some well-defined market) is going to buy. For smartphones, that might be half the population of the world. For internet search, that might be 100% of the online world. For backend management systems for large hospital chains, that could be 1000 potential customers. These products hit “tipping points” where “suddenly everyone buys it.” Even if, like internet search, the product has no explicitly viral nor word-of-mouth component⁠—when you search on Google, you don’t “invite friends” to also search on Google⁠—the ubiquity and inevitability of the trend leads to an explosion of users.  
  
*Examples:* word-processing, spreadsheets, broadband internet, the smartphone, the shifts to cloud computing and online shopping, major media delivery platforms of radio, TV, DVD, and video streaming.

> <sup>8</sup> Wordle [exploded](https://www.theguardian.com/games/2022/jan/11/wordle-creator-overwhelmed-by-global-success-of-hit-puzzle?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post) from 90 players in November 2021, to 300,000 in December, to 2,000,000 in January, when it was [bought](https://www.nytimes.com/2022/01/31/business/media/new-york-times-wordle.html?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post) by the New York Times.

### Logistic growth: Nearly the right model for virality

Products cannot grow forever, for the obvious reason that markets are finite. The Facebook virus spread to billions of people, but not infinite. Smartphones have been purchased by billions of people, but not infinite.

Therefore, even if “exponential” is the correct model for the core growth mechanism of the product, it nevertheless cannot continue growing exponentially because it runs out of market. Furthermore, markets tend to have so-called “low-hanging fruit”⁠—customers who are more eager to buy⁠—so although the virus spreads exponentially through these easy-pickings, it runs into the majority of people who will buy, but maybe later, maybe after more of their friends or competitors are using it, maybe if it’s less expensive, maybe once it has more features, maybe once it supports integration with specific other software, and all manner of other excuses. The virus has more trouble infecting these high-strung fruits, so growth slows.

This suggests a curve that starts exponentially, but then slows as it runs into the soft back-pressure of more demanding customers, and finally flattens out completely as it runs into the hard limit of the size of the addressable market.

Biologists have already done the work for us, because this is the correct model not just for viral products, but biological viruses infecting a population⁠—akin to product types 1 and 2 above. Intriguingly, this is also the correct model <sup>9</sup> for the diffusion of a gas across a membrane⁠—akin to product type 3. The mathematical model for all of these processes is the logistic curve:

> <sup>9</sup> The similarity is that in both cases you have a sudden demand that enters into a new space, but which slows and eventually stops as the new space becomes saturated.

**Figure 23**

The logistic curve *is* exponential in the early days when it is far away from its natural limit. As the product (or gas or virus) gets to around 25% market penetration (or infections or saturation), the curve flattens into linear growth, in a tension between the exponential force of growth, countered by fewer and more demanding remaining targets. Finally it levels out at what is called the “carrying capacity”⁠—the fully-saturated market.

The logistic curve is evident in the real world, in all three product types: (Figure 24) (Figure 25) (Figure 26) (Figure 27) (Figure 28) (Figure 29) (Figure 30)

[source](https://www.statista.com/statistics/274564/monthly-active-twitter-users-in-the-united-states/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 24**: Twitter is a type 1 “Viral” product that follows the logistic model

[source](https://www.statista.com/statistics/274564/monthly-active-twitter-users-in-the-united-states/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 25**: Pinterest is a type 1 “Viral” product that follows the logistic model

[source](https://www.businessofapps.com/data/ebay-statistics/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 26**: eBay is a type 2 “Word-of-mouth” in the number of buyers, following the logistic model (though also sagging towards the end, reminiscent of the Elephant Curve)

**Figure 27**: eBay also follows the logistic model in the number of sellers (with even more pronounced sagging)

[source](https://www.statista.com/statistics/266219/global-smartphone-sales-since-1st-quarter-2009-by-operating-system/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 28**: Smartphones are a type 3 “Hot Trend” that follows the logistic model all the way to saturation

[source](https://gs.statcounter.com/platform-market-share/desktop-mobile/worldwide/#monthly-200901-202202?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 29**: Smartphone *usage*, separate from smartphone *sales*, is also logistic. Many pundits predicted this percentage would grow nearly without bound; in fact it saturated at 55%.

**Figure 30**: The internet is a type 3 “Hot Trend” product with a near-exact logistic shape; at 66% global penetration, it hasn’t reached carrying-capacity, but it’s been in its linear mode for many years, and fell off the exponential path sooner than you might have expected

### Stacking logistic growth: The quadratic reappears

Marketing-driven products demonstrated quadratic growth, especially once Elephant-shaped campaigns and products were stacked. How does this differ with logistic growth?

As already pointed out, logistic growth is similar to the Elephant Curve. The “high growth” portion of a marketing campaign might in fact be logistic; a product might extend that period into years rather than weeks, and the absolute magnitude of the result might be many times larger.

If this idea is correct, we ought to see viral-like products exhibit a similar curve to the iPod curve⁠—i.e. a product with initially-exponential growth, then a flattening, perhaps with some small growth, then on a long-enough timeline, a decline. An Elephant with a more stretched-out trunk.

The Facebook Messenger product appears to exhibit at least the first half of the logistic curve:

[source](https://www.businessinsider.com/how-facebook-plans-to-improve-messenger-in-2018-1?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 31**

Furthermore, this curve is actually a sum of US growth and outside-US growth. Looking only inside the US, Facebook Messenger is further along the curve, past the linear midsection and already leveling out near some carrying-capacity:

**Figure 32**

The same thing happens with Facebook DAUs and MAUs.<sup>10</sup> DAUs in the United States and Canada are logistical and have already topped-out at an apparent natural carrying-capacity of 185 million:

> <sup>10</sup> Daily Active Users, Monthly Active Users

[source](https://www.vox.com/2018/1/31/16957122/facebook-daily-active-user-decline-us-canda-q4-earnings-2018?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 33**

Breaking out MAUs by all geographies reveals that top-line growth of users is an aggregate of some geographies essentially not growing at all (late in the curve), while others are still growing, albeit also linearly (middle of the curve):

[source](https://www.digitalinformationworld.com/2020/01/facebook-q4-2019-1657-million-dau-2498-million-mau.html?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 34**

The result of these individual effects of different products, released at different times, in different geographies, each with a “marketing campaign” style growth curve, is that it adds up to linear growth:

**Figure 35**: Exponential growth for the first few years crashes down into linear growth for nearly twenty years, from large-scale logistic-shaped products and geographies

Does this conform to the Elephant Curve? Is this really still essentially quadratic? The answer is clear when we plot the same data, this time measuring the year-over-year change in MAUs. Not as a *percentage*, but as numbers:

**Figure 36**: Facebook MAU growth is indeed an Elephant Curve: Logistic at first, then flat(ish), then starting to decline.

Why do we keep seeing this pattern, even at the scale of Facebook, one of the most “viral” products of all time? Because mathematically, things that look like an Elephant Curve, even if the logistic “trunk” is elongated over time, are linear for nearly their entire lifetimes. Everywhere except the very beginning. Adding up linear things definitionally creates a quadratic.

As a striking example of this claim⁠—that multiple, various Elephant Curves result in quadratic growth in the real world⁠—consider the detail behind the earlier chart of Global Internet Users over time, a type 3 product. Every country has grown logistically, at a variety of starting-times, diffusion rates, and carrying capacities, yet the aggregate is quadratic:

[source](https://ourworldindata.org/internet?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

[(Click to Enlarge)](https://longform.asmartbear.com/exponential-growth/thirty-years-varied-logistic-growth-adds-quadratic-growth-4392w.png)

**Figure 37**: Thirty years of varied logistic growth adds up to quadratic growth

To be certain the graph at the bottom (which is the same data as the chart shown earlier) is specifically quadratic, we chart the absolute difference in online population year by year. In a quadratic, these differences should grow linearly, i.e. each year adding a constant amount more than the previous year added. Which is indeed what we find, as precisely as we could expect from data in the messy real-world:

**Figure 38**

Bringing it back down to the scale of a single company, consider Netflix, another type 3 product. While their overall growth accelerates, under the hood we can see the US was already in a phase of slow-growth by 2014, with outside-US is taking up the slack through 2019:

[source](https://www.businessinsider.com/netflixs-original-international-content-fuel-q1-growth-2019-4?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 39**: A quadratic top-line, created by two roughly-linear geographies

If we chart the *changes* in subscribers, rather than totals, it’s even more clear that growth in the US has been in the declining phase of the Elephant Curve for a while, with outside-US is growing linearly:

[source](https://www.statista.com/chartoftheday/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 40**

And then, fast-forwarding to 2023, looking at total, global subscribers, we see that growth slowed outside of the US as well, and the familiar Elephant Curve returns in its entirety:

[source](https://twitter.com/stats_feed/status/1609104967935164417?s=12&amp;t=XEDWR_LNgM1uzUNNrX6WaA?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 41**

### Logistic growth with a varying carrying capacity: Start with market-share

Suppose you’re Facebook, and you’ve saturated many markets. You might be at carrying-capacity for those markets, but more people are still coming online. The markets are growing, so your carrying-capacity is growing, so you should still be able to grow too.

Indeed, recalling the charts above, Facebook’s current MAU growth rate, and that of global Internet users, both are currently hovering around 7% per year. Which isn’t a coincidence.

Let’s plot Facebook’s MAUs as a percentage of people online⁠—their *market share*:

**Figure 42**: The Elephant Curve strikes again

Finally we have the complete answer to why Facebook’s growth appears so “linear,” when the theory expects an Elephant Curve. When you examine growth *relative to market size* it *is* an Elephant, complete with logistic trunk, optimized back, and declining rump (even despite a COVID bump).

This is why at-scale companies are willing to spend billions of dollars increasing the size of the market⁠—it’s one of the few ways to create growth other than raising prices. So Google spent billions on Loon⁠—a subsidized service to bring low-cost internet to remote areas of the world. Its problem-statement is the first text on [its website](https://x.company/projects/loon/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post): “Billions of people across the globe still don’t have reliable, affordable access to the internet.” Or, putting it another way, “Wifi balloons are a kooky idea but how else are we going to increase the carrying-capacity of the ‘global internet user’ Elephant Curve?”

Or Facebook with its “Free Basics” system that ([in their words](https://www.facebook.com/connectivity/solutions/free-basics?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)) “Helps people discover the relevance and benefits of connectivity with free access to basic online services.” Except actually it’s only a few, hand-curated websites, all of which just happen to be western consumer products companies that are large Facebook advertisers, and the only available social network just happens to be Facebook. And there’s no email, so I hope you like Facebook Messenger. In other words, a [digital colonialism](https://www.theguardian.com/technology/2017/jul/27/facebook-free-basics-developing-markets?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post) whose purpose is to increase the carrying capacity of Facebook MAUs and the advertising that goes with it.

Elephant Curves are more visible when we plot growth as market share, because this incorporates the idea that carrying-capacity of the underlying market can itself be a moving target.

### Logistic growth with a varying unit revenue

We’ve largely been analyzing *users* rather than *revenue*, and for good reason: The lifeblood of any product is people who use it, regardless how much money it can extract in the process.

However, when we turn to revenue, we find that curves can become perkier. Facebook’s user growth might be linear, but could it be that revenue is exponential? It’s certainly not linear:

[source](https://www.statista.com/statistics/271258/facebooks-advertising-revenue-worldwide/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)

**Figure 43**

We already know Facebook’s user growth is linear, so the missing piece is Facebook’s revenue *per* user:

**Figure 44**: Logistic or Elephant yet again

Perhaps by now we’re not shocked to see the Elephant Curve once again. And we also know how the rest of the story goes: Because MAUs are Elephantine (which means mostly linear), and revenue-per-user is Elephantine (which means mostly linear), when you multiply them you get a quadratic, not an exponential, and that’s what we see in Facebook’s overall revenue growth.

## Actionable conclusions

When we seek out the Elephant Curve in our marketing channels, product lines, geographies, and verticals, not just in its hopefully-explosive initial phase, but its phases of optimization and decline, we can proactively look for these phases, and take action.

### Model by component

Our final discussion on the value of analyzing components of growth separate leads to a prescription for analyzing growth.

1. Estimate the growth curve for the entire market. Expect to be Elephantine (or simply logistic, in the case of trends that you can reasonably assume will not decline in the forecasted future, like global Internet use or smartphone use).
2. Estimate the product market-share curve. Expect to be Elephantine, and don’t be so bold as to assume your product will never decline relative to the market⁠—are you better at execution than Facebook?
3. Estimate monetization, i.e. revenue per customer.<sup>11</sup> This curve *might* be Elephantine, but not necessarily. It is highly dependent on the product and market, on how distinct the product is competitively, on the budgets of the customers, and more. Facebook has a strong [moat](https://longform.asmartbear.com/moats/) (network effect) and doesn’t charge end-users, so they (like Google) can raise prices consistently. A product in a commoditized market might never be able to raise prices, and thus must find growth in avenues like increasing usage, the introduction of companion products, expanding to other verticals or geographies, or by applying their technology to new markets.

> <sup>11</sup> The definition of “customer” should match whatever activity is most highly correlated with growth; this is also what “market share” should mean. For normal products people pay for, this is simply “paying customers,” but for example in the case of Facebook, this is MAUs at least, perhaps even DAUs.

You get better models by predicting each of these components separately, then multiplying for a final growth prediction. You’re also better able to track the model against reality, as more data becomes available.

---

Besides this break-down, there are many operational ideas suggested by the results above, especially for managing marketing campaigns.

This might be expanded in a future article, but for now, these probing questions might lead to better ideas on how to analyze and affect growth:

- Is our AdWords campaign topped out? Are we fooling ourselves into thinking there’s more inventory to access? How much more optimization is there to be had, and how would know? Are we hitting a decline due to uneconomical auctions, and if so, what is our reaction? When should we start experimenting with new channels, rather than continue to flog the AdWords channel for results that don’t exist?
- Is it OK to be less cost-effective if it means we can stave off decline? Should we be that “irrational bidder” who bids “too much” because we’re wise enough to see value beyond immediate cash pay-back? If so, how do we quantify that value, so we know just how “irrational” to be?
- To hit our growth goals for the year, what would have to be true of the growth of existing campaigns? Which can be reasonably expected to grow, hold steady, or shrink, based on their phase? How many additional, successful campaigns do we need, and how soon? Since not all that we attempt will succeed, how many do we need to start to yield the final quantity we need?
- Should we lean into newer channels before others figure them out, saturating the channel and cause clicks to be [both expensive and more rare](https://taylorpearson.me/ctr/?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post)?
- Rather than stack up small, limited campaigns, is there something more substantial that could generate more total growth? A single, large new geography instead of many smaller ones? A single, substantial new sales mechanism (e.g. reselling) rather than more advertising? A different pricing model instead of an additional sales model? Even if it takes 10x the effort, and possible even if it takes 10x the time, it might have 10x the results.
- Or the reverse⁠—do we pull funds when we smell decline, rather than spending our time and money fighting a losing battle, accepting a short-term hit on top-line growth in exchange for more efficient growth? Do we try to stack up many smaller, more efficient campaigns, generating growth as a bulk effort? Each effort affects the top line only marginally, but conversely our growth is less sensitive to the decline of any one campaign.

### Advice for Product Managers

- It’s great to add a feature to an existing product, but significant additional growth comes from increasing carrying capacity or creating a new avenue of growth. Early on you should focus on winning market share in one space, creating the first Elephant Curve, but after the product matures, something more drastic is required: Wholly new products, or updates significant enough to address new markets.
- It’s well-known that companies need to add additional products to continue fast growth after achieving scale. However the second product is highly unlikely to achieve same market share and monetary scale as the first, so there needs to be multiple, not just one.<sup>12</sup> This requires serious investment, parallel efforts, and the chutzpah to kill off the ideas that aren’t working.
- Because word-of-mouth-driven growth is so much more effective than marketing-driven growth (both in cost-per-customer and in that unlike direct advertising it grows automatically as the company grows), it is worth a great deal of time trying to figure out how to build that into the product, rather than relying only on the marketing team.

> <sup>12</sup> This is true at any scale⁠⁠—advertising is still 82% of Google’s revenue; of that 71% is advertising from search alone (i.e. excluding YouTube and other properties). Apple revenue is 60% iPhone. Even at smaller scales: Basecamp (neé 37signals) built multiple products over nearly two decades but only their first was successful enough to be worth working on; the company divested itself of the rest and rebranded to be identical to that product. It *is* possible for second products to eclipse the first; the iPhone was of course not Apple’s first product; The Tesla model 3 outsells the earlier model X, And at my own company Smart Bear our second product ended up being 95% of sales, and we essentially did the same as 37signals and went to a single product model.

---

> Half my advertising is wasted. I just don’t know which half.  
> —John Wanamaker

Mr. Wanamaker made his famous complaint more than a hundred years ago; even with modern analytics, today [it’s worse](https://www.mediavillage.com/article/which-half-of-my-advertising-is-wasted-and-it-is-only-half?utm_source=longform.asmartbear.com&utm_campaign=longform.asmartbear.com&utm_medium=post). The quadratic growth model won’t solve that puzzle, but the better you understand the mechanisms of growth, the more it is under your control.  

Printed from: *A Smart Bear*  
[https://longform.asmartbear.com/exponential-growth/](https://longform.asmartbear.com/exponential-growth/)  
© 2007-2025 Jason Cohen ![Twitter](https://longform.asmartbear.com/images/twitter.png) [@asmartbear](https://twitter.com/intent/user?screen_name=asmartbear)  

---

How startups beat incumbents

A startup can beat a large, successful incumbent, if it does things the incumbent can not or will not do. Here are those things.

Moats: Durable competitive advantage

Industries commoditize over time, delivering similar products at similar prices resulting in low profit. Moats are the antidote; your strategy must create some.