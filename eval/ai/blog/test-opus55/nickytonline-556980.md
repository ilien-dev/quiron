# My 2020 Year in Review

I've started this post four times. The first draft was a cheerful list of accomplishments. The second was a long complaint. The third tried to be profound and failed. This version is my attempt at being honest: 2020 was hard, it was weird, and somehow it was also one of the most important years of my career.

So let's walk through it: what I built, what I learned, what broke, and what I'm taking into 2021.

## January–February: The Year I Thought I Was Going to Have

I started 2020 with a goals list taped to my monitor. It was ambitious in the way all January lists are:

- Ship a side project to real users
- Get comfortable with TypeScript
- Speak at a local meetup
- Read 24 books
- Go to at least one conference in person

For about eight weeks, things went to plan. I was commuting to the office, pairing with teammates at actual desks, and spending my evenings rewriting a small JavaScript project in TypeScript. I signed up to give a lightning talk at a meetup in April. I bought a ticket to a conference in June.

You can probably guess how the last two went.

## March: Everything Changes

In mid-March, our team got a message saying we'd be working from home "for two weeks, maybe three." I packed up my keyboard, a monitor, and a sad little desk plant, and I didn't go back to the office for the rest of the year.

The first month of remote work was rough. I didn't have a real desk. I worked from my kitchen table, then my couch, then a folding table wedged into the corner of my bedroom. My back hated me. My sleep schedule fell apart. I found myself checking Slack at 11 p.m. because the line between "work" and "home" had stopped existing.

The technical side was easier than the human side. We already used Git, CI, and cloud infrastructure, so code kept shipping. What we lost was the hallway conversation, the quick "hey, can you look at this?" over someone's shoulder, the lunch where you hear about a problem on another team before it becomes your problem.

**What I learned:** Remote work doesn't remove the need for communication. It just removes the accidental kind. Everything has to be intentional now.

## April–May: Building Habits That Actually Stuck

Around April I realized "temporary" wasn't temporary, and I needed to stop living in emergency mode. A few changes made a huge difference:

**1. A real workspace.** I bought a cheap desk and a decent chair. It's not glamorous, but my body stopped aching and my brain started associating that corner with focus.

**2. A fake commute.** Every morning I walk around the block before I open my laptop, and I do the same thing when I close it. It sounds silly, but it gives my day a clear start and end.

**3. Written-first communication.** Our team started writing short design docs before tackling anything bigger than a day of work. We also moved status updates to an async thread instead of a daily call. Meetings got shorter and fewer, and the ones we kept actually mattered.

**4. Camera-on pairing sessions.** Twice a week I'd pair with a teammate for an hour, just to work through something together. Some of the best debugging I did all year happened in those calls, and they were the closest thing to office camaraderie I had.

## June: The Meetup Talk That Became a Video

My April meetup was canceled, but in June the organizers moved online and asked if I still wanted to give my talk. I said yes before I could think too hard about it.

The topic was "Migrating a Small Project to TypeScript Without Losing Your Mind." I'd been sitting on lessons from my side project rewrite, and the talk was basically a list of things I wish I'd known before starting:

- Turn on `strict` mode early. It's painful, but adding it later is worse.
- Use `unknown` instead of `any` when you genuinely don't know a type.
- Migrate file by file with `allowJs`, not all at once.
- Types for third-party libraries are sometimes wrong. Don't assume your code is the problem.

Presenting to a grid of muted webcams was strange. You get none of the feedback of a live room: no laughs, no nods, no confused faces. But afterward, several people messaged me with questions, and one person said the talk convinced them to finally try TypeScript at work. That one message made the whole thing worth it.

**What I learned:** Online events lower the barrier to speaking. If you've been nervous about giving a talk, a virtual meetup is a great first step.

## July–September: Shipping the Side Project (Finally)

For years I've had a graveyard of half-finished side projects. This year, with no commute and fewer social plans, I decided to actually finish one.

The project was a small web app for tracking personal reading goals, partly inspired by my own 24-book target. It let you log books, set yearly goals, and see your progress over time. Nothing revolutionary, but it was *mine*.

The stack:

- **Frontend:** React with TypeScript
- **Backend:** A small Node/Express API
- **Database:** PostgreSQL
- **Hosting:** A managed platform with a free tier, because I am cheap

The hardest part wasn't the code. It was scope. Every weekend I'd think of a new feature: social sharing! Recommendations! A mobile app! I eventually wrote "v1" on a sticky note with exactly five features and refused to touch anything else until those were done.

I launched in September with a short post here on DEV and a few shares on social media. About 300 people signed up in the first month. That's a tiny number by startup standards, but it was 300 more people than had ever used anything I built on my own.

**What I learned:**

- Finishing is a skill, and it's separate from building.
- A small, working thing beats a big, imaginary thing.
- Real users will find bugs you never imagined. (Someone entered a book with a 4,000-character title. I now validate input lengths.)

## October–November: Burnout, and Admitting It

I'd love to say the year kept climbing, but October was when everything caught up with me.

Between my day job, maintaining the side project, the news cycle, and months of isolation, I hit a wall. I stopped enjoying code. I'd open my editor and stare at it. Small bugs felt enormous. I was irritable with people I care about.

What helped was boring and unglamorous:

- I took a full week off with no laptop.
- I told my manager I was struggling, which was scary, but they were supportive and helped me rebalance my workload.
- I put the side project in "maintenance mode" and stopped adding features.
- I started reading fiction again instead of only technical books.

I'm not writing this to sound wise. I'm writing it because I spent weeks pretending I was fine, and I wish someone had told me earlier that burnout is common, especially this year, and that it's okay to step back.

**What I learned:** Rest isn't a reward for productivity. It's a requirement for it.

## December: Looking Back at the List

So how did the goals taped to my monitor turn out?

- ✅ **Ship a side project to real users** — Done, and still running.
- ✅ **Get comfortable with TypeScript** — I now reach for it by default.
- ✅ **Speak at a local meetup** — Virtually, but it counts.
- ⚠️ **Read 24 books** — I hit 17. Fine by me.
- ❌ **Go to a conference in person** — Not this year, for obvious reasons.

Three and a half out of five, in a year like this one? I'll take it.

## What I'm Taking Into 2021

A few principles I want to carry forward:

1. **Be intentional about communication.** Write things down. Over-communicate context. Assume nothing is obvious.
2. **Keep scope small.** Whether it's a feature or a side project, ship the small version first.
3. **Protect my energy.** Schedule breaks like meetings. Take the time off.
4. **Share what I learn.** The talk and the launch post connected me with more developers than any year before, even without in-person events.
5. **Be kind, including to myself.** Everyone is carrying something heavy right now.

## Thank You

To everyone who signed up for my little app, asked a question after my talk, left a comment on a post, or just sent a "how are you holding up?" message: thank you. This community made a lonely year feel a lot less lonely.

How was your 2020? I'd genuinely love to hear what you built, learned, or survived. Drop it in the comments. 💙

---

That comes to roughly 1,380 words. A few notes:

- **Front matter** uses DEV's format with `published: false`, so you can preview it as a draft before going live.
- **To make it yours**, swap in your real goals, project details, signup numbers, and stack. Readers respond best to specific personal details.
- **If you'd rather not include something personal** like the burnout section, I can rework it into a lighter "lessons learned" section.
