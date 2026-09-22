# How I Do Code Reviews

Code review is one of those skills nobody really teaches you directly. You pick it up by watching how senior developers review your pull requests, by getting feedback that stings a little, and eventually by figuring out your own approach through trial and error. After doing this for a long time, I've settled into a process that I think strikes a decent balance between thoroughness and not making people dread opening a review from me. Here's how I approach it.

## Start With Context, Not Code

Before I look at a single line of diff, I read the PR description. If there isn't one, or it's just a one-line summary, that's already useful information. A good description tells me what problem is being solved, why this particular approach was chosen, and anything the author wants reviewers to pay special attention to. Jumping straight into the diff without that context means you're reviewing code in a vacuum, and you'll end up asking questions the description would have already answered, or worse, suggesting changes that don't account for constraints the author already dealt with.

## Read Before You Comment

My first pass through a PR is read-only. I go through the whole diff top to bottom without leaving a single comment, just to build a mental model of what's changing and why. Commenting as you go tends to produce reviews that are reactive and scattered, flagging small things before you've seen the full picture. A second pass, informed by having seen everything, produces much more useful feedback, because you can tell the difference between a genuine issue and something that gets addressed three files later.

## Separate Blocking Issues From Suggestions

Not every comment I leave needs to block a merge, and I try to be explicit about which is which. I'll usually prefix a comment with something like "blocking:" if it's something that genuinely needs to change before I'll approve, versus "nit:" or "suggestion:" for things that are more about preference or minor polish. This distinction matters a lot, because without it, authors can't tell whether they need to address every single comment before merging or whether some are optional. Ambiguity here just creates friction and back-and-forth that wastes everyone's time.

## Ask Questions Instead of Making Demands

When something looks wrong or confusing, my default is to ask a question rather than assert that it's incorrect. Something like "what happens here if the array is empty?" instead of "this will break on an empty array." Sometimes I'm right and the author realizes there's a bug. Sometimes I'm missing context and there's a guard clause somewhere else that handles it. Either way, framing feedback as a question keeps the conversation collaborative instead of adversarial, and it leaves room for me to be wrong without it feeling like a confrontation.

## Focus on What Matters

It's easy to get pulled into nitpicking variable names or formatting preferences, but I try to keep my attention on things that actually matter: correctness, security, maintainability, and whether the code does what the PR claims it does. If a linter or formatter can catch something automatically, I don't want to spend human review time on it. That's what automated tooling is for, and leaning on it frees up review time for things a machine genuinely can't evaluate.

## Test the Change When It's Feasible

For anything nontrivial, I try to actually pull the branch down and run it locally, especially for UI changes or anything with tricky edge cases. Reading a diff only tells you so much. Actually clicking through a new feature, or running a test suite against unusual inputs, catches things that never would have occurred to me just by staring at the code.

## Be Generous With Approval

If a PR does what it's supposed to do and doesn't introduce any real problems, I approve it, even if I'd have written parts of it differently. Code review isn't about making every PR match exactly how I personally would have solved the problem. It's about catching real issues and keeping the codebase healthy, not enforcing my own stylistic preferences onto every contributor.

## Wrapping Up

None of this is revolutionary, and everyone develops their own rhythm over time. But the throughline for me is treating review as a collaborative conversation rather than a gate to get through. Read for context first, separate what's blocking from what's optional, ask questions instead of making demands, and focus your energy on the things that actually matter. Do that consistently, and code review stops being something people dread and starts being something that actually makes the codebase, and the team, better.
