# How I Use Obsidian As A Creative - Part 2

In Part 1, I walked through the foundation: how my vault is structured, why I stopped obsessing over folders, and how daily notes became the front door for everything I make. If you haven't read it, the short version is that I treat Obsidian less like a filing cabinet and more like a studio floor. Things get messy, and that's fine, as long as I can find what I need when I need it.

This part covers what happens *after* an idea lands in the vault. Collecting ideas has never been my problem. Most creatives I know have the same issue: hundreds of half-thoughts, sketches, and "this could be something" notes that never become anything. Over the past year I've built a workflow that moves ideas from raw spark to finished work, and Obsidian sits at the center of it.

Here's how it works.

---

## 1. The Idea Pipeline: Seed → Sprout → Project

Every creative idea in my vault has a stage, tracked with a single frontmatter property:

```yaml
---
stage: seed
type: essay
created: 2026-10-03
---
```

The three stages are:

- **Seed** — A raw idea. Sometimes one sentence. Sometimes a voice memo transcription. No pressure, no expectations.
- **Sprout** — An idea I've returned to at least twice and added something to. It's shown it has legs.
- **Project** — Something I've committed to finishing, with a rough scope and a next action.

The rule that makes this work is simple: **an idea can only be promoted, never forced.** I don't decide upfront that something will be a project. I let it earn its way there by repeatedly pulling me back.

This sounds small, but it removed a huge amount of guilt. A seed that never sprouts isn't a failure. It's compost. Some of my best pieces came from mashing two forgotten seeds together six months after I wrote them.

---

## 2. Dataview Dashboards That Actually Get Used

I resisted Dataview for a long time because every dashboard I saw online looked like a cockpit. I didn't want to maintain a control panel. I wanted to make things.

What finally clicked was building **one** dashboard with **three** queries and nothing else. It's my vault's homepage:

````markdown
## 🌱 Sprouts worth revisiting
```dataview
TABLE type, file.mtime AS "Last touched"
FROM ""
WHERE stage = "sprout"
SORT file.mtime ASC
LIMIT 10
```

## 🔨 Active projects
```dataview
TABLE type, next-action AS "Next"
FROM ""
WHERE stage = "project" AND status != "done"
SORT priority DESC
```

## 🎲 Random seed of the day
```dataviewjs
const seeds = dv.pages().where(p => p.stage === "seed").array();
const pick = seeds[Math.floor(Math.random() * seeds.length)];
if (pick) dv.paragraph(dv.fileLink(pick.file.path));
```
````

The sprouts query is sorted **oldest first** on purpose. The ideas I've neglected longest float to the top, which nudges me to either push them forward or let them go.

The random seed is my favorite part. Every morning I get one forgotten idea served back to me. Most days I glance at it and move on. But every couple of weeks, it lines up with whatever I'm working on and something clicks.

---

## 3. Canvas for the Messy Middle

Every creative project has a stage where linear notes stop working. For writing, it's when I'm figuring out structure. For visual work, it's moodboarding. For anything with multiple parts, it's when I need to see the whole thing at once.

That's where Canvas comes in.

When a project gets promoted, I create a canvas for it alongside the main note. On it I drop:

- **Reference images** dragged straight in from my attachments folder
- **Existing notes** from the vault that feel related, embedded as cards
- **Loose text cards** for fragments that don't deserve their own note yet
- **Groups** to cluster things by theme, act, section, or mood

For a long essay I wrote earlier this year, the canvas started as about forty scattered cards. Over a week, I dragged them into five groups, and those groups became the five sections of the piece. I didn't outline it. I *arranged* it, which is a very different mental mode, and one that suits me much better.

A tip that took me too long to learn: **don't try to keep canvases tidy.** A canvas is a workbench. When the project ships, I take a screenshot for my archive and stop maintaining it. The finished work is the artifact, not the board.

---

## 4. Templates That Ask Questions

I use the Templater plugin, but not for elaborate automation. My templates are mostly **prompts**: questions I'd otherwise forget to ask myself.

Here's my project template:

