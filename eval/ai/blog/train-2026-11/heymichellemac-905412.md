# How To Add A Table Of Contents To Jekyll Blog Posts

Long tutorials are easier to navigate when readers can jump straight to the section they need. A table of contents also gives visitors a quick preview of what your post covers before they start reading.

If your Jekyll blog uses Kramdown, you can generate one directly from your Markdown headings. There’s no extra plugin to install and no JavaScript to maintain.

Let’s add one, customize its appearance, and check that it works.

## 1. Check your Markdown renderer

Jekyll uses Kramdown as its default Markdown renderer. If you haven’t changed that setting, you can probably skip straight to the next step. See [Jekyll’s Markdown documentation](https://jekyllrb.com/docs/configuration/markdown/) for the supported configuration options.

To make the renderer explicit, add this to `_config.yml`:

```yaml
markdown: kramdown
```

If that setting already exists, edit the existing entry instead of adding another one.

This tutorial relies on Kramdown’s syntax, so a site configured with a different renderer may need a different approach.

## 2. Add the table of contents placeholder

Open a Markdown post inside your `_posts` directory. Below its front matter and introduction, insert:

```markdown
* TOC
{:toc}
```

The first line creates a placeholder list. The second tells Kramdown to replace that list with a table of contents generated from the document’s headings.

The placeholder text itself isn’t special: `TOC` simply makes its purpose clear when editing the file. The `{:toc}` marker does the work. Kramdown documents this behavior in its [HTML converter reference](https://kramdown.gettalong.org/converter/html.html).

Here’s a complete example:

```markdown
---
layout: post
title: "Getting Started With Jekyll"
---

This guide walks through creating and publishing a Jekyll blog.

**On this page**

* TOC
{:toc}

## Install Jekyll

Add your installation instructions here.

## Create Your Site

Explain how to generate a new site.

### Choose a Theme

Describe your theme options.

## Publish Your Blog

Add your deployment instructions here.
```

Keep the marker directly beneath the list item, as shown.

When Jekyll builds the page, the placeholder becomes a linked list. The subsection appears beneath its parent section, reflecting the structure of your headings.

## 3. Choose which heading levels appear

A long post can have plenty of small subsections. Including every heading may make the contents list harder to scan.

To include only second-level and third-level headings, update `_config.yml`:

```yaml
markdown: kramdown

kramdown:
  toc_levels: "2..3"
```

If you already have a `kramdown:` section, add `toc_levels` beneath it. Preserve the other settings and use spaces for YAML indentation.

The [`toc_levels` option](https://kramdown.gettalong.org/options.html) controls which heading levels enter the generated list.

For most tutorials, `##` headings work well for major steps and `###` headings for supporting topics. Write descriptive headings so readers can understand the outline without opening each section.

## 4. Give it some styling

Add a custom class to the placeholder:

```markdown
* TOC
{:toc .post-toc}
```

Then place the following CSS in a stylesheet your theme already loads:

```css
.post-toc {
  padding: 1rem 1rem 1rem 2.5rem;
  margin: 1.5rem 0;
  border-left: 4px solid #6366f1;
  background: #f5f5f5;
  color: #222;
  line-height: 1.8;
}

.post-toc a {
  color: #4338ca;
  text-decoration: underline;
}
```

Adjust the colors to suit your theme, especially if your site supports dark mode. Check that links remain readable and keyboard focus remains visible.

Keep the styling modest: the list should help readers reach the article.

## 5. Preview and troubleshoot

Start your local development server:

```bash
bundle exec jekyll serve
```

Open the post and click each contents link. Confirm that it reaches the expected heading and that nested entries look sensible on mobile.

Restart the server after changing `_config.yml` so your configuration is reloaded.

If the literal `{:toc}` text appears, check your Markdown renderer and the marker’s placement. If entries are missing, check `toc_levels` and confirm that your sections use Markdown headings.

Also check whether your theme already provides a contents feature before adding a second one.

Once everything looks right, keep the placeholder in your post template. Future articles can then get a navigable outline as you write their headings.
