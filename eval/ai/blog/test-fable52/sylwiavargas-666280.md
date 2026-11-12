Justin Gordon's RailsConf 2021 talk starts from a feeling most of us had when we first opened a Rails app: models, routes, and config files look like they're written in a language of their own. His argument is that none of it is magic. It's plain Ruby with the explicit parts left out, and once you put them back, the code becomes readable. Here are my notes.

## The core idea

Ruby lets you omit a lot: the receiver, the parentheses, the braces around a hash, the `return`. That makes for beautiful DSLs, but it also hides what is actually happening. If you come from JavaScript, where almost everything is spelled out, this is disorienting.

The fix is a mental exercise: take a line of "magic" and rewrite it explicitly.

## Example: a model

```ruby
class Post < ApplicationRecord
  has_many :comments, dependent: :destroy
end
```

This looks like a declaration. It's really a method call. Add back what Ruby let us skip:

```ruby
class Post < ApplicationRecord
  self.has_many(:comments, { dependent: :destroy })
end
```

Three things were implicit:

1. **The receiver.** A method call without a receiver goes to `self`.
2. **The parentheses.** They're optional on method calls.
3. **The hash braces.** Trailing key-value pairs are collected into a single argument.

There's also a fourth insight: a class body is executable code. Inside it, `self` is the class itself, so `has_many` is a class method running at load time, which defines more methods for you.

## Always ask: what is `self`?

This was my biggest takeaway. Nearly every "how does this work?" question in Ruby reduces to two questions:

- What is `self` on this line?
- Where is this method defined?

Inside a class body, `self` is the class. Inside an instance method, it's the instance. Inside a block, it's *usually* whatever it was outside the block, unless the method receiving the block changes it.

## Example: routes

```ruby
Rails.application.routes.draw do
  resources :posts
end
```

Who receives `resources`? It's not defined in your file, and `self` at the top of the file doesn't have it. The trick is that `draw` evaluates the block in the context of another object using `instance_eval`, which swaps `self` for the duration of the block. That's the mechanism behind most Ruby DSLs: a block plus a changed `self` gives you what looks like new keywords.

## When the method doesn't exist at all

Sometimes you search the codebase for a method and find nothing. Two usual suspects:

- **`method_missing`**: the object intercepts calls to undefined methods and decides what to do with them.
- **`define_method`**: methods generated at runtime, so there's no `def` to grep for.

Both are regular language features. They just mean you can't always find the answer with text search.

## Ask the running program

Instead of guessing, use a REPL (the talk leans on Pry) to interrogate live objects:

```ruby
self                                   # where am I?
Post.method(:has_many).owner           # who defines this?
Post.method(:has_many).source_location # which file and line?
Post.ancestors                         # the lookup chain
```

In Pry, `ls` lists what's available on an object, `cd` moves into it, and `show-source` prints a method's definition. Dropping a `binding.pry` into a routes file or a model body and typing `self` is the fastest way to turn a hunch into a fact.

## My takeaways

- "Magic" usually means "implicit". Rewrite the line with explicit receivers, parentheses, and braces.
- Class bodies run. Macros like `has_many`, `validates`, and `before_action` are method calls on the class.
- Blocks plus `instance_eval` explain most DSLs.
- If grep fails, suspect metaprogramming and ask the object directly.
- This skill pays off most when reading other people's code, gems and Rails itself included.

The talk is worth watching if you're new to Ruby or mentoring someone who is. The recording is on the RailsConf 2021 YouTube playlist.