```markdown
---
stage: project
type: <% tp.system.suggester(["essay", "illustration", "music", "video", "other"], ["essay", "illustration", "music", "video", "other"]) %>
status: active
priority: 2
next-action:
started: <% tp.date.now("YYYY-MM-DD") %>
---

# <% tp.file.title %>

## Why does this want to exist?

## What does "done" look like?

## What am I afraid this will turn into?

## Related seeds
- 

## Log
### <% tp.date.now("YYYY-MM-DD") %>
- Promoted to project.
```

The question **"What am I afraid this will turn into?"** has saved more projects than any productivity system. Writing down "I'm afraid this becomes a 6,000-word monster nobody reads" or "I'm afraid I'll over-render this until it looks stiff" gives me something concrete to watch for. When I notice it happening, I already have the warning written in my own words.

The **Log** section matters too. Every work session gets a dated line or two. It's not journaling, just breadcrumbs. When I come back after two weeks away, I read the last three entries and I'm back in it within minutes instead of an hour.

---

## 5. Linking Themes, Not Just Topics

Early on, my links were literal: a note about a painting linked to `[[Painting]]`, a note about a short story linked to `[[Fiction]]`. Technically connected, creatively useless.

What changed things was creating **theme notes**, notes about the ideas I keep circling back to regardless of medium. A few of mine:

- `[[Things that outlive their purpose]]`
- `[[Quiet competence]]`
- `[[Maps that lie]]`
- `[[Rooms after people leave]]`

These aren't categories. They're obsessions. When I write a seed, I ask whether it touches one of them. Over time, each theme note's backlinks panel became a cross-medium collection: a photo I took, a paragraph from a book, a song lyric, a half-finished sketch, a story premise.

Opening one of those notes and scrolling the backlinks is the closest thing I've found to looking inside my own head. It's also where the most original work comes from, because the connections cut across formats in ways I'd never plan.

If you take one thing from this post, make it this: **link to what you care about, not what things are.**

---

## 6. Shipping: The "Out the Door" Note

The last piece of the pipeline is what happens when something's finished. I used to just mark it done and move on. Now every finished project gets a short retrospective, appended to the project note:

```markdown
## Out the door
- **Shipped:** 2026-09-14
- **Where:** personal site, newsletter
- **What surprised me:**
- **What I'd steal for next time:**
- **Seeds this created:**
```

That last line is the important one. Finishing a project almost always generates new ideas: tangents I cut, questions I didn't answer, techniques I want to push further. Each one becomes a new seed, linked back to the project that spawned it.

That closes the loop. Finished work feeds the pipeline instead of just leaving it.

---

## A Few Plugins I Actually Use

People always ask, so here's the full list, deliberately short:

- **Dataview** for the dashboard
- **Templater** for the question-driven templates
- **Calendar** for jumping between daily notes
- **Excalidraw** for quick sketches that live alongside text
- **Image Converter** to keep attachments from bloating the vault

That's it. Every plugin I removed made the vault faster and made me more likely to open it.

---

## What I'd Tell Someone Starting Out

If you're a creative person setting up Obsidian, here's the honest advice I wish I'd had:

1. **Don't build a system before you have a problem.** Let friction tell you what to add.
2. **Make capture effortless and organization optional.** You can always link things later. You can't recover an idea you didn't write down.
3. **Give ideas permission to die.** A vault full of seeds isn't a backlog. It's soil.
4. **Revisit on purpose.** Random notes, oldest-first sorting, theme backlinks: anything that resurfaces old material is worth more than any capture method.
5. **Finish things.** The vault exists to serve the work, not the other way around.

In Part 3, I'll get into how I use Obsidian for the business side of being a creative: tracking clients, invoices, pitches, and making sure the admin doesn't eat the art.

Thanks for reading. If you've got a creative workflow in Obsidian that works for you, I'd genuinely love to hear about it in the comments.

---

Since I don't have your Part 1, the recap in the intro and the Part 3 teaser are placeholders. Adjust them to match what you actually covered and plan to cover. The body is about 1,400 words without the code blocks. The plugin list and examples are also generic, so swap in your real setup and themes to make it yours.
