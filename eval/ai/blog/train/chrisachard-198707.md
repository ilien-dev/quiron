# Fear Driven Development

We've all heard of Test Driven Development. Behavior Driven Development. Domain Driven Design. But there's another methodology that's practiced far more widely than any of those, and nobody ever puts it on their resume.

I'm talking about **Fear Driven Development**.

You've probably done it. I definitely have. It's when the decisions you make about code aren't driven by what's best for the product, the users, or even the codebase. They're driven by fear.

## What it looks like

Fear Driven Development shows up in a lot of subtle ways:

- **You don't touch that file.** Everyone knows the one. It's 3,000 lines long, has no tests, and the last person who understood it left the company in 2016. So instead of fixing the bug properly, you add a special case somewhere else.
- **You copy and paste instead of refactoring.** Changing the shared function might break something, so you duplicate it and tweak the copy. Now there are two of them.
- **You don't delete dead code.** What if something is still using it? Better leave it there. Forever.
- **You avoid deploying on Fridays.** Or Thursdays. Or really any day your manager is on vacation.
- **You don't ask questions in meetings.** What if it's a dumb question? What if everyone else already knows?
- **You over-engineer everything.** You add three layers of abstraction "just in case," because being caught unprepared feels worse than writing complex code.

None of these feel like big decisions in the moment. But they add up. Over time, fear makes a codebase harder to change, which makes people more afraid to change it, which makes it even harder. It's a loop.

## Where the fear comes from

Fear isn't irrational. It usually comes from real experiences:

- You broke production once, and it was a bad day.
- You got blamed for something in a code review, and it stung.
- The system is genuinely fragile, and changes really do cause unexpected problems.
- The team culture punishes mistakes instead of learning from them.

So the fear is often a *signal*. It's telling you something about the code, the process, or the environment. The problem is when we respond to the signal by avoiding things, instead of fixing what's causing it.

## How to fight it

The goal isn't to become fearless and start pushing to `main` with your eyes closed. The goal is to make the scary things less scary.

**Write tests for the scary parts.** Before you touch that 3,000-line file, write a few characterization tests that capture what it does today. They don't have to be pretty. They just have to tell you when you've changed behavior. Suddenly the file isn't a minefield anymore.

**Make deploys small and boring.** Big deploys are scary because a lot can go wrong at once. Small, frequent deploys with easy rollbacks make each one low-stakes. If you can undo a change in thirty seconds, you'll be a lot braver about making it.

**Use feature flags.** Ship code turned off, then turn it on for a small group of users. If something breaks, flip it back.

**Add observability.** A lot of fear comes from not knowing what's happening. Good logging, metrics, and alerts mean you'll find out quickly if something goes wrong, instead of hearing about it from an angry customer three days later.

**Push for blameless postmortems.** If your team treats incidents as learning opportunities instead of searching for someone to blame, people stop hiding mistakes and start fixing the systems that allowed them.

**Ask the "dumb" question.** In my experience, if you're confused, at least two other people in the room are too. Someone has to go first.

## A small challenge

This week, pick one thing you've been avoiding because it feels risky. Maybe it's a gnarly function, an outdated dependency, or a question you've been too embarrassed to ask. Then figure out what would make it feel safe, whether that's a test, a flag, or just a quick chat with a teammate.

Then do it.

Fear is a useful signal. It's just a terrible architect.
