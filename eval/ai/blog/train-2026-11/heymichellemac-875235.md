# How To Add Related Posts In Jekyll To Increase Engagement

Readers who finish one post often leave because they don't know what to read next. A "Related Posts" section fixes that. It keeps people on your site, lowers your bounce rate, and surfaces older articles that would otherwise go unread. Jekyll, the static site generator behind GitHub Pages and many developer blogs, makes this easy once you know which tools to use.

This guide covers two approaches. The first uses Jekyll's built-in `site.related_posts`, which requires no plugins. The second is a small custom generator that scores posts by shared tags and categories, so you control how relatedness is calculated.

## Prerequisites

You'll need:

- A working Jekyll site (Jekyll 4.x is current as of this writing)
- Posts with `tags` or `categories` in their front matter
- Basic familiarity with Liquid templating

Your posts should have front matter that looks something like this:

```yaml
---
title: "Deploying Jekyll to GitHub Pages"
date: 2026-03-14
categories: [devops]
tags: [jekyll, github-pages, ci]
---
```

Consistent tags matter more than anything else in this guide. If one post uses `js` and another uses `javascript`, Jekyll treats them as unrelated. Before you start, audit your tags and pick one spelling for each concept.

## Option 1: Use the Built-In `site.related_posts`

Jekyll exposes a `site.related_posts` variable on every page. Inside a post, you can loop over it directly. Here is a minimal example for a post layout at `_layouts/post.html`:

```html
---
layout: default
---
<article class="post">
  <h1>{{ page.title }}</h1>
  <time datetime="{{ page.date | date_to_xmlschema }}">
    {{ page.date | date: "%B %-d, %Y" }}
  </time>

  {{ content }}
</article>

{% if site.related_posts.size > 0 %}
<section class="related-posts">
  <h2>Related Posts</h2>
  <ul>
    {% for post in site.related_posts limit: 3 %}
      <li>
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        <span class="meta">{{ post.date | date: "%b %Y" }}</span>
      </li>
    {% endfor %}
  </ul>
</section>
{% endif %}
```

Note that `site.related_posts` is only populated on post pages, not on your homepage or index pages. The `{% if %}` guard prevents an empty heading from rendering when no matches exist.

### How Jekyll Chooses Related Posts

By default, Jekyll ranks related posts by how many tags and categories they share with the current post, and it caps the list at 10 entries. If you have the `classifier-reader` gem installed and `lsi: true` in `_config.yml`, Jekyll instead uses Latent Semantic Indexing on the post content. That produces more semantic matches but is slower to build and adds a dependency. For most blogs the default is enough.

The built-in approach works well, but it has limitations. You can't weight tags differently, and you can't filter out drafts or posts from a certain category. For that, a custom generator is more useful.

## Option 2: A Custom Related Posts Generator

Jekyll plugins live in a `_plugins/` directory at your site root. Create `_plugins/related_posts.rb` with the following:

```ruby
module RelatedPosts
  class Generator < Jekyll::Generator
    safe true
    priority :low

    LIMIT = 3

    def generate(site)
      posts = site.posts.docs.reject { |p| p.data["draft"] }

      posts.each do |post|
        post.data["related"] = find_related(post, posts)
      end
    end

    private

    def find_related(post, posts)
      my_tags = normalize(post.data["tags"])
      my_cats = normalize(post.data["categories"])

      scored = posts.filter_map do |other|
        next if other.equal?(post)

        shared_tags = (normalize(other.data["tags"]) & my_tags).size
        shared_cats = (normalize(other.data["categories"]) & my_cats).size
        score = (shared_tags * 2) + shared_cats

        [score, other] if score.positive?
      end

      scored
        .sort_by { |score, other| [-score, -other.date.to_i] }
        .first(LIMIT)
        .map { |_score, other| other }
    end

    def normalize(value)
      Array(value).map { |v| v.to_s.strip.downcase }.uniq
    end
  end
end
```

