Every December I tell myself I'll write one of these, and every December I find a reason not to. This year I'm doing it. Partly so I remember what happened, and partly because reading other people's year-in-review posts has helped me more than I expected. Seeing someone else admit they struggled with the same things makes them feel a lot more manageable.

So here's my 2021: what I built, what I learned, what didn't work, and what I'm carrying into 2022.

## The Big Picture

If I had to sum up 2021 in one sentence, it would be: **I stopped trying to learn everything and started trying to finish things.**

In 2020 I collected tutorials the way some people collect houseplants. I had a dozen half-finished courses, three abandoned side projects, and a bookmarks folder called "read later" that I never read later. I felt busy all the time, but I couldn't point to much that I'd actually made.

This year I made a rule: no new course or framework until I'd shipped something with what I already knew. It was harder than it sounds, and I broke the rule more than once. Still, it changed how I spent my time.

## What I Shipped

### A real project, used by real people

My biggest win was finally launching a side project that other people use. It's a small web app that helps a local community group manage volunteer sign-ups. Before, they were juggling a shared spreadsheet, a group chat, and a lot of "wait, who's covering Saturday?"

It's nothing fancy: a React front end, a small Node/Express API, and PostgreSQL behind it. But it has users who aren't my friends being polite, and that's a completely different experience. Real users find bugs you'd never think of. They use features in ways you didn't intend. They also tell you, kindly but clearly, when something is confusing.

A few things I learned from it:

- **Boring tech is a feature.** I picked tools I already knew well, so I spent my time solving the group's problems instead of fighting my stack.
- **Talk to users early.** My first version had a beautiful calendar view nobody asked for. What they actually needed was a reminder email the night before a shift.
- **Done beats perfect.** The first deploy was rough. It also worked, and every improvement since then has been based on feedback instead of guesses.

### Leveling up at work

At my day job I moved from mostly taking tickets to owning a feature end to end. That meant writing the technical design, breaking the work into tasks, coordinating with design and QA, and being the person people pinged when something broke.

It was uncomfortable at first. I'm used to getting a well-defined problem and solving it. Owning a feature means dealing with ambiguity, making trade-offs, and sometimes telling people "no, not in this release." I didn't get it all right, but by the end of the year I was much more comfortable being the one who decides instead of the one who waits to be told.

## What I Learned

### TypeScript finally clicked

I'd been "sort of" using TypeScript for a while, which mostly meant sprinkling `any` everywhere until the red squiggles went away. This year I committed to it properly, and somewhere around March it clicked. Once I stopped fighting the compiler and started treating it as a collaborator, I caught bugs before they reached the browser and refactored with way more confidence.

If you're stuck in the `any` phase, my advice is to turn on `strict` mode in a small project and suffer through it for a week. It's worth it.

### Testing is a design tool

I used to think of tests as a chore to get through after the "real" work. This year I started writing tests earlier, and I noticed something: code that's hard to test is usually badly designed. When a function needs five mocks to test, it's doing too much. Tests became a way to get feedback on my design, not just a safety net.

### Writing helps me think

I published a handful of posts here on dev.to this year. None of them went viral, and that's fine. Writing them forced me to understand topics well enough to explain them, and that taught me more than any tutorial did. A couple of readers left comments that corrected my misunderstandings, and I'm genuinely grateful for that.

## What Didn't Go Well

I don't want this to read like a highlight reel, so here's the honest part.

**I burned out a bit in the summer.** Between a demanding release at work and evenings spent on the side project, I stopped taking real breaks. I didn't notice until I realized I was dreading opening my laptop, even for things I usually enjoy. I took two weeks off in August, mostly offline, and it helped a lot. The lesson I keep having to relearn is that rest isn't the opposite of productivity. It's part of it.

**I said yes to too much.** I agreed to help with a couple of open source issues, a friend's portfolio site, and a mentoring commitment, all in the same month. I did all of them a little worse than I would have done one of them well. In 2022 I want to get better at saying "not right now."

**I neglected fundamentals.** I spent a lot of time on frameworks and not much on things like networking, databases, and how the browser actually works. I felt that gap a few times this year when debugging got deep.

## By the Numbers

Because every year-in-review needs some numbers:

- **1** side project launched with real users
- **6** blog posts published
- **~40** books started, **12** actually finished (progress!)
- **2** weeks fully offline
- **0** new JavaScript frameworks learned, and I'm oddly proud of that

## Looking Ahead to 2022

A few intentions, not resolutions, for next year:

1. **Go deeper on fundamentals.** I want to really understand databases: indexing, query planning, transactions. I'm planning to work through a good book on it alongside a small project.
2. **Protect my time.** Fewer commitments, done well. A real calendar block for rest, not just for work.
3. **Keep writing.** One post a month, about whatever I'm learning, even if it feels basic. Someone is always one step behind you and would find it useful.
4. **Help someone else get started.** I had people take a chance on me early on. I'd like to pay that forward through mentoring, done properly this time instead of squeezed in.

## Thanks

If you read any of my posts this year, left a comment, or answered a question I asked in a moment of desperation, thank you. This community has been one of the best parts of being a developer, and I'm glad to be part of it.

How was your 2021? I'd love to read your year in review. Drop a link in the comments.
