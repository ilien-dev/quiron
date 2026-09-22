# How To Add Related Posts In Jekyll To Increase Engagement

Jekyll is a popular static site generator that powers thousands of blogs and documentation sites. One feature that can significantly improve user engagement is the ability to show related posts at the end of each article. This encourages readers to explore more of your content and increases time spent on your site.

In this guide, I'll show you several approaches to implement related posts in Jekyll, from simple tag-based solutions to more sophisticated content-based recommendations.

## Why Related Posts Matter

Related posts serve multiple purposes. From a user experience perspective, they provide context and guide readers toward content that interests them. From an SEO perspective, they create internal links that help search engines understand your site structure and can improve your rankings. They also increase engagement metrics like pages per session and average session duration.

Jekyll's built-in `site.related_posts` feature provides a starting point, but it's limited—it simply shows posts with the most recent publication dates, which isn't always the most relevant selection.

## Approach 1: Tag-Based Related Posts

The simplest approach is to show posts that share tags with the current post. This is intuitive and works well for most blogs.

In your post layout, add this code:

```liquid
{% if page.tags %}
  <div class="related-posts">
    <h3>Related Posts</h3>
    <ul>
      {% assign related = site.posts | where_exp: "post", "post.url != page.url" %}
      {% assign taggedPosts = "" | split: "" %}
      {% for post in related %}
        {% assign intersection = post.tags | join: "|" %}
        {% for tag in page.tags %}
          {% if intersection contains tag %}
            {% assign taggedPosts = taggedPosts | push: post %}
            {% break %}
          {% endif %}
        {% endfor %}
      {% endfor %}
      {% for post in taggedPosts limit: 5 %}
        <li><a href="{{ post.url }}">{{ post.title }}</a></li>
      {% endfor %}
    </ul>
  </div>
{% endif %}
```

This approach finds posts that share at least one tag with the current post, limits results to five, and displays them in a list.

## Approach 2: Category-Based Related Posts

If your blog uses categories, you can show posts from the same category:

```liquid
{% if page.category %}
  <div class="related-posts">
    <h3>More in {{ page.category }}</h3>
    <ul>
      {% for post in site.posts %}
        {% if post.category == page.category and post.url != page.url %}
          <li><a href="{{ post.url }}">{{ post.title }}</a></li>
          {% if forloop.index == 5 %}{% break %}{% endif %}
        {% endif %}
      {% endfor %}
    </ul>
  </div>
{% endif %}
```

## Approach 3: Combining Tags and Categories

For more sophisticated results, combine both tags and categories:

```liquid
<div class="related-posts">
  <h3>You Might Also Like</h3>
  <ul>
    {% assign relatedByCategory = "" | split: "" %}
    {% assign relatedByTag = "" | split: "" %}
    
    {% for post in site.posts %}
      {% unless post.url == page.url %}
        {% if post.category == page.category %}
          {% assign relatedByCategory = relatedByCategory | push: post %}
        {% endif %}
        {% for tag in page.tags %}
          {% if post.tags contains tag %}
            {% assign relatedByTag = relatedByTag | push: post %}
            {% break %}
          {% endif %}
        {% endfor %}
      {% endunless %}
    {% endfor %}
    
    {% assign combined = relatedByCategory | concat: relatedByTag %}
    {% assign unique = combined | uniq %}
    {% for post in unique limit: 5 %}
      <li><a href="{{ post.url }}">{{ post.title }}</a></li>
    {% endfor %}
  </ul>
</div>
```

## Approach 4: Ruby Plugin for Advanced Matching

For more control, create a Jekyll plugin. Create a file called `_plugins/related_posts.rb`:

```ruby
module Jekyll
  class RelatedPostsGenerator < Generator
    def generate(site)
      site.posts.docs.each do |post|
        post.data['related_posts'] = find_related(post, site)
      end
    end

    private

    def find_related(post, site)
      related = []
      post_tags = post.data['tags'] || []
      post_category = post.data['category']

      site.posts.docs.each do |other_post|
        next if other_post == post

        score = 0
        other_tags = other_post.data['tags'] || []
        other_category = other_post.data['category']

        # Category match: 3 points
        score += 3 if other_category == post_category

        # Tag matches: 1 point each
        common_tags = post_tags & other_tags
        score += common_tags.length

        related << { post: other_post, score: score } if score > 0
      end

      related.sort_by { |item| -item[:score] }
        .take(5)
        .map { |item| item[:post] }
    end
  end
end
```

Then in your layout:

```liquid
{% if page.related_posts %}
  <div class="related-posts">
    <h3>Related Posts</h3>
    <ul>
      {% for post in page.related_posts %}
        <li><a href="{{ post.url }}">{{ post.title }}</a></li>
      {% endfor %}
    </ul>
  </div>
{% endif %}
```

## Styling Your Related Posts

Add some CSS to make your related posts section visually appealing:

```css
.related-posts {
  margin-top: 3rem;
  padding: 2rem;
  background-color: #f5f5f5;
  border-left: 4px solid #0066cc;
}

.related-posts h3 {
  margin-top: 0;
}

.related-posts ul {
  list-style: none;
  padding: 0;
}

.related-posts li {
  margin-bottom: 0.5rem;
}

.related-posts a {
  color: #0066cc;
  text-decoration: none;
}

.related-posts a:hover {
  text-decoration: underline;
}
```

## Optimization Tips

If you have a large number of posts, computing related posts during build time can slow your Jekyll build. Consider caching the results or using a simpler algorithm for large sites.

You can also add a `related_posts_limit` variable to your frontmatter to control how many related posts appear on specific posts.

## Monitoring Impact

After implementing related posts, monitor your analytics. Look at metrics like:
- Pages per session: Do users visit more pages?
- Session duration: Do sessions last longer?
- Bounce rate: Are more users staying on your site?

## Conclusion

Related posts are a simple but effective way to increase engagement on your Jekyll blog. Whether you choose tag-based matching, category-based matching, or a custom algorithm, the implementation is straightforward. Start with the simplest approach that works for your site, and refine from there based on user engagement and your specific needs. Your readers will appreciate having easy access to content that interests them, and you'll benefit from improved metrics.