# The 7 Step Process I Used To Build A Landing Page To Promote My Book

When I finished writing my book, I thought the hard part was over. Then I realized nobody could buy it, because there was nowhere to send them.

I'm a developer, so my first instinct was to open an editor and start building. That instinct was wrong, and it cost me a weekend. The page I eventually shipped came out of a much more deliberate process, and it's the one I'd follow again. Here it is, step by step.

## Step 1: Define the one thing the page has to do

My first draft tried to do everything: sell the book, grow my newsletter, link to my other projects, show off my blog. It had four different calls to action above the fold.

A landing page is not a homepage. It has one job. So before writing any code, I wrote one sentence:

> A developer who lands here should understand what the book will do for them and click "Get the book" within 60 seconds.

Every later decision got checked against that sentence. Does a navbar help? No, it gives people exits. Does a link to my blog help? No. Does a sample chapter help? Yes, because it lowers the risk of buying.

If you only take one step from this post, take this one. It makes the other six much easier.

## Step 2: Write the copy before touching the design

This is the step developers most want to skip, and I was no exception. I had the hero section styled before I knew what it would say, which meant I was designing around lorem ipsum and then cramming real words into boxes that didn't fit them.

The second time, I wrote the whole page in a plain Markdown file first. No layout, no colors, only words in order:

1. **Headline:** the outcome the reader gets, not the title of the book.
2. **Subheadline:** who it's for and what makes it different.
3. **The problem:** a description of the pain in the reader's own words.
4. **What's inside:** the chapter list, rewritten as benefits.
5. **Who I am:** two sentences on why I'm worth listening to.
6. **Proof:** quotes from early readers.
7. **The offer:** price, formats, guarantee.
8. **FAQ:** every objection I could think of.

The most useful trick here was rewriting features as outcomes. "Chapter 4: Caching strategies" became "Know which caching layer to reach for, and when to leave it alone." It's the same content, but the reader can see themselves in the second version.

I also read the whole thing out loud. Anything that sounded like a press release got cut.

## Step 3: Sketch the layout in low fidelity

With the copy done, the layout almost designed itself. I drew boxes on paper, one per section, in the order of the Markdown file. It took fifteen minutes.

I settled a few things at this stage:

- **Single column.** A landing page is a linear argument, and sidebars interrupt it.
- **Call to action in three places:** the hero, after the chapter breakdown, and at the bottom. It's the same button with the same text every time.
- **Book cover in the hero.** People want to see the thing they're buying, even when it's a PDF.
- **No navigation menu.** The page gets a logo and a button, and nothing else.

Sketching on paper kept me from fiddling with border radii for an hour. You can't bikeshed a pencil drawing.

## Step 4: Pick the most boring stack that works

I was tempted to use this as an excuse to try a new framework. I talked myself out of it by going back to the sentence from Step 1. Nothing in it says "be technically interesting."

A landing page is a single static document, so I went with:

- **Plain HTML and CSS**, with a small static site generator so I could keep the copy in Markdown.
- **No client-side framework.** The only JavaScript on the page is the checkout embed and analytics.
- **A static host with a CDN**, so I get free hosting, automatic HTTPS, and a deploy on every push.
- **A hosted checkout** for payments and file delivery. I did not want to be handling tax rules and download links myself.

The whole page weighs less than most hero images. It loads instantly on a bad mobile connection, and that matters more than I expected, because most of my traffic comes from people tapping a link on social media on their phone.

If you already know a framework well and can ship faster with it, use it. The stack matters much less than the time it takes you to get the page live.

## Step 5: Build mobile first and keep the styling restrained

I built the page at 375px wide and scaled up from there. With a single-column layout, "responsive" mostly meant setting a max-width and increasing the font size on larger screens.

The style rules I gave myself:

- **One typeface in two weights.** A system font stack costs nothing to load.
- **One accent color**, used only for the buy button. If everything is colorful, nothing stands out.
- **Generous whitespace.** I doubled the section padding I first thought was reasonable, and it finally looked right.
- **Line length capped around 65 characters.** Long lines are tiring to read, and this page is mostly reading.

```css
main {
  max-width: 65ch;
  margin-inline: auto;
  padding-inline: 1.25rem;
  font-size: clamp(1.05rem, 1rem + 0.4vw, 1.25rem);
  line-height: 1.6;
}
```

That snippet did about 80% of the design work.

I also covered the accessibility basics. I used semantic headings in order, wrote alt text for the cover, checked the color contrast, and made sure the button is a real `<a>` or `<button>` with a visible focus state. It took almost no time, and it's part of what makes a page feel trustworthy.

## Step 6: Add proof and remove risk

At this point the page looked finished, but it wasn't persuasive yet. Everything on it was me saying my own book was good.

So before launch, I did three things:

**I collected testimonials.** I sent the draft to a handful of developers I trust and asked a specific question: "What's one thing you'll do differently after reading this?" Specific questions get specific answers, and specific answers make good quotes. "Great book!" convinces no one. A sentence about a real change in someone's work does.

**I offered a free sample chapter.** A visitor who isn't ready to buy can leave an email address and get a chapter. It gives hesitant readers a way to check the quality, and it gives me a way to follow up. It's the one secondary action I allowed on the page, and I placed it well below the main button.

**I added a refund guarantee.** It's a simple one: if the book doesn't help, email me and I'll refund you. It removes the last bit of hesitation at very little cost.

I also wrote the FAQ from real questions my early readers asked: what formats it comes in, whether it suits beginners, and whether updates are free. Each answer removes a reason not to click.

## Step 7: Launch, measure, and iterate

Before sharing the link, I ran through a short checklist:

- Open Graph and Twitter card tags, with a proper preview image. The link will mostly be seen as a card in a feed, so that preview acts as the real first impression.
- A descriptive `<title>` and meta description.
- A test purchase, from start to finish, on my phone.
- Privacy-friendly analytics, with an event on the buy button.
- A Lighthouse run, fixing anything that wasn't green.

Then I launched and watched two numbers: how many visitors clicked the button, and how many of those completed the purchase. A low first number points to the page, and usually to the headline. A low second number points to the price or the checkout.

My first change after launch was the headline. The original was clever, and the replacement was clear. The clear one did better, which is apparently a lesson everyone has to learn for themselves.

Since then, I've changed one thing at a time and given each change enough traffic to mean something.

## What I'd tell myself at the start

Looking back, the process comes down to three ideas:

1. **Decide what the page is for** before deciding what it looks like.
2. **Write the words first.** The design exists to carry them.
3. **Ship the simple version** and let real visitors tell you what to fix.

The build itself was the easy part, and that's a little humbling for a developer. The work that made the difference happened in a Markdown file and on a sheet of paper.

If you're working on a landing page for your own book, course, or side project, I'd love to see it. Drop a link in the comments, and tell me which step gave you the most trouble.

---

The post runs about 1,400 words. I kept the book's title, the specific tools, and the results unnamed because I don't know your real ones. Dropping in your actual title, stack, and a conversion figure or two in Steps 4 and 7 will make it more credible.
