# Multi-fetch Fragments

Multi-fetch Fragments makes rendering and caching a collection of template partials easier and faster. It takes advantage of the `read_multi` method on the Rails cache store, so instead of asking the cache for each item's fragment one at a time, the whole collection is requested in a single round trip.

> **Note:** This feature was merged into Rails itself as of Rails 5 (`render partial: ..., collection: ..., cached: true`). If you are on Rails 5 or later, you do not need this gem. It remains useful for Rails 3 and Rails 4 applications.

## The problem

A very common pattern in Rails views is rendering a collection of partials and caching each one:

```erb
<%= render partial: 'item', collection: @items %>
```

```erb
<%# _item.html.erb %>
<% cache item do %>
  <li><%= item.name %> — <%= item.description %></li>
<% end %>
```

This works, but every item in the collection triggers its own cache read. Render 50 items and you make 50 sequential requests to your cache store. With Memcached or Redis running on another host, each of those requests pays for a network round trip, and the cost adds up quickly, even when every fragment is already cached.

## The solution

Multi-fetch Fragments adds a `cache` option to collection rendering:

```erb
<%= render partial: 'item', collection: @items, cache: true %>
```

With that one option, the gem will:

1. Compute the cache key for every item in the collection.
2. Fetch all of the fragments with a single `read_multi` call.
3. Render only the partials that were missing from the cache.
4. Write each newly rendered fragment back to the cache.
5. Return the complete collection, in its original order.

Because the caching now happens at the collection level, you should remove the `cache` block from inside the partial:

```erb
<%# _item.html.erb %>
<li><%= item.name %> — <%= item.description %></li>
```

Your templates get simpler and your pages get faster.

## Installation

Add the gem to your application's Gemfile:

```ruby
gem 'multi_fetch_fragments'
```

Then run:

```
bundle install
```

That's all the setup required. The gem hooks into Action View's partial renderer automatically; there is nothing to configure and no initializer to write.

## Usage

### Basic usage

Add `cache: true` to any collection render:

```erb
<%= render partial: 'item', collection: @items, cache: true %>
```

Each item's cache key is derived from the item itself, exactly as it would be with the standard `cache` helper. For Active Record objects, that means the key includes the record's `updated_at` timestamp, so a fragment expires naturally when its record changes.

On Rails 4, the partial's template digest is included in the key as well. Editing the partial invalidates the old fragments without any manual version bumping.

### Custom cache keys

Sometimes the item alone is not enough to identify a fragment. You might render the same record differently for different locales, user roles, or page contexts. Pass a `Proc` (or lambda) as the `cache` option to build your own key:

```erb
<%= render partial: 'item', collection: @items,
           cache: Proc.new { |item| [item, 'show'] } %>
```

The proc is called once per item and can return anything Rails knows how to expand into a cache key: a string, an object that responds to `cache_key`, or an array combining several of these.

```erb
<%= render partial: 'item', collection: @items,
           cache: ->(item) { [I18n.locale, current_user.role, item] } %>
```

### Expiration

Key-based expiration is usually all you need, but if you want fragments to expire after a fixed period, pass `expires_in`:

```erb
<%= render partial: 'item', collection: @items,
           cache: true, expires_in: 60.minutes %>
```

The option is handed to the cache store when new fragments are written, so it behaves the same way it does with `Rails.cache.write`.

### Other render options

The `cache` option works alongside the usual collection options, such as `as:` and `locals:`:

```erb
<%= render partial: 'products/card', collection: @products,
           as: :product, cache: true %>
```

Bear in mind that anything a partial depends on should be reflected in its cache key. If a local variable changes the rendered output, use a custom key proc that includes it.

## Cache store support

The speedup depends on your cache store implementing `read_multi` efficiently.

| Store | Notes |
| --- | --- |
| Memcached | Use the [Dalli](https://github.com/petergoldstein/dalli) gem, which performs a true multi-get. |
| Redis | Supported through `redis-store` / `redis-activesupport`, which implement `read_multi`. |
| Memory / File store | Works correctly, but falls back to reading keys one by one, so there is little to gain. |

For Memcached with Dalli, a typical configuration looks like this:

```ruby
# config/environments/production.rb
config.cache_store = :dalli_store, 'cache.example.com'
```

If your store does not support `read_multi` natively, the gem still behaves correctly. You simply won't see the performance benefit.

## How much faster is it?

The answer depends on three things: how many items you render, how far away your cache server is, and how warm the cache is.

- **Warm cache, remote store:** this is where the gem shines. One network round trip replaces dozens or hundreds, and the savings grow with the size of the collection.
- **Cold cache:** every partial still has to be rendered, so the gain is small. You do save the individual cache misses.
- **Local, in-process store:** round trips are effectively free already, so expect little difference.

As a rule of thumb, the larger the collection and the higher the latency to your cache, the more you benefit. The best way to know is to measure your own pages before and after. Tools such as `rack-mini-profiler` or your application performance monitor will show the difference in cache time clearly.

## When not to use it

- **Single partials.** The option only applies to collection rendering. For a one-off fragment, keep using the regular `cache` helper.
- **Partials with uncacheable content.** If the partial outputs per-request data, such as CSRF tokens or user-specific content, either move that content out of the partial or include what it depends on in a custom cache key.
- **Rails 5 and later.** Use the built-in `cached: true` option instead.

## Migrating to Rails 5

When you upgrade, moving off this gem is a small mechanical change:

1. Remove `multi_fetch_fragments` from your Gemfile.
2. Replace `cache: true` with `cached: true` in your collection renders.
3. Replace custom key procs with the `cached: ->(item) { ... }` form.

## Contributing

Bug reports and pull requests are welcome.

1. Fork the repository.
2. Create a feature branch (`git checkout -b my-new-feature`).
3. Add tests for your change and make sure the suite passes (`bundle exec rake`).
4. Commit your changes and push the branch.
5. Open a pull request describing what you changed and why.

Please keep changes focused. One fix or feature per pull request makes review much easier.

## License

Multi-fetch Fragments is released under the [MIT License](http://www.opensource.org/licenses/MIT).
