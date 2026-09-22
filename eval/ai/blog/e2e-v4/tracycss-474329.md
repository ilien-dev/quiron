# How to Participate in the Hacktoberfest as a Code Newbie 💻

If you are new to coding and open source has always felt too scary to touch, Hacktoberfest is one of the best times of the year to dip your toes in. It runs every October and it invites developers of all skill levels to make pull requests to open source projects. Yes, that includes beginners. If you have been holding back, this post is for you.

#### What is Hacktoberfest?

It's a month-long celebration of open source software, organized by DigitalOcean together with different open source communities. The goal is to get more people contributing to open source projects, whether that's fixing bugs, improving documentation, adding tests or building new features.

In the past, people who completed a certain number of quality pull requests during October got some kind of reward (a T-shirt in earlier years, and more recently options like planting trees). But I don't think the reward is the point. The experience you get and the confidence you build by contributing to real codebases are worth much more.

#### Why it's good for beginners

When you are new, contributing to open source can feel like too much. Aren't these projects run by expert developers? Won't my code get torn apart in a review? What if I break something?

Hacktoberfest is made to lower that barrier. Maintainers who take part know a wave of new contributors is coming, many of them beginners, and a lot of projects create newcomer-friendly issues on purpose to get ready for them. The event was designed with people in your situation in mind.

#### Step 1: Sign up

Go to the official [Hacktoberfest website](https://hacktoberfest.com) and register with your GitHub (or GitLab) account. It's free and takes a minute. This is what makes your pull requests count toward Hacktoberfest.

#### Step 2: Find beginner-friendly issues

This is the part that scares newcomers the most, but there are a few ways to find issues that fit your level.

Many repositories tag issues for newcomers with labels like:

- `good first issue`
- `beginner-friendly`
- `hacktoberfest`
- `help wanted`

You can search GitHub for these labels together with the Hacktoberfest topic:

```
is:issue is:open label:"good first issue" label:"hacktoberfest"
```

There are also community-maintained lists that collect beginner-friendly Hacktoberfest issues from many repositories, so you don't have to search dozens of projects one by one. Search for "Hacktoberfest beginner friendly issues" and you will find several of them every year.

And don't skip documentation! Docs are a great place to start because you don't need to know the project's code well. Fixing typos, making confusing instructions clearer, adding missing examples or improving a README all count as real contributions. They are also a low-pressure way to get used to forking, branching and opening a pull request.

#### Step 3: Learn the contribution workflow

If you have never contributed to an open source project before, the basic workflow looks like this:

1. **Fork the repository** (this creates your own copy of the project under your GitHub account)
2. **Clone your fork locally**: `git clone <your-fork-url>`
3. **Create a new branch**: `git checkout -b fix-typo-in-readme`
4. **Make your changes**: fix the bug, update the docs, whatever the issue asks for
5. **Commit your changes** with a clear commit message that says what you did
6. **Push to your fork**: `git push origin fix-typo-in-readme`
7. **Open a pull request** from your fork's branch back to the original repository

Most repositories have a `CONTRIBUTING.md` file that explains what they expect, so check for one before you start.

#### Step 4: Write a clear pull request

When you open your pull request, take a moment to explain what you changed and why. A good description makes life much easier for the maintainer who reviews it, and it shows you understand what you are submitting and didn't just copy instructions.

A simple template works well:

```
## What this changes
Fixes a typo in the installation instructions section of the README.

## Why
The current instructions reference an outdated command that no longer works.
```

Keep it short. You don't need to over-explain a small fix.

#### Step 5: Be patient and open to feedback

Maintainers are often volunteers with a lot on their plate, so it might take a few days (or longer) before someone reviews your pull request. Don't be discouraged by the wait, and don't take it personally if a maintainer asks for changes. Review feedback is not a judgment of your worth as a developer. It's a normal part of how open source, and software development in general, works. Every experienced developer has had pull requests sent back with requested changes more times than they can count.

#### Things to avoid

Sadly, Hacktoberfest has attracted some bad behavior in past years, mostly low-effort spam pull requests made only to hit the quota (like adding a random blank line). That wastes maintainers' time and gives the whole event a bad name. Please don't do this. Instead:

- Only submit pull requests to projects that have opted into Hacktoberfest
- Make sure your contribution adds value, even if it's small
- Read a project's contribution guidelines before you submit anything
- If a maintainer labels your PR as spam, learn from it and try again somewhere else with a more thoughtful contribution

#### What you get out of it

Whatever the physical reward is in a given year, taking part in Hacktoberfest as a beginner gives you things that last. Forking, branching, committing and opening pull requests start to feel normal, so you get real Git and GitHub practice. You see how experienced developers structure and maintain real projects. Going through the whole process, from finding an issue to getting a PR merged, is a big confidence boost. Merged pull requests are proof of your skills that you can point to in job applications. And talking with maintainers and other contributors can lead to mentorship and networking.

You don't need to be an expert to contribute to open source, you just need to start. Look for beginner-friendly issues, be thoughtful about what you submit, and don't be afraid of feedback. Hacktoberfest is as good a reason as any to finally take that first step.
