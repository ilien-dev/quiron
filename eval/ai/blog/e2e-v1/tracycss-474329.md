# How to Participate in the Hacktoberfest as a Code Newbie 💻

Hacktoberfest is one of the best times of year to dip your toes into open source, especially if you're new to coding and have always felt too scared to contribute. The event runs every October and asks developers of every skill level to make pull requests to open source projects. And yes, that includes beginners. If you've been holding back, this post is for you.

## What is Hacktoberfest?

Hacktoberfest is a month-long celebration of open source software. DigitalOcean organizes it with various open source communities. The goal is simple: get more people contributing to open source projects, whether that's fixing bugs, improving docs, adding tests or building new features.

In past years, people who got a certain number of quality pull requests in during October earned some kind of reward (a T-shirt in some years, and more recently options like planting trees). But honestly, the reward isn't the point. What you get out of it is the experience, and the confidence that comes from contributing to real codebases.

## Why it's a good place for beginners to start

If you're new to coding, the idea of contributing to open source can feel like way too much. Aren't these projects run by expert developers? Won't your code get torn apart in review? What if you break something?

Hacktoberfest exists to lower that barrier. Maintainers who take part know a wave of new contributors is about to show up, many of them beginners, and a lot of projects set up newcomer-friendly issues ahead of time. The whole event was designed with people in your situation in mind.

## Step 1: Sign up

Go to the official [Hacktoberfest website](https://hacktoberfest.com) and register with your GitHub (or GitLab) account. It's free and takes about a minute. Signing up is what gets your pull requests counted for Hacktoberfest.

## Step 2: Find beginner-friendly issues

This is often the part that scares newcomers the most. There are a few reliable ways to find issues that fit your skill level, though.

### Search GitHub labels

Many repositories tag issues for newcomers with labels like:

- `good first issue`
- `beginner-friendly`
- `hacktoberfest`
- `help wanted`

You can search GitHub for these labels together with the Hacktoberfest topic:

```
is:issue is:open label:"good first issue" label:"hacktoberfest"
```

### Use curated lists

Some community-maintained lists collect beginner-friendly Hacktoberfest issues from lots of repositories, so you can browse without searching dozens of projects by hand. Search for "Hacktoberfest beginner friendly issues" and you'll find several of these lists every year.

### Don't skip the docs

Docs are a great place to start, because you don't need to know a project's code well to improve them. Fixing typos, clearing up confusing instructions, adding missing examples or improving a README all count as real contributions. They're also a low-pressure way to get used to how forking and branching work, and how you open a pull request.

## Step 3: Learn the contribution workflow

If you've never contributed to an open source project before, the basic workflow goes like this:

1. **Fork the repository**: this makes your own copy of the project under your GitHub account
2. **Clone your fork locally**: `git clone <your-fork-url>`
3. **Create a new branch**: `git checkout -b fix-typo-in-readme`
4. **Make your changes**: fix the bug, update the docs, whatever the issue asks for
5. **Commit your changes**: write a clear commit message that says what you did
6. **Push to your fork**: `git push origin fix-typo-in-readme`
7. **Open a pull request**: from the branch on your fork back to the original repository

Most repositories have a `CONTRIBUTING.md` file that explains what they expect, so check for one before you start.

## Step 4: Write a clear pull request

When you open your pull request, take a moment to say what you changed and why. A good description makes life a lot easier for the maintainer who reviews it. It also shows that you understand what you're sending in, and aren't just copying instructions without thinking.

A simple template works well:

```
## What this changes
Fixes a typo in the installation instructions section of the README.

## Why
The current instructions reference an outdated command that no longer works.
```

Keep it short and specific. You don't need to over-explain a small fix.

## Step 5: Be patient and open to feedback

Maintainers are often volunteers with a lot on their plate, so it might take a few days (or longer) for someone to look at your pull request. Don't be discouraged by the wait. And don't take it personally if a maintainer asks for changes.

Review feedback says nothing about your worth as a developer. It's a normal part of how open source works, and software development in general. Every experienced developer has had pull requests sent back with changes more times than they can count.

## Things to avoid

Sadly, Hacktoberfest has drawn some bad behavior in past years. Mostly that means low-effort spam pull requests sent in only to hit the count, like adding a random blank line. That kind of thing wastes maintainers' time and gives the whole event a bad name. Please don't do it.

Instead:

- Only send pull requests to projects that have opted in to Hacktoberfest
- Make sure your change adds something, however small
- Read a project's contribution guidelines before you submit anything
- If a maintainer labels your PR as spam, learn from it and try again somewhere else with a better contribution

## What you get beyond the shirt

Whatever physical reward is on offer in a given year, taking part in Hacktoberfest as a beginner gets you some things that last:

- **Git and GitHub practice.** Forking, branching, committing and opening pull requests start to feel normal.
- **Real codebases.** You get to see how experienced developers structure and maintain actual projects.
- **Confidence.** Going through the whole process, from finding an issue to getting a PR merged, is a big boost.
- **Something for your portfolio.** Merged pull requests are proof of your skills that anyone can check, and you can point to them in job applications.
- **People.** Talking with maintainers and other contributors can lead to mentorship and networking.

You don't need to be an expert to contribute to open source. You just need to start somewhere small, and Hacktoberfest is as good a reason as any to finally do it.
