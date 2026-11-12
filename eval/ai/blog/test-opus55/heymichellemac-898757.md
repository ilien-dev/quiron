Writing a book is hard. Getting people to *find* the book turns out to be its own project.

When my manuscript was finally done, I realized I had no good place to send people. A tweet thread disappears in a day. A retailer page is cluttered with someone else's recommendations. I wanted one URL I owned, that loaded fast, explained the book in seconds, and turned curious visitors into readers.

So I built a landing page. Not a full author website with a blog, a bio page, and a media kit. Just one focused page with one job.

Here's the seven-step process I followed, what I'd do again, and a few code snippets you can borrow.

---

## Step 1: Decide on the *one* thing the page should do

Before touching any code, I wrote one sentence on a sticky note:

> "This page exists to get visitors to ________."

Possible answers include:

- Pre-order the book
- Buy it now
- Join an email list for launch updates
- Download a free sample chapter

You can technically do all of these, but every extra call to action dilutes the others. I picked **"download a free sample chapter"** as the primary goal, with "buy now" as a secondary link. A sample chapter is low-commitment for the visitor, and it gets me an email address, which outlasts any single sale.

Every later decision got checked against that sticky note. Should I add a section about my other projects? Does it help people download the chapter? No? Cut it.

**Takeaway:** a landing page with one goal will almost always outperform a page that tries to do everything.

---

## Step 2: Write the copy before you design anything

This was the step that changed the most for me. My instinct as a developer was to open a code editor and start with the hero section. Instead, I opened a plain text file and wrote every word that would appear on the page.

I answered these questions, in this order:

1. **Who is this book for?** Be specific. "Developers" is too broad. "Self-taught developers trying to land their first job" is something a reader can recognize themselves in.
2. **What problem does it solve for them?**
3. **What will they be able to do after reading it?**
4. **Why should they trust me to teach it?**
5. **What's inside?** (Chapter highlights, not the full table of contents.)
6. **What do other readers say?**
7. **What objections might they have?** (These become the FAQ.)

Writing copy first forces clarity. If you can't explain the book in a headline and two sentences, no amount of gradients and animations will fix that.

My headline went through about a dozen drafts. The winning pattern was simple: **outcome + audience**. Something like *"Ship your first real project, a practical guide for self-taught developers."* Clever headlines were fun to write, but clear ones were easier to understand at a glance.

---

## Step 3: Structure the page around a reader's questions

With the copy written, the page structure basically fell out of it. Here's the section order I landed on:

1. **Hero:** headline, subheadline, book cover, primary CTA
2. **The problem:** a short paragraph the reader nods along to
3. **What you'll learn:** 4–6 benefit-focused bullet points
4. **Sample chapter CTA:** repeated, with a short form
5. **About the author:** brief, relevant credibility
6. **Testimonials:** from early readers or beta reviewers
7. **FAQ:** format, length, refunds, who it's *not* for
8. **Final CTA:** one more chance to convert

The rule of thumb I followed: **a CTA should be visible no matter where the reader stops scrolling.** Someone who's convinced after the hero shouldn't have to scroll to the bottom to act. Someone who needs the FAQ to decide should find a button right after it.

I sketched this as a wireframe on paper first. Ten minutes with a pen saved me hours of moving divs around.

---

## Step 4: Pick a boring, fast tech stack

It's tempting to treat a side project as an excuse to try the newest framework. For a landing page, I'd push back on that. You want:

- Near-instant load times
- Great SEO and social previews out of the box
- Cheap (ideally free) hosting
- Something you'll still understand in a year when you need to update the price

I went with a **static site**: plain HTML and CSS with a sprinkle of JavaScript, deployed to a static host. Astro, Eleventy, or a simple Vite setup are all great choices if you want components and a build step. Netlify, Vercel, Cloudflare Pages, and GitHub Pages all offer free tiers that are more than enough for a book page.

The page doesn't need a database, user accounts, or server-side rendering. Every dependency you skip is one less thing that breaks before launch day.

---

## Step 5: Build it mobile-first, and treat the cover like a hero

A large share of your traffic will come from social media links opened on phones. I designed for a narrow screen first and expanded from there.

A few things that made a real difference:

**Optimize the book cover.** It's the most important image on the page and usually the heaviest. I exported it in modern formats and let the browser pick:

