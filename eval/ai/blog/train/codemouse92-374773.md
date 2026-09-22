# Goodbye Master, Hello...What?

For decades, Git repositories have commonly used `master` as the name of their default branch. It became so familiar that many developers stopped seeing it as a choice at all. You cloned a repository, made a branch, opened a pull request, and merged it back into `master`.

Then the industry began reconsidering that default.

GitHub switched the default branch name for new repositories from `master` to `main` in 2020. GitLab, Bitbucket, and many individual projects made similar changes. The motivation was straightforward: use clearer, more inclusive language where changing it carries relatively little cost.

But removing one default creates an obvious question: what should replace it?

## The Popular Answer: `main`

Today, `main` is the safest choice.

It is short, descriptive, and widely recognized. Major hosting platforms use it by default, tools increasingly expect it, and new developers are likely to understand it immediately. If you are creating a repository and have no special naming requirements, this is probably all you need:

```bash
git init -b main
```

For an existing local repository, you can rename the branch with:

```bash
git branch -m master main
git push -u origin main
```

Afterward, update the default branch in your hosting platform before removing the old remote branch:

```bash
git push origin --delete master
```

The commands are easy. The surrounding systems are where things get interesting.

## Other Reasonable Names

`main` is not the only option. A branch name can communicate something about how a project works.

Some teams use `trunk`, especially when practicing trunk-based development. It suggests a central line of development from which short-lived branches emerge.

Others use `stable`, `production`, or `release`. These names can be useful, but they also imply specific guarantees. Is everything on `production` actually deployed? Does `stable` contain only tested code? If the answer changes depending on the day, the name may create more confusion than clarity.

Names such as `develop` make sense in branching models where development work is collected separately from release-ready code. However, making `develop` the default branch can surprise contributors who assume that the default represents the project’s primary history.

The best name is not the cleverest one. It is the one whose meaning remains obvious six months later.

## Renaming Is More Than a Git Command

A default branch often appears in places beyond Git itself:

- CI/CD workflow triggers
- deployment rules
- branch protection settings
- documentation and badges
- scripts and configuration files
- open pull requests
- local clones
- external integrations

Before deleting the old branch, search your repository for references:

```bash
git grep master
```

Also inspect settings maintained outside the repository. A pipeline configured through a hosting dashboard will not appear in a text search.

Collaborators with existing clones may need to run:

```bash
git fetch origin
git branch -m master main
git branch -u origin/main main
git remote set-head origin -a
```

Clear communication matters more than the rename itself. Tell contributors what is changing, when it will happen, and whether they need to take action.

## A Small Change, Done Thoughtfully

Renaming a branch will not solve inequality in technology, and nobody should pretend otherwise. It is a modest vocabulary change, not a substitute for inclusive hiring, accessible communities, fair compensation, or respectful collaboration.

Still, small improvements do not have to solve everything to be worthwhile.

Language evolves. Tools evolve. Conventions evolve. We already rename confusing variables, replace outdated APIs, and improve defaults when we find better ones. Branch names can receive the same treatment.

So: goodbye, `master`. Hello, `main`—or `trunk`, or another name your team chooses deliberately.

Just remember to update the deployment pipeline.