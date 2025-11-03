---
title: "Directional decisions"
source: "https://world.hey.com/jason/directional-decisions-22bcd41c"
author:
published:
created: 2025-11-03
description: "In the course of building products, you’ll make a thousand common decisions, but only a handful of directional decisions. While a common decision may alter a specific feature, design, or implementation, a directional decision remaps the fundamental trajectory of the entire product. Make a directional decision and you’re now pointed thi..."
tags:
  - "jason-fried"
---
July 11, 2024

In the course of building products, you’ll make a thousand common decisions, but only a handful of directional decisions.  
  
While a common decision may alter a specific feature, design, or implementation, a directional decision remaps the fundamental trajectory of the entire product.  
  
Make a directional decision and you’re now pointed this way or that way. Make a directional decision and you either shut something off or open something up. Make a directional decision and you’ll get a hundred no’s for the price of one.  
  
Let’s look at a specific directional decision we made for [Writebook](https://once.com/writebook), our latest product.  
  
Writebook is remarkably simple software that lets you publish text and pictures in a simple, browsable online book format.  
  
Books are written and published. This presents an opportunity to make a directional decision: Is Writebook a writing tool or a publishing tool? Or both?  
  
At one point, we treated the publishing side and the writing side as equals. Both are involved in getting a book online. Seems reasonable, right?  
  
Reasonable isn’t the measure, though. It’s easy to say something should do everything well because saying something is easy doesn’t involve any work, or require any tradeoffs. But building products is all about tradeoffs. When there are no tradeoffs in the conversation you’re having, you know you aren’t building, you’re just talking. But it was time to build.  
  
But what’s the epicenter of Writebook? What’s the thing you can do easily with Writebook that was a lot harder without Writebook? Essentially, what does Writebook exist to do? What did the current world look like without Writebook?  
  
You can write books in a thousand tools in a thousand places. But instantly publishing a book in a simple web-friendly format is really hard. It generally involves a lot of custom work, or a complex CMS system, or bending some blogging platform into a pretzel just to unsatisfyingly make it sorta kinda create books instead of blogs.  
  
And since Writebook supports Markdown, you can easily write in a simple text editor and then copy and paste the finished text into Writebook when you’re ready. The place to write isn’t what’s lacking out there. The place to publish is.  
  
So we made a directional decision: Writebook was a publishing tool. You could obviously still write in it — we even designed a new Markdown editor to make basic formatting easier. But, our overall directional deciding Writebook was about publishing rather than writing allowed us to say no to dozens of days of additional work and sidestep piles of additional complexity.  
  
But how did that decision come to be? Why did it happen? When did it happen?  
  
Well, before we settled on the publishing angle, we went down the “writing and publishing are equals” path. Part of that project involved building a system to track diffs so an author (or multiple) could track changes, additions, and subtractions. Writing software usually has this sort of thing, so if we were making writing software it felt like basic table stakes.  
  
It was during a design review that it hit me. This is fucking complicated and unnecessary. It’ll work, but it’s not actually useful. And, further, trying to build a multiple-author change tracking system to our standards is going to distract us from the more important, core differentiation work we have to do on the publishing side.  
  
So I wrote up my thoughts and posted it to the Writebook project in Basecamp. Here is that post in full: [https://public.3.basecamp.com/p/4SfGJ2wQNXdUArbxf7FjDouz](https://public.3.basecamp.com/p/4SfGJ2wQNXdUArbxf7FjDouz)  
  
![full-basecamp-thread.png](https://world.hey.com/jason/22bcd41c/representations/eyJfcmFpbHMiOnsiZGF0YSI6MTczMTA5MzM5NiwicHVyIjoiYmxvYl9pZCJ9fQ--acbf096e9fbf76774e4aba00aabdd699b176fee3e9db055b09da791a69183eae/eyJfcmFpbHMiOnsiZGF0YSI6eyJmb3JtYXQiOiJwbmciLCJyZXNpemVfdG9fbGltaXQiOlszODQwLDI1NjBdLCJxdWFsaXR5Ijo2MCwibG9hZGVyIjp7InBhZ2UiOm51bGx9LCJjb2FsZXNjZSI6dHJ1ZX0sInB1ciI6InZhcmlhdGlvbiJ9fQ--7edc7b21f6fad97fa22412618822c4d19725431f296c7ce47dc174b61535d27c/full-basecamp-thread.png)

  
  
I concluded with:  
  

> Workbook is a final publishing platform, it's not a collaborative editing environment. What we're solving for is easily getting a book up online, in in various formats, in the simplest, quickest, more comprehensive way. If you want comprehensive collaborative editing and change tracking, write it elsewhere and, when it's done, pop it in here to publish.

  
We ended up keeping a very minimal version of writing history in place as a backstop for major mistakes (“Oh shit, I deleted the whole thing by accident”), but in the final version of Writebook there’s no formal track changes feature, no colored diffs, and no focus on the collaborative writing process.  
  
Writebook is simply a final publishing platform first and foremost. You can write and edit in it, but it’s bare bones and basic — which is fine almost all of the time anyway.  
  
And guess what? Writebook has been out for a few weeks now and tracking changes or sophisticated collaborative editing tools or features has barely been requested. I’m glad we explored it early on, but even more glad we dropped it in the end. Publishing was the right direction.  
  

\-Jason

About Jason Fried