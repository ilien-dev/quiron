# How To Add A Table Of Contents To Jekyll Blog Posts

Long-form blog posts are easier to navigate when readers can see their structure at a glance. A table of contents gives visitors quick links to each section and helps them jump directly to the information they need.

In this guide, we’ll add an automatically generated table of contents to Jekyll posts using the `jekyll-toc` plugin.

## 1. Install the plugin

Add `jekyll-toc` to the `:jekyll_plugins` group in your `Gemfile`:

```ruby
group :jekyll_plugins do
  gem "jekyll-toc"
end
```

Then install the dependency:

```bash
bundle install
```

Next, register the plugin in `_config.yml`:

```yaml
plugins:
  - jekyll-toc
```

Restart the Jekyll development server after changing `_config.yml`:

```bash
bundle exec jekyll serve
```

Jekyll does not automatically reload configuration changes, so restarting the server is important.

## 2. Add the table of contents to a layout

The plugin provides a `toc` filter that reads Markdown headings and turns them into a nested list of links.

Open the layout used by your blog posts, usually `_layouts/post.html`, and add:

```liquid
{% if page.toc %}
  <nav class="table-of-contents" aria-label="Table of contents">
    <h2>Table of Contents</h2>
    {{ content | toc_only }}
  </nav>
{% endif %}

{{ content }}
```

The `toc_only` filter outputs only the generated table of contents. The normal `content` variable still renders the complete post below it.

The `if` statement makes the feature optional. To enable it for a post, add `toc: true` to its front matter:

```yaml
---
layout: post
title: "Understanding Jekyll Collections"
toc: true
---
```

This is useful because a short announcement probably does not need a table of contents, while a detailed tutorial does.

## 3. Make headings linkable

Each entry in the table of contents points to an HTML heading ID. Jekyll’s default Markdown processor, Kramdown, normally generates these IDs automatically.

For example:

```markdown
## Installing Jekyll
```

becomes something similar to:

```html
<h2 id="installing-jekyll">Installing Jekyll</h2>
```

You can also assign an explicit ID when you need a stable URL:

```markdown
## Installing Jekyll
{: #installation }
```

The resulting section can then be opened directly with a URL ending in `#installation`.

Try to keep heading text unique. Repeated headings may produce confusing or automatically numbered IDs.

## 4. Style the table of contents

Add a few styles to your site’s stylesheet:

```css
.table-of-contents {
  margin: 2rem 0;
  padding: 1rem 1.25rem;
  border-left: 4px solid #3b82f6;
  background: #f8fafc;
}

.table-of-contents h2 {
  margin-top: 0;
  font-size: 1.25rem;
}

.table-of-contents ul {
  margin-bottom: 0;
  padding-left: 1.25rem;
}

.table-of-contents a {
  text-decoration: none;
}

.table-of-contents a:hover {
  text-decoration: underline;
}
```

You can also enable smooth scrolling:

```css
html {
  scroll-behavior: smooth;
}
```

Remember that smooth scrolling should remain a progressive enhancement. The links must still work when it is unavailable.

## 5. Choose which heading levels to include

A table of contents can become noisy if it includes every small subsection. You can configure the plugin in `_config.yml`:

```yaml
toc:
  min_level: 2
  max_level: 3
```

This example includes `h2` and `h3` headings while excluding the post title and deeply nested sections.

## A note about GitHub Pages

GitHub Pages supports only a limited set of plugins during its standard build process. If your deployment rejects `jekyll-toc`, build the site with GitHub Actions and publish the generated `_site` directory instead. Another option is to write the table of contents manually.

Once configured, every post with `toc: true` gets an accessible, automatically updated navigation block. Add, remove, or rename a heading, and Jekyll keeps the table of contents in sync for you.