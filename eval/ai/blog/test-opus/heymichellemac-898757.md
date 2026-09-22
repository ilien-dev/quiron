# The 7 Step Process I Used To Build A Landing Page To Promote My Book

When I finished writing my book, I thought the hard part was over. Then I realized I had no way to actually tell people about it. I needed a landing page: one place where I could explain what the book was, who it was for, and how to get it.

As a developer, I could have spent weeks building something elaborate. Instead, I gave myself a deadline of one weekend and followed a simple process. Here are the seven steps I used, what I learned along the way, and what I'd do differently next time.

## Step 1: Define the Goal of the Page

Before touching any code, I asked myself one question: **what's the single thing I want a visitor to do?**

It's tempting to cram everything onto a landing page. Links to your blog, your social profiles, your other projects, a newsletter signup, a contact form. But every extra link is a distraction from the main action.

For me, the goal was clear: **get people to join the early access list.** The book wasn't out yet, and I wanted to build an audience of people who'd be excited when it launched.

Everything else on the page existed to support that one action. If a section didn't help someone decide to sign up, it didn't make the cut.

## Step 2: Write the Copy First

This was the biggest lesson for me. I used to start with design, then try to squeeze words into the boxes. This time, I wrote all the copy in a plain text document before opening my code editor.

I structured it like this:

1. **Headline:** What is the book, in one sentence?
2. **Subheadline:** Who is it for, and what will they get out of it?
3. **The problem:** What struggle does the reader have right now?
4. **The solution:** How does the book help?
5. **What's inside:** A short list of chapters or key topics.
6. **About the author:** Why should they listen to me?
7. **Call to action:** Join the list.

Writing the headline took longer than anything else. I wrote about 20 versions. My first draft was something like "A Book About Getting Your First Developer Job." Accurate, but boring. The final version focused on the outcome the reader wanted, not the format of the product.

A good tip here: read your copy out loud. If it sounds like a corporate brochure, rewrite it until it sounds like you're explaining it to a friend.

## Step 3: Sketch the Layout

With the copy done, I grabbed a notebook and sketched a rough layout. No Figma, no mockups. Just boxes and arrows on paper.

Because the copy already existed, the layout almost designed itself. Each section of the text became a section of the page, stacked vertically:

- Hero with headline, subheadline, book cover image, and signup form
- Problem/solution section
- "What you'll learn" list
- A short author bio with a photo
- A final call to action repeating the signup form

I put the signup form in two places: at the top for people who are already convinced, and at the bottom for people who needed to read everything first.

I also sketched a mobile version. A huge share of my traffic was going to come from social media, and most of that is on phones. Designing mobile-first kept me from building something that only looked good on my 27-inch monitor.

## Step 4: Choose a Simple Tech Stack

I'll be honest: this is where I almost derailed. I started researching frameworks, headless CMS options, and animation libraries. Then I reminded myself that the page had one job.

I ended up with:

- **Plain HTML and CSS**, with a small amount of JavaScript for the form
- **A static hosting provider** with a free tier and automatic deploys from GitHub
- **An email service** with an embeddable signup form and a free plan for small lists

No build step. No framework. The whole site was one HTML file, one CSS file, and a couple of images.

Would a framework have been more fun? Probably. Would it have made the page better at getting signups? No. When your goal is to ship, boring tech is your friend.

## Step 5: Build It

With the copy, layout, and stack decided, building the page was actually the fastest part. I used CSS Grid and Flexbox for layout, and a handful of CSS custom properties for colors and spacing so everything stayed consistent:

```css
:root {
  --color-primary: #5b3cc4;
  --color-text: #1f1f1f;
  --color-bg: #fffaf5;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 2rem;
  --max-width: 720px;
}
```

A few things I paid special attention to:

**Performance.** I compressed the book cover image and served it in a modern format. The whole page weighed in under 200 KB. Fast pages convert better, especially on mobile connections.

**Accessibility.** I made sure every image had alt text, the form inputs had proper labels, the color contrast passed WCAG AA, and the page could be navigated with just a keyboard. A landing page that some people can't use is a landing page that loses signups.

**The form.** I styled the email provider's form to match the rest of the page, added a clear success message, and made sure errors were announced to screen readers.

```html
<form class="signup" action="..." method="post">
  <label for="email">Email address</label>
  <input id="email" type="email" name="email" required autocomplete="email">
  <button type="submit">Get early access</button>
</form>
```

**Social previews.** I added Open Graph and Twitter card meta tags with a custom preview image. Since most people would find the page through a shared link, the preview was basically my first impression.

## Step 6: Get Feedback Before Launching

Before I shared the page publicly, I sent it to five people: two developers, two people in my target audience, and one friend who's brutally honest.

Their feedback was eye-opening:

- One person didn't understand what the book was about until they scrolled halfway down. I rewrote the subheadline.
- Two people said the button text "Subscribe" felt like a commitment. I changed it to "Get early access," which felt more like a benefit.
- My honest friend said the author bio was too long and "sounded like a LinkedIn profile." Fair. I cut it in half.

None of these were things I would have caught myself. I was too close to the project. If you only take one step from this list, make it this one.

## Step 7: Launch, Share, and Measure

Once the page was live, I shared it on Twitter, LinkedIn, and here on DEV, along with a short thread about why I wrote the book. I also added the link to my email signature and my social bios.

I set up simple, privacy-friendly analytics to track two numbers:

1. **Visitors**
2. **Signups**

Divide the second by the first and you get your conversion rate. That became the number I focused on. When I tweaked the headline a couple of weeks after launch, I could see whether it actually made a difference instead of guessing.

I also kept an eye on where visitors were coming from. It turned out one platform was sending far more engaged visitors than the others, so I shifted more of my energy there.

## What I'd Do Differently

Looking back, a few things stand out:

- **Start building the page earlier.** I waited until the book was almost done. If I'd launched the page on day one of writing, I could have grown the list the whole time.
- **Add social proof sooner.** Once early readers started sending me kind messages, I added a few quotes to the page. I wish I'd collected them from beta readers from the start.
- **Offer something free.** A free sample chapter in exchange for an email address would likely have boosted signups. I added this later and wish I'd done it at launch.

## Wrapping Up

Here's the process one more time:

1. Define the one goal of the page
2. Write the copy first
3. Sketch the layout
4. Choose a simple tech stack
5. Build it with performance and accessibility in mind
6. Get feedback before launching
7. Launch, share, and measure

The biggest takeaway for me was that a landing page is mostly a writing problem, not a coding problem. The code took one afternoon. Figuring out what to say, and saying it clearly, took much longer, and it's what actually made the page work.

If you're working on your own book, course, or side project, I hope this helps you get your landing page out the door. And if you have questions about any of these steps, I'm happy to answer them in the comments!