```html
<picture>
  <source srcset="/img/cover.avif" type="image/avif" />
  <source srcset="/img/cover.webp" type="image/webp" />
  <img
    src="/img/cover.jpg"
    alt="Cover of the book: Ship Your First Real Project"
    width="600"
    height="900"
    fetchpriority="high"
  />
</picture>
```

Setting `width` and `height` prevents layout shift, and `fetchpriority="high"` tells the browser this image matters for the first paint.

**Keep typography readable.** Long-form copy on a landing page needs comfortable line lengths:

```css
body {
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: clamp(1rem, 0.95rem + 0.3vw, 1.15rem);
  line-height: 1.6;
}

.prose {
  max-width: 65ch;
  margin-inline: auto;
}
```

Using system fonts also means no web font download, which is one less request blocking your text.

**Make the CTA button unmissable.** One accent color, used *only* for calls to action. If everything is highlighted, nothing is.

---

## Step 6: Wire up the conversion plumbing

A beautiful page that doesn't capture anything is just a brochure. This step is about making sure the goal from Step 1 actually works end to end.

### Email capture

I used a hosted newsletter service rather than building my own. Most of them (Buttondown, ConvertKit/Kit, MailerLite, and similar) give you a plain HTML form endpoint, so there's no SDK to install:

```html
<form action="https://your-newsletter-provider.example/subscribe" method="post">
  <label for="email">Get the first chapter free:</label>
  <input
    id="email"
    name="email"
    type="email"
    autocomplete="email"
    required
    placeholder="you@example.com"
  />
  <button type="submit">Send me the chapter</button>
</form>
```

I then set up an automated welcome email that delivers the sample chapter PDF immediately. **Test this with a real address.** I found a broken download link in my own welcome email during testing, which would have been embarrassing to discover from a reader.

### Purchase links

Wherever the book is sold, link directly to the specific product page, not the store's homepage. If you sell on multiple platforms, a small row of buttons works better than a dropdown.

### Social previews

When people share your page, the preview card *is* your ad. Don't skip Open Graph tags:

```html
<meta property="og:title" content="Ship Your First Real Project" />
<meta property="og:description" content="A practical guide for self-taught developers. Get the first chapter free." />
<meta property="og:image" content="https://yourbook.example/img/og-card.png" />
<meta property="og:url" content="https://yourbook.example/" />
<meta name="twitter:card" content="summary_large_image" />
```

I made a dedicated 1200×630 image with the cover and headline instead of reusing the tall cover image, which gets awkwardly cropped on most platforms.

---

## Step 7: Measure, launch, and keep iterating

Launch day isn't the finish line, it's the first time you get real data.

**Before launch, I ran through a checklist:**

- [ ] Lighthouse scores checked on mobile (performance, accessibility, SEO)
- [ ] Every link and button clicked on a real phone
- [ ] Form tested end to end, including the welcome email
- [ ] Social previews checked with each platform's card validator
- [ ] Favicon, page title, and meta description set
- [ ] Custom domain with HTTPS

**For analytics**, I chose a lightweight, privacy-friendly tool (Plausible, Fathom, Umami, or Cloudflare Web Analytics are all solid). I mostly care about three numbers: visitors, where they came from, and how many signed up. A cookie banner on a single-page book site felt like unnecessary friction, and these tools generally let you avoid one.

**After launch**, I looked at where people came from and where they dropped off, then made small changes one at a time: a sharper headline, moving a testimonial higher, shortening the "about me" section. Small, isolated tweaks make it much easier to tell what actually helped.

---

## Wrapping up

Here's the whole process in one glance:

1. **Pick one goal** for the page
2. **Write the copy first**
3. **Structure the page** around your reader's questions
4. **Choose a boring, fast stack**
5. **Build mobile-first** and optimize the cover
6. **Wire up conversions:** email, purchase links, social previews
7. **Measure, launch, iterate**

The biggest lesson for me was that the code was the easy part. The hard part was getting clear on who the book was for and what I wanted them to do. Once that was settled, the page practically built itself.

If you're working on a book, a course, or any side project that needs a home on the web, I hope this saves you a few detours. And if you've built your own launch page, I'd love to see it. Drop a link in the comments!
