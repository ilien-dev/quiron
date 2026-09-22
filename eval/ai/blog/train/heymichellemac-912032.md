# How I Use Obsidian as a Creative – Part 2

In Part 1, I talked about why I moved my creative life into Obsidian: the local Markdown files, the linking, and the freedom to build a system that fits how my brain actually works instead of forcing myself into someone else's template. I covered my basic folder setup and how I capture ideas quickly before they vanish.

This time, I want to go deeper into the day-to-day. How do I actually use Obsidian when I'm working on creative projects? What does my workflow look like from the spark of an idea to something finished? And which plugins and habits have made the biggest difference?

Grab a coffee. This one's a bit longer.

## A quick recap of my setup

For anyone who skipped Part 1, here's the short version of my vault structure:

- **Inbox** – where everything lands first
- **Projects** – active creative work, one folder per project
- **Library** – notes on books, films, articles, and other inspiration
- **Seeds** – half-formed ideas that aren't projects yet
- **Journal** – daily notes
- **Archive** – finished or abandoned work

I try not to over-organize. Folders are for rough sorting; links and tags do the heavy lifting.

## From seed to project

The most important thing Obsidian has done for me is give ideas somewhere to *grow*.

I used to write ideas in random notebooks, phone notes, and the backs of receipts. Most of them died there. Now, every idea becomes a note in my Seeds folder, even if it's only one sentence.

Here's what a typical seed note looks like when I first create it:

```markdown
# A short story about a lighthouse keeper who collects lost radio signals

Created: 2022-03-14
Tags: #seed #fiction

- What if the signals are from the future?
- Tone: quiet, lonely, a bit hopeful
```

That's it. No pressure to make it good.

The magic happens over time. When I'm reading, journaling, or working on something else and I stumble onto something related, I link it back. A note about a documentary on shipping forecasts links to the lighthouse idea. A journal entry about feeling isolated links to it. A reference image I saved links to it.

After a few weeks or months, I'll open the seed and check the backlinks panel. Sometimes there's nothing, and that's fine; the idea wasn't ready. But sometimes there are ten or fifteen connections, and I can see the idea has gathered real weight. That's when it graduates to a project.

## Project notes

When something becomes a project, it gets its own folder with a main hub note. My hub note template looks like this:

```markdown
# Project: {{title}}

Status: #status/active
Started: {{date}}
Medium: 

## What is this?

## Why does it matter to me?

## Inspiration
- 

## Open questions
- 

## Pieces
- 

## Log
```

The "Why does it matter to me?" section is the one I'd least want to lose. When I get stuck halfway through a project (and I always do), rereading my original answer reminds me why I started.

The "Pieces" section links out to other notes: character sketches, drafts, research, mood boards, scene outlines. Each of those is its own note, so I can link to them from anywhere and they don't get buried inside one giant document.

The "Log" is a running list of dated entries where I jot down what I worked on and how it felt. It's surprisingly motivating to scroll back and see progress over time.

## Using daily notes as a creative journal

Daily notes are the heartbeat of my vault. Every morning, I open today's note (I use the **Periodic Notes** plugin with a template), and it has a few simple prompts:

```markdown
# {{date:dddd, MMMM D}}

## Morning pages

## What I'm working on today

## Things I noticed

## Links
```

**Morning pages** are a loose version of the Julia Cameron practice. I just write whatever's in my head for ten minutes or so. It clears the noise out.

**Things I noticed** is my favorite section. It's where I note small observations: a conversation overheard on the bus, a colour combination on a shop sign, a phrase from a podcast. These are the raw materials for creative work, and having a daily habit of writing them down has trained me to notice more.

Whenever something in a daily note connects to a project or seed, I link it. Over time, my daily notes become a web of connections back into my creative work.

## Plugins that earn their place

I've tried a lot of plugins, and I've uninstalled most of them. These are the ones I actually rely on:

**Templater.** More powerful than the core templates plugin. I use it to auto-fill dates, prompt me for a project title, and move new notes into the right folder automatically.

**Dataview.** This lets me query my vault like a database. For example, I have a dashboard note that lists every active project:

````markdown
```dataview
TABLE medium, started
FROM "Projects"
WHERE contains(file.tags, "#status/active")
SORT started DESC
```
````

I also use it to surface seed notes I haven't touched in a while, which is a great way to rediscover forgotten ideas.

**Excalidraw.** For sketching, diagramming plot structures, or making rough visual layouts. It lives right inside my vault, and I can link to drawings from any note.

**Kanban.** For projects with lots of moving pieces, like a zine or a video, I use a kanban board to track tasks. It's just a Markdown file under the hood, which I love.

**Calendar.** A small sidebar calendar that makes jumping between daily notes easy.

**Canvas** (core feature). I use Canvas as a digital corkboard, pinning notes, images, and links onto an infinite board to see how things connect. It's incredible for outlining a story or planning a series.

## Handling inspiration without hoarding it

One trap I fell into early on was collecting *everything*. I'd clip every article, save every image, and highlight every book. My vault got huge and I never looked at most of it.

Now I follow one rule: **if I save something, I have to write at least one line about why.**

So instead of just pasting a link to a painting, my Library note says something like:

> The way the light hits only half the room makes the empty chair feel like it's waiting for someone. Could use this feeling for the lighthouse story.

That one line turns passive collecting into active thinking, and it gives me a reason to link the note somewhere useful.

## Weekly review

Every Sunday, I do a short review. I have a weekly note template that pulls in:

- The daily notes from the past week
- Any projects I logged progress on
- Seeds created this week

I skim through, link anything that needs linking, move finished projects to the Archive, and pick one or two things to focus on for the coming week. It takes about twenty minutes and it keeps the vault from turning into a junk drawer.

## What hasn't worked

To be honest about it, a few things didn't stick for me:

- **Elaborate tagging systems.** I tried nested tags for mood, medium, genre, and theme. I never kept them consistent. Now I use a handful of simple tags and rely on links instead.
- **Writing full drafts in Obsidian.** For long-form writing, I still prefer a dedicated writing app with distraction-free mode. I draft there, then paste finished sections back into Obsidian for reference. Your mileage may vary; plenty of people write whole novels in Obsidian.
- **Too many plugins.** Every plugin adds a bit of friction and a bit of fragility. Fewer is better.

## Syncing and backups

Since my whole creative life lives in this vault, backups matter. I use Obsidian Sync to keep things consistent across my laptop, tablet, and phone, and I also back up the vault folder to an external drive once a week. Because it's all plain Markdown files, I'm never locked in. If Obsidian disappeared tomorrow, my notes would still open in any text editor.

## Final thoughts

The biggest shift Obsidian gave me wasn't a specific plugin or template. It was a change in how I treat ideas. Instead of expecting them to arrive fully formed, I plant them, connect them, and let them grow. Some never sprout. Others turn into the work I'm proudest of.

If you're a creative person thinking about trying Obsidian, my advice is to start small. A daily note, a seeds folder, and the habit of linking things together will get you surprisingly far. You can always add complexity later.

In Part 3, I'll share how I use Obsidian specifically for planning and publishing content, including how I manage my blog posts and newsletter from idea to publish. See you then!
