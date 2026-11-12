I almost didn't write this. A year in review feels like something you do when the year went to plan, and 2020 did not go to plan for anyone I know. But I've read a dozen of these posts this week, and the ones I liked best were the honest ones. So here is mine: what I worked on, what I learned, what I dropped, and what I want from 2021.

## The year work moved into my bedroom

In the second week of March my team was told to take our laptops home "for a couple of weeks". I'm writing this in December from the same desk, which is a folding table wedged between my bed and the wardrobe.

The first month was rough. Our team ran on overheard conversations. Someone would sigh at their monitor, someone else would roll their chair over, and the problem would be solved in five minutes. Remote, that same problem turned into a forty-message Slack thread and a call nobody wanted.

What fixed it was not a tool. It was writing things down. We started putting decisions in pull request descriptions and short design notes instead of in meetings. By summer I noticed something I didn't expect: I understood our codebase better than I had in the office, because the reasoning behind changes was finally somewhere I could read it.

I also learned that I'm bad at stopping. Without a commute there was no line between work and not-work, and I spent most of April answering messages at 10pm. More on that below.

## What I learned

**TypeScript, properly this time.** I had been writing "TypeScript" for two years, which really meant JavaScript with `any` sprinkled over it. This year we migrated a mid-sized React app to strict mode and I had to learn what I'd been avoiding: generics, discriminated unions, narrowing, and how to read an error message that is nine lines long. The migration took three months of small pull requests. The payoff arrived the first time I renamed a field in an API response and the compiler handed me a list of every place that would break.

**Testing that I trust.** I used to write tests after the fact, to make a coverage number go up. This year I switched most of my component tests to React Testing Library and started testing what the user sees instead of how the component is built. I have fewer tests now, and they fail for real reasons. That change did more for my confidence when deploying than anything else on this list.

**Docker, finally.** I'd copied Dockerfiles from Stack Overflow for years without understanding them. During a quiet week in May I sat down and worked through layers, caching, multi-stage builds, and compose. I got our local setup from "follow this 30-step wiki page" to a single command. A new teammate who joined in September was running the app within an hour, and that felt better than any feature I shipped.

**SQL, a little.** I leaned on an ORM for so long that I couldn't read a query plan. A slow dashboard forced me to learn. One missing index took a page from eleven seconds to under one. I'm still a beginner here, but I'm no longer afraid of `EXPLAIN`.

## The side project graveyard

Lockdown gave me evenings, and I filled them with repositories. Here is the honest count: I started six side projects this year and finished one.

The casualties include a habit tracker (I stopped using it, which says something), a recipe site for my family, a Chrome extension, a half-built static site generator that nobody asked for, and a game jam entry that never reached the "game" part.

The one that survived is a small command line tool that turns my Markdown notes into a searchable local site. It's about 600 lines, it has 40-odd stars, and two strangers have sent pull requests. Getting a pull request from someone I've never met was a highlight of my year.

The lesson I took from the graveyard is that I finish things I need and abandon things I think would look good on a profile. The notes tool exists because I use it every day. Everything else was built for an imaginary audience.

## Writing in public

I published my first post here in April. It was a short piece about a `useEffect` bug that cost me an afternoon, and I assumed nobody would read it. It got a few thousand views and a comment thread that taught me more than I'd put into the post.

I ended the year with nine posts. That's short of the "one a week" I promised myself in a burst of April energy, and I'm fine with it. Writing forces me to find the gaps in what I think I know. Twice this year I started a post to explain something and discovered halfway through that I had it wrong.

I also gave my first talk, at a meetup that had moved online. Presenting to a grid of muted squares is strange. You tell a joke and get silence, and you can't tell if it landed. But the barrier to entry was low: no travel, no stage, just my folding table. I doubt I'd have volunteered for an in-person one.

## The part that wasn't about code

By October I was tired in a way that sleep didn't fix. I wasn't working enormous hours. I was just never fully off. The laptop sat two metres from my pillow, and the same screen held my job, my side projects, my friends, and the news.

I took a week off in November and did nothing technical at all. I walked a lot, cooked badly, and read two novels. When I came back I made three changes that have stuck so far:

1. The work laptop goes in a drawer at 6pm. Closed isn't enough; it has to be out of sight.
2. No Slack on my phone.
3. A walk before work, as a fake commute. It sounds silly and it works.

I don't have a neat conclusion about burnout. I only know that I spent a lot of the year treating free time as hours to be optimised, and that I felt better the moment I stopped.

## What I'd do differently

- **Ask for help sooner.** Remote work made it easy to stay stuck quietly for a day. Nobody could see me struggling, so nobody offered.
- **Start fewer things.** Six projects is five too many.
- **Keep a work log.** Writing this post was hard because I'd forgotten most of the first half of the year. I had to dig through commit history to reconstruct it.
- **Stop comparing.** My feed was full of people who seemed to learn three languages and launch a startup during lockdown. Getting through the year in one piece was a fair goal.

## Goals for 2021

I'm keeping the list short on purpose.

- **Go deeper on the backend.** I want to build and deploy one service end to end, including the parts I usually hand off: the database, monitoring, and alerts.
- **Contribute to one open source project regularly**, instead of scattering one-off fixes across ten.
- **Write one post a month.** Twelve is a number I can hit.
- **Mentor someone.** Several people were generous with their time for me this year, and I'd like to pass that on.
- **Protect the evenings.** The drawer rule stays.

## Closing

2020 was not the year I planned. I didn't travel, I didn't attend the conference I'd bought a ticket for, and I didn't finish most of what I started. But I'm a better engineer than I was in January, mostly because of unglamorous things: stricter types, better tests, clearer writing, and learning when to shut the laptop.

If you wrote your own review, leave a link in the comments. I'd like to read it. And if your year was mostly about getting by, that counts too.

See you in 2021.
