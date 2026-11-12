# Fear Driven Development

There's a methodology more widespread than Agile, older than Waterfall, and practiced in nearly every codebase that's been alive longer than two years. Nobody puts it on their résumé, and no conference has a track for it.

It's called **Fear Driven Development**, and you've probably done it this week.

## What it looks like

You open a file to fix a small bug. The function is 400 lines long. There's a comment at the top that says `// DO NOT TOUCH - ask Dave`. Dave left the company in 2021.

You find the line that's wrong. The fix is obvious: change a `>` to a `>=`. But you don't do that. Instead, you add a new `if` statement *above* the broken logic that catches your specific case and returns early. You don't change the original code, because you don't know what else depends on it.

The bug is fixed and the ticket is closed. The function is now 407 lines long.

Congratulations, you've practiced FDD.

## The symptoms

Fear Driven Development has some recognizable patterns:

- **Copy-paste over modification.** Rather than changing a shared function, you duplicate it as `processOrderV2` and use that instead. Now there are two, and soon there'll be three.
- **Commented-out code that lives forever.** Nobody deletes it, because what if we need it?
- **Feature flags that never get removed.** `ENABLE_NEW_CHECKOUT` has been `true` in production for three years, but the old path is still there, just in case.
- **Friday deploy bans that turn into Thursday deploy bans.** Then Wednesday. Eventually you ship once a month in a two-hour window with six people on a call.
- **Pull requests that grow huge.** Because every deploy is scary, you batch changes, which makes every deploy scarier.
- **"Let's not refactor right now."** It's never right now.

## Why it happens

Fear isn't irrational. It's a response to real signals. Developers become afraid when:

1. **Changes have broken things before, and nobody saw it coming.** The feedback loop was "a customer complained."
2. **Nobody understands the system end to end.** Knowledge lives in people's heads, and those people leave.
3. **Mistakes get punished.** If the last person who caused an outage got publicly blamed, everyone learned the lesson: don't touch anything.
4. **Rolling back is hard.** If undoing a bad change takes hours, every change carries hours of risk.

Fear is just the team's way of pricing in risk that the system doesn't help them manage.

## The cure isn't courage

You can't fix FDD by telling people to be braver. "Just refactor it!" is easy to say when it's not your pager going off at 3 a.m.

What actually works is making change *cheap and safe*, so fear stops being a reasonable response:

- **Tests that you trust.** Not 100% coverage, but tests around the things that matter most. Even a handful of characterization tests on that scary 400-line function changes everything. Now you'll *know* if you broke it.
- **Small, frequent deploys.** The less you change at once, the easier it is to find what went wrong. Frequency builds confidence; rarity builds dread.
- **Fast rollbacks.** If reverting takes two minutes, a bad deploy is an inconvenience, not a crisis.
- **Observability.** Logs, metrics, and alerts that tell you something's wrong before your users do.
- **Blameless postmortems.** Treat outages as system failures, not personal ones. People will take reasonable risks only when the cost of being wrong is learning, not humiliation.
- **Delete things.** Version control remembers. You don't need commented-out code as a safety blanket.

## The real cost

The danger of FDD is that it feels safe. Every individual decision, like adding the early return, copying the function, or skipping the refactor, is locally reasonable. But they compound. The codebase gets harder to understand, which makes it scarier to change, which makes people write more defensive code, which makes it harder to understand.

Fear is a feedback loop. So is confidence.

The next time you catch yourself writing the workaround instead of the fix, ask: *what would I need in order to not be afraid of this?* Then go build that first.

---

*What's the scariest file in your codebase? Tell me in the comments. I promise not to tell Dave.*
