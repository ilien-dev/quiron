# How to Participate in Hacktoberfest as a Code Newbie

Hacktoberfest is one of the best times of the year to dip your toes into open source, especially if you're new to coding and have always been too scared to contribute. The event runs every October and encourages developers of all skill levels to make pull requests to open source projects. Yes, that includes beginners. If you've been holding back, this post is for you.

## What is Hacktoberfest?

Hacktoberfest is a month-long celebration of open source. It's organized by DigitalOcean with various open source communities, and the goal is simple: get more people to contribute to open source projects, whether that means fixing bugs, improving documentation, adding tests or building new features.

In past years, people who completed a certain number of quality pull requests during October got some kind of reward. It was a T-shirt for a while, and more recently there have been options like planting trees. But honestly, I don't think the reward is the point. The point is the experience you get, and the confidence you get from contributing to real projects.

## Why it's a great place for beginners to start

If you're new to coding, the idea of contributing to open source can feel scary. Aren't these projects maintained by expert developers? Won't your code get torn apart in review? What if you break something?

The event exists to lower that barrier. Maintainers who take part know that a wave of new people is about to show up, many of them beginners, and a lot of projects set up beginner-friendly issues ahead of time. The whole event is built with people like you in mind.

## Step 1: Sign up

Go to the official [Hacktoberfest website](https://hacktoberfest.com) and register with your GitHub (or GitLab) account. It's free and takes a minute. That's how your pull requests get tracked.

## Step 2: Find beginner-friendly issues

I think this is the part that scares beginners the most. There are a few reliable ways to find issues that fit your skill level, though.

### Search GitHub labels

Many projects tag issues for beginners. Look for labels like these:

- `good first issue`
- `beginner-friendly`
- `hacktoberfest`
- `help wanted`

You can search GitHub for these labels together with the Hacktoberfest topic:

```
is:issue is:open label:"good first issue" label:"hacktoberfest"
```

### Use curated lists

The community keeps lists of beginner-friendly Hacktoberfest issues from lots of projects, so you can look through a list and skip searching dozens of projects by hand. Search for "Hacktoberfest beginner friendly issues" and you'll find several of these lists every year.

### Don't skip documentation

I'd say the docs are a great place to start, because you don't need to know a project's code well. Fixing typos, clarifying confusing instructions, adding missing examples or improving a README all count as real contributions. They're also a low-pressure way to get used to the basics of forking, branching and opening a pull request.

## Step 3: Understand the contribution workflow

If you've never contributed to an open source project before, the basic workflow looks like this:

1. Fork the repository. This creates your own copy of the project under your GitHub account.
2. Clone your fork locally with `git clone <your-fork-url>`.
3. Create a new branch with `git checkout -b fix-typo-in-readme`.
4. Make your changes. Fix the bug, update the docs, or do whatever the issue calls for.
5. Commit your changes with a clear commit message that says what you did.
6. Push to your fork with `git push origin fix-typo-in-readme`.
7. Open a pull request from your fork's branch back to the original repository.

Most projects have a `CONTRIBUTING.md` file that explains what they expect, so I'd check for one before you start.

## Step 4: Write a clear pull request

When you open your pull request, take a moment to explain what you changed and why. A good description makes life much easier for the maintainer who reviews it. It also shows that you understand what you changed and aren't just copying instructions.

I like a simple template like this one:

```
## What this changes
Fixes a typo in the installation instructions section of the README.

## Why
The current instructions reference an outdated command that no longer works.
```

I'd keep it short and specific. A small fix only needs a short description.

## Step 5: Be patient and open to feedback

Maintainers are often volunteers with a lot on their plates, so it might take a few days (or longer) before someone reviews your pull request. Don't be discouraged by the wait, and don't take it personally if a maintainer asks for changes.

I promise that a review says nothing about your worth as a developer. Reviews are a normal part of how open source works, and how software development works in general. Every experienced developer has had a maintainer ask for changes more times than they can count.

## Things to avoid

Unfortunately, the event has attracted some bad behavior in past years. Mostly it was low-effort, spammy pull requests submitted just to hit the quota, like adding a random blank line. That kind of pull request wastes maintainers' time and gives the whole event a bad name. Please don't do it.

Here's what I'd do instead:

- Only submit pull requests to projects that have opted in.
- Make sure your pull request adds something, however small.
- Read a project's contribution guidelines before you submit a pull request.
- If a maintainer labels your PR as spam, learn from it and try again with a better pull request on another project.

## What you get besides the shirt

Whatever the physical reward is in a given year, I think taking part as a beginner gets you some things that last:

- You get practical Git and GitHub experience, until forking, branching, committing and opening pull requests feel like second nature.
- You see real projects and how experienced developers build and maintain them.
- You get confidence. Going through the whole process, from finding an issue to getting a PR merged, gives you a real boost.
- You get portfolio material. Merged pull requests are proof of your skills that you can show when you apply for jobs.
- You get to meet people. Talking with maintainers and other contributors can lead to mentorship and networking.

## Final thoughts

It's a welcoming way into open source, especially if you've been holding back. My advice is to start small, look for beginner-friendly issues, put some thought into your contributions and not be afraid of feedback.

You don't need to be an expert to contribute to open source. You just need to start, and I think Hacktoberfest is as good a reason as any.
