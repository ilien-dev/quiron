# Development Log: One Month In

It's been exactly one month since I started working on this project, and I figured it was a good time to stop, look back, and write down where things stand. Partly this is for anyone following along, and partly it's for me, because I've already noticed how quickly the details of early decisions start to fade.

## Where I Started

When I kicked things off, the goal was simple on paper: build a small, fast command-line tool for managing project notes that live alongside the code. Plain text files, a clear folder structure, and a handful of commands for creating, searching, and linking notes. Nothing fancy.

I gave myself one rule for the first month: get something usable, even if it's rough. I've abandoned too many side projects by spending weeks on architecture before writing a single feature.

## What Got Done

Here's what's working right now:

- **Creating notes.** `notes new "title"` creates a Markdown file with a timestamp and some front matter.
- **Listing and searching.** `notes list` and `notes search <term>` both work, with basic filtering by tag.
- **Linking.** You can reference another note with `[[note-name]]`, and `notes links` shows what points where.
- **Config file.** A small TOML config lets you set the notes directory and default editor.

It's not much, but I've been using it every day for about two weeks now, which was the real milestone I was hoping for.

## What Went Well

**Writing tests early.** I resisted this at first, but having tests for the parser saved me at least three times when I refactored how front matter is read. It also made me more willing to change things, which matters a lot this early.

**Keeping scope small.** I had a long list of "wouldn't it be cool if" features. I wrote them all down in a `LATER.md` file and then ignored it. That file is now 40 lines long. Not one of those items is done, and I think that's exactly why the core works.

**Using it myself.** Dogfooding surfaced problems I never would have thought of, like how annoying it is when search results aren't sorted by date.

## What Was Harder Than Expected

**Search performance.** My first version just read every file on every search. That was fine with 20 notes, but I generated 5,000 test notes and it fell over. I've since added a simple index that rebuilds when files change, which brought search time down considerably, though I still need to benchmark it properly.

**Cross-platform paths.** Windows path handling bit me more than once. I'm now leaning on the standard library for everything path-related instead of doing any string manipulation myself.

**Naming things.** I've renamed the project twice. I'm still not sure I like the current name.

## What's Next

For month two, I want to focus on:

1. **Better search**, including fuzzy matching and searching inside specific tags.
2. **A proper install story**, so people can try it without cloning the repo.
3. **Documentation**, starting with a real README and a few usage examples.
4. **Getting feedback** from at least a few other people who aren't me.

## Closing Thoughts

One month in, the thing I'm happiest about isn't any particular feature. It's that the project still feels alive. I'm excited to open it up in the evening, and I think that's mostly because I kept the scope tight and shipped something I actually use.

If you've got thoughts, ideas, or want to try it out, let me know in the comments. I'll be back with another log at the two-month mark.
