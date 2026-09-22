# How to Participate in the Hacktoberfest as a Code Newbie 💻

Hacktoberfest is one of the best times of the year to try open source, especially if you're new to coding and contributing has always felt too scary. It runs every October and gets developers of every level to open pull requests on open source projects. Yes, that includes beginners.

DigitalOcean organizes it together with open source communities, and the goal is to get more people contributing, whether that's fixing bugs, improving docs, adding tests or building new features. In past years people who finished a certain number of quality pull requests in October got a reward: a T-shirt some years, and more recently options like planting trees. The reward isn't really the point, though. What you get out of it is the experience, and the confidence that comes from working on real codebases.

## Why it's a good place to start

If you're new to coding, the idea of contributing to open source can feel like a lot. Aren't these projects run by experts? Won't your code get torn apart in review? What if you break something?

Hacktoberfest exists to lower that barrier. Maintainers who take part know a wave of new contributors is coming, many of them beginners, and a lot of projects set up newcomer-friendly issues ahead of time. The whole event is built with people in your spot in mind.

## Signing up and finding an issue

Go to the official [Hacktoberfest website](https://hacktoberfest.com) and register with your GitHub (or GitLab) account. It's free and takes a minute, and it's what makes your pull requests count toward Hacktoberfest.

Finding an issue is often the part newcomers find scariest. A lot of repositories tag issues for newcomers with labels like these:

- `good first issue`
- `beginner-friendly`
- `hacktoberfest`
- `help wanted`

You can search GitHub for those labels together with the Hacktoberfest topic:

```
is:issue is:open label:"good first issue" label:"hacktoberfest"
```

There are also community lists that collect beginner-friendly Hacktoberfest issues from many repositories, so you don't have to dig through dozens of projects by hand. Search for "Hacktoberfest beginner friendly issues" and you'll find several of them each year.

And don't skip documentation. You don't need to know a project's code well to fix a typo, clarify confusing instructions, add a missing example or improve a README, and those are real contributions. They're also a low-pressure way to get used to forking, branching and opening a pull request.

## The contribution workflow

If you've never contributed to an open source project, the basic steps are:

1. **Fork the repository.** This makes your own copy of the project under your GitHub account.
2. **Clone your fork locally:** `git clone <your-fork-url>`
3. **Create a new branch:** `git checkout -b fix-typo-in-readme`
4. **Make your changes.** Fix the bug, update the docs, whatever the issue calls for.
5. **Commit your changes** with a clear commit message that says what you did.
6. **Push to your fork:** `git push origin fix-typo-in-readme`
7. **Open a pull request** from your fork's branch back to the original repository.

Most repositories have a `CONTRIBUTING.md` file that explains what they expect, so look for one before you start.

When you open the pull request, say what you changed and why. A good description makes the maintainer's review a lot easier, and it shows you understand what you're submitting and aren't just copying instructions. Something this simple works:

```
## What this changes
Fixes a typo in the installation instructions section of the README.

## Why
The current instructions reference an outdated command that no longer works.
```

Keep it short and specific. A small fix doesn't need a long explanation.

## Waiting and feedback

Maintainers are often volunteers with a lot on their plate, so a review can take a few days or longer. Don't be discouraged by the wait, and don't take it personally if a maintainer asks for changes. Review feedback says nothing about your worth as a developer. It's a normal part of how open source works, and how software development works in general. Every experienced developer has had pull requests sent back more times than they can count.

## Please don't spam

In past years Hacktoberfest has drawn some bad behavior, mostly low-effort pull requests sent just to hit the quota (adding a random blank line, for example). That wastes maintainers' time and gives the whole event a bad name. Please don't do it. Only send pull requests to projects that have opted into Hacktoberfest, make sure your change adds something (however small), and read the project's contribution guidelines first. If a maintainer labels your PR as spam, learn from it and try again somewhere else with a more thoughtful contribution.

## What you get out of it

Whatever the physical reward is in a given year, taking part as a beginner gives you things that last. Forking, branching, committing and opening pull requests become second nature. You get to see how experienced developers structure and maintain real projects. Getting through the whole process, from finding an issue to getting a PR merged, is a real confidence boost. Merged pull requests are concrete proof of your skills that you can point to in job applications. And talking with maintainers and other contributors can lead to mentorship and new contacts.

You don't need to be an expert to contribute something useful to open source. You just need to start, and Hacktoberfest is as good a reason as any.
