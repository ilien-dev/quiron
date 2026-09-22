# Development log: one month in

It's been exactly one month since I started working on this project, and I figured it was a good time to stop and write down where the project stands. Partly this is for anyone following along. Partly it is for me, because the details of early decisions are already starting to fade.

## Where I started

When I kicked things off, the goal was simple on paper: build a small, fast command-line tool for managing project notes that live alongside the code. The notes would be plain text files in a clear folder structure, and the tool would have a handful of commands for creating notes, searching notes and linking notes to each other.

I gave myself one rule for the first month, which was to get something usable even if it was rough. I have abandoned too many side projects by spending weeks on architecture before writing a single feature.

## What got done

Here's what is working right now:

- `notes new "title"` creates a Markdown file with a timestamp and some front matter.
- `notes list` and `notes search <term>` both work, with basic filtering by tag.
- You can reference another note with `[[note-name]]`, and `notes links` shows what points where.
- A small TOML configuration file lets you set the notes directory and the default editor.

The list is short. Still, I have been using the tool every day for about two weeks now, and that was the milestone I was hoping for.

## What went well

Writing tests early was the first thing. I resisted it at first, but the tests for the parser saved me at least three times when I refactored how front matter is read, and having them made me more willing to change things, which matters a lot at this stage of development.

Keeping the scope small was the second. I had a long list of "wouldn't it be cool if" features, so I wrote them all down in a `LATER.md` file and then ignored the file. That file is now 40 lines long. Not one of those items is done, and I think that is exactly why the core works.

Using the tool myself was the third. Dogfooding surfaced problems I never would have thought of, like how annoying it is when search results aren't sorted by date.

## What was harder than expected

Search performance was the big one. My first version just read every file on every search. That was fine with 20 notes, but when I generated 5,000 test notes the search fell over. I've since added a simple index that rebuilds when files change, which was a considerable improvement in search time, though I still need to benchmark the search properly.

Windows path handling bit me more than once, so now the standard library handles every path for me and I don't do any string manipulation on paths myself.

And naming things. I have renamed the project twice and I'm still not sure I like the current name.

## What's next

For month two I want to focus on:

1. Better search, including fuzzy matching and searching inside specific tags.
2. A proper install story, so people can try the tool without cloning the repo.
3. Documentation, starting with a real README and a few usage examples.
4. Feedback from at least a few other people who aren't me.

## Closing thoughts

One month in, what makes me happiest is that the project still feels alive. I'm excited to open it up in the evening, and I think that is mostly because I kept the scope tight and shipped something I actually use.

If you have thoughts or ideas, or want to try the tool, leave a comment. I'll be back with another log at the two-month mark.
