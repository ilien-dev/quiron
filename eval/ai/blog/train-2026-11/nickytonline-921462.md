# How I Do Code Reviews

I've reviewed a lot of pull requests, and had my own code reviewed even more. Over time I stopped treating review as a gate and started treating it as a conversation. This is the process I follow, including the parts I used to get wrong.

## Start with the why, not the diff

Before I look at any code, I read the PR description and the linked ticket. I want to answer one question: what is this change trying to accomplish?

If I can't answer that in a sentence, that's my first piece of feedback. Without context, the reviewer has to reverse-engineer intent from code. That's how you end up approving something clean, well-tested, and aimed at the wrong problem.

## Skim the shape first

Next I skim the whole change without commenting. I look at which files were touched, how big the change is, and whether the structure makes sense.

- Does the change match the description, or is unrelated work mixed in?
- Are tests included, and do they sit next to the behavior they cover?
- Is anything surprising, like a new dependency, a config change, or a migration?

If a PR is 1,500 lines and touches four concerns, I'll often ask for a split before reviewing in depth. That isn't being difficult. Review quality drops sharply with size, and I'd rather review three small PRs thoroughly than rubber-stamp one huge one.

## Read the tests first

This habit changed my reviews the most. Tests are a spec written by the author. Reading them first tells me what the author believes the code should do, and then I can check the implementation against that belief.

I look for missing cases: empty inputs, nulls, timeouts, concurrent access, permission boundaries. If the tests only cover the happy path, I say so and suggest specific cases rather than a vague "needs more tests."

## Review the implementation in layers

Then I read the code, in order of importance:

1. **Correctness.** Does it do what it claims? Any off-by-one errors, race conditions, or unhandled failures?
2. **Security and data safety.** Is input validated? Are queries parameterized? Could this leak or destroy data?
3. **Design.** Does it fit the existing architecture? Is the abstraction earning its keep, or is it speculative?
4. **Readability.** Could someone new understand this in six months?
5. **Style.** Naming, formatting, minor nits.

The order matters. A correctness bug shouldn't be buried under fifteen comments about variable names. And style should mostly be automated: if a linter or formatter can catch it, it shouldn't consume human attention.

## Make comments easy to act on

I label comments so the author knows what's required:

- **Blocking:** this must change before merge.
- **Suggestion:** I'd do it differently, but it's your call.
- **Nit:** tiny and optional, ignore freely.
- **Question:** I don't understand, and I'm not assuming it's wrong.

Questions are underrated. "Why a map here instead of a list?" often gets a better outcome than "Use a list." Sometimes the author had a reason I missed and I learn something. Sometimes it was an accident and they fix it themselves.

I also explain the reason behind a request. "This could deadlock if two requests hit it at once" is far more useful than "Fix this."

## Say what's good

I try to leave at least one positive comment when something is done well: a tricky edge case handled, a clean abstraction, a test that documents behavior clearly. This isn't flattery. It tells the author what to keep doing, and it makes the critical comments easier to hear.

## Run it when it matters

For anything non-trivial, I check out the branch and run it. Reading code shows me what the author intended. Running it shows me what actually happens. I'll click through the UI, hit the endpoint, or step through a failing scenario in a debugger. It takes ten extra minutes and catches things no diff view will.

## Be fast, and be kind

A review that sits for two days is a blocked teammate. I aim to respond within a working day, even if the response is "I'll look at this properly tomorrow." For small PRs, a few hours.

On tone, I assume good intent and critique the code, not the person. "This function is doing a lot" beats "you wrote a messy function." If a thread gets long or tense, I jump on a quick call. Five minutes of talking resolves what thirty comments won't.

## Know when to approve

Perfect is not the bar. The bar is whether the change leaves the codebase better than it found it, and whether I'd be comfortable being paged for it. If the remaining issues are nits, I approve and trust the author to handle them. Holding a PR hostage over style preferences erodes trust and slows everyone down.

## Being reviewed is part of it

All of this works better when both sides practice it. I write small PRs, explain my reasoning in the description, and review my own diff before asking anyone else. I catch about half the comments I would have received myself.

## Wrapping up

Good review isn't about catching every flaw. It's about shared understanding, shared ownership, and steady improvement. Start with intent, read the tests, prioritize what matters, communicate clearly, and stay kind.

What's in your review routine? I'd love to hear what has worked for you in the comments.
