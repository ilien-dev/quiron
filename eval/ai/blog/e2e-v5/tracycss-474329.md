# How to Participate in the Hacktoberfest as a Code Newbie 💻

This is my first Hacktoberfest (2020) and I am still a code newbie, so if you are new to coding and wondering whether you can take part too, this post is for you.

#### Background story
When I first heard about Hacktoberfest I thought it was about hacking servers (I blame Mr. Robot for that 😅), and at that point I didn't even know HTML. It is actually a month of contributing to open source projects on GitHub.

My first pull request was rejected because I forgot to create a branch, but after that most of my pull requests got merged. Now I also open issues, mostly about accessibility: low colour contrast, input fields with no label, and duplicate alt text on images.

#### Registering and the 2020 rules
You register on the [Hacktoberfest website](https://hacktoberfest.digitalocean.com/) with your GitHub account, and there is a 14-day review window for your pull requests.

From October 3rd the rules changed and a repository now needs the `hacktoberfest` topic for your pull request to count. One of my pull requests was marked "Ineligible Repository" because of this, so check the topic before you start working. You can read the [rules update here](https://hacktoberfest.digitalocean.com/hacktoberfest-update).

Your pull request counts if it is:
- merged,
- labeled `hacktoberfest-accepted`, or
- approved by a maintainer.

I am honestly not sure how crucial the `hacktoberfest-accepted` label is.

#### Where to find projects
- The [Hacktoberfest website](https://hacktoberfest.digitalocean.com/)
- The [hacktoberfest topic on GitHub](https://github.com/topics/hacktoberfest)
- Start your own project. There is a [guide for maintainers](https://hacktoberfest.digitalocean.com/details#maintainers).

If you want to look for accessibility issues like I do, the [WAVE checker](https://wave.webaim.org/extension/) extension is a good place to start.

Before you start, read the [Hacktoberfest etiquette for contributors](https://dev.to/devteam/hacktoberfest-etiquette-for-contributors-ec6) post by the DEV team.

#### Practice with my demo repo
I made a [demo repo](https://github.com/muchirijane/learning-code-through-github-repos) you can use for your first pull request, and all you do is add a learning resource to the README. I use the cmder terminal but any terminal works.

1. Fork the repository, which creates your own copy of the project under your GitHub account.
2. Clone your fork:

```
git clone <your-fork-url>
```

3. Create a new branch. Don't skip this one because it is the reason my first pull request was rejected!

```
git checkout -b feature/react-resource
```

4. Add your resource to the README and commit your changes.
5. Push to your fork:

```
git push origin feature/react-resource
```

6. Open a pull request against the `develop` branch.

If you are new to Git and GitHub, I wrote an [earlier post for beginners](https://dev.to/tracycss/git-and-github-for-beginners-po3) that goes through the basics.

#### Please don't spam
Some people open pull requests that add nothing just to get the T-shirt or the tree, and I saw some really bad commits shared on Twitter. It wastes the maintainers' time so please don't do it. Make your pull request something that helps the project, however small.

You can find more from the [DEV team](https://dev.to/devteam) and ask questions on the [Hacktoberfest Discord](https://discord.com/invite/hacktoberfest).

If you found this post helpful you can [buy me a coffee](https://www.buymeacoffee.com/janetracy) ☕.
