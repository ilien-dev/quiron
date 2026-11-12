# Goodbye Master, Hello...What?

Renaming a Git branch sounds like a five-minute task.

You type a command, update a setting, and get back to work. Then CI breaks, a deployment script starts complaining, and someone asks whether the new branch should be called `main`, `trunk`, `develop`, or, apparently without irony, `the-real-one`.

Congratulations. Your naming change has become an architecture meeting.

The interesting part isn’t the command. It’s what the argument reveals about how we build software together.

## A default isn’t a design decision

For years, plenty of developers created repositories with a branch called `master` because that was the default they encountered. No committee. No manifesto. Just a name inherited from a tool, a tutorial, or an older project.

That distinction matters.

We often defend familiar conventions as if we carefully selected them. Sometimes we did. Sometimes we copied a command from a README in 2016 and never revisited it.

Changing a default invites a useful question: if we were starting today, what would we choose?

For a repository’s primary integration branch, `main` is a straightforward answer. It describes the branch’s role without requiring a history lesson.

But choosing the name is only the beginning.

## Your branch name is an interface

A branch can look like an internal detail until you rename it.

Suddenly, you discover its consumers:

- CI workflows that filter events by branch.
- Deployment jobs that check out a hardcoded reference.
- Documentation with clone and checkout instructions.
- Protection rules tied to the old name.
- Scripts in somebody else’s repository.

That last one is especially fun. Nothing says “loosely coupled system” like another team’s release process depending on a string you thought was private.

A widely referenced branch name behaves like an API. Changing it deserves the same basic care: identify consumers, update dependencies, communicate the transition, and verify the result.

The lesson extends beyond Git. Anything people or programs rely on can become a contract, whether you intended it to or not.

## Pick a name that explains the job

So, what should replace `master`?

Usually, `main`.

It’s short, readable, and easy to explain: this is the main branch.

`trunk` can also make sense when your team uses that vocabulary consistently. `develop` describes a different role in workflows that distinguish ongoing integration from release-ready code.

The mistake is treating these names as interchangeable decorations.

If your primary branch represents deployable code, document that expectation. If it accepts incomplete work behind feature flags, explain that too.

A branch called `production` doesn’t magically make its contents safe to deploy. A branch called `main` doesn’t tell a new teammate when to merge.

Names help, but working agreements do the heavier lifting.

## Make the migration boring

Before renaming anything, search for the old branch name across the repository and your automation configuration. Check repository settings separately; a text search won’t reveal every protection rule or deployment integration.

Then coordinate the change with the people who maintain those systems.

Afterward, verify the ordinary path: open a pull request, run the checks, merge a harmless change, and confirm the expected deployment behavior.

Also give collaborators clear instructions for updating their local clones. “We renamed the branch, good luck” is technically an announcement, but it leaves something to be desired as documentation.

Keep the migration focused. This is probably not the moment to redesign your entire release strategy.

## Leave room for people

Conversations about naming can become exhausting because participants are answering different questions.

One person is discussing inclusive language. Another is worried about broken automation. A third just wants their pull request merged before lunch.

Those concerns can coexist.

You can support a naming change while asking for a migration plan. You can acknowledge practical costs without treating the old default as sacred.

Good engineering conversations connect intentions to implementation.

So, goodbye `master`. Hello `main`, perhaps.

The name should be easy. The work is making sure everyone—and every script—knows what it means.

Then we can return to naming things that are actually difficult.

Like variables.