Here is what this code does:

1. **Filters drafts.** Posts marked `draft: true` are excluded from the candidate pool.
2. **Scores by overlap.** Each shared tag is worth two points and each shared category is worth one. Tags are weighted higher because they describe a post's topics more precisely than categories do. Adjust the weights to suit your site.
3. **Breaks ties by recency.** When two posts have equal scores, the newer one wins. This keeps the suggestions fresh.
4. **Stores the result on the post.** Each post gets a `related` array in its `data` hash, which your layout can read as `page.related`.

The `normalize` method lowercases and trims values, so `JavaScript` and `javascript` match. It also handles the case where a post has a single string instead of an array, because `Array()` wraps it.

### Rendering the Custom Results

Update your post layout to use `page.related` instead of `site.related_posts`:

```html
{% if page.related and page.related.size > 0 %}
<section class="related-posts">
  <h2>Keep Reading</h2>
  <ul>
    {% for post in page.related %}
      <li>
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        {% if post.excerpt %}
          <p>{{ post.excerpt | strip_html | truncate: 100 }}</p>
        {% endif %}
      </li>
    {% endfor %}
  </ul>
</section>
{% endif %}
```

Including a short excerpt often increases clicks, because readers can see why the link is relevant before they commit to it.

### Testing Your Generator

Run a local build and check the output:

```bash
bundle exec jekyll build --incremental
```

Then open a post in `_site/` and confirm the related section appears. If it doesn't, check these common problems:

- **Nothing renders.** Your posts probably don't share any tags. Add the same tag to two or three posts to test.
- **The wrong posts appear.** Your tags may be inconsistent. Run a quick grep across `_posts/` to see the variants.
- **The build fails.** Check that `_plugins/related_posts.rb` has no syntax errors. Ruby is strict about `end` keywords.
- **Changes don't appear.** Jekyll caches aggressively. Run `jekyll clean` and rebuild.

If you deploy to GitHub Pages, note that GitHub Pages only runs a whitelist of plugins. Custom Ruby plugins in `_plugins/` are not supported by the default GitHub Pages build. To use this approach on GitHub Pages, build the site locally or in a GitHub Actions workflow and publish the `_site/` output, rather than relying on the built-in Pages pipeline.

## Making Related Posts Actually Increase Engagement

Adding the section is only the first step. A few choices make a measurable difference:

**Place the section after the conclusion, not before.** Readers who reach the end of a post have shown intent. A related-posts block at the top competes with the content they came for.

**Keep the list short.** Three well-chosen links outperform ten loosely related ones. The `LIMIT` constant in the generator makes this easy to change.

**Write descriptive titles.** Related posts display titles as link text, so "Part 2" tells a reader nothing. "Adding Search to a Jekyll Site" does.

**Check your metrics.** Use your analytics tool to track clicks on the related-posts section. Compare pages-per-session and time-on-site before and after the change. If the numbers don't move, try a different placement or heading text.

**Maintain your tags.** The quality of your recommendations depends entirely on the quality of your metadata. Review tags every few months and merge duplicates.

## Choosing an Approach

Use the built-in `site.related_posts` if you want the fastest setup and your site is hosted on a platform that runs default Jekyll. Use the custom generator if you need control over weighting, draft handling, or result count, and you can build the site yourself.

Either way, related posts are one of the cheapest engagement improvements you can make to a Jekyll blog. Once the template is in place, every new post you publish automatically links into your back catalog, which gives older content a second life.

## Summary

- Jekyll's `site.related_posts` gives you related posts with no plugins, based on shared tags and categories.
- A custom generator in `_plugins/related_posts.rb` lets you weight tags, skip drafts, and control the result count.
- Consistent tagging is the foundation of good recommendations.
- Custom plugins don't run on the default GitHub Pages build, so build locally or in CI if you use them.
- Place the section after the post's conclusion, keep it short, and measure the result.

If you try this on your own site, I'd like to hear what weights worked best for your content.
