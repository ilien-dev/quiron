When you first open a Rails app, a lot of the code doesn't look like code. Lines like `has_many :comments` or `before_action :authenticate_user!` read like configuration or English. They work, but it's not obvious *why*.

That's the subject of Justin Daniel's RailsConf 2021 talk, **"Implicit to Explicit: Decoding Ruby's Magical Syntax."** The idea is simple: Rails isn't magic, it's Ruby with optional syntax left out. If you add that syntax back, the magic disappears and you're left with ordinary method calls.

Here are my notes.

## The core idea: everything is a method call

Ruby lets you leave out several things:

- **Parentheses** around method arguments
- **The receiver** (`self.`) when calling a method on the current object
- **Curly braces** around a hash passed as the last argument
- **The `return` keyword** at the end of a method

Each one is a small convenience. Combined, they make method calls look like language keywords.

## Decoding a model

Take a typical model:

```ruby
class Post < ApplicationRecord
  has_many :comments, dependent: :destroy
  validates :title, presence: true
end
```

Here is the same code with the implicit parts written out:

```ruby
class Post < ApplicationRecord
  self.has_many(:comments, { dependent: :destroy })
  self.validates(:title, { presence: true })
end
```

Inside a class body, `self` is the class itself, `Post`. So `has_many` is just a **class method** that `Post` inherits from `ActiveRecord::Base`. It runs once when the class loads, and it defines methods like `post.comments` for you.

*(A Ruby 3 caveat: keyword arguments and a trailing hash are no longer fully interchangeable, so the braces version is only conceptually equivalent. The point is about seeing the structure.)*

## Decoding a controller

```ruby
class PostsController < ApplicationController
  before_action :set_post, only: [:show, :edit]

  def show
    render json: @post
  end
end
```

Made explicit:

```ruby
class PostsController < ApplicationController
  self.before_action(:set_post, { only: [:show, :edit] })

  def show
    self.render({ json: @post })
  end
end
```

`before_action` is another class method that registers a callback. `render` is an instance method on the controller, called with a single options hash. It looks like a DSL, but it's an ordinary method call.

## Operators are methods too

The talk also covers a part of Ruby that surprises many newcomers: operators are just methods with special syntax.

```ruby
1 + 2            # => 1.+(2)
array[0]         # => array.[](0)
user.name = "Al" # => user.name=("Al")
```

So when you define `def name=(value)` in a class, you're making assignment syntax work for your own objects. Nothing is special-cased for built-in types.

## Blocks and `&:symbol`

Blocks get the same treatment. This one-liner:

```ruby
names.map(&:upcase)
```

expands to:

```ruby
names.map { |name| name.upcase }
```

The `&` calls `to_proc` on the symbol `:upcase`, which returns a proc that calls `upcase` on whatever is passed to it. Again, this is a protocol built from regular methods, not a parser trick.

Routes work the same way. In `Rails.application.routes.draw do ... end`, the block is evaluated against a routing mapper object. That's why `resources :posts` can appear with no visible receiver: inside that block, `self` is the mapper.

## Why this matters

My main takeaway is that **being able to translate implicit Ruby into explicit Ruby is a debugging skill**. When a Rails line confuses you, ask:

1. What is `self` right now?
2. What method is being called?
3. What arguments, including hidden hashes and blocks, is it receiving?

Once you can answer those, you can look up the method in the Rails API docs, read its source, or call it yourself in the console. The framework becomes code you can read instead of incantations you memorize.

## Final thoughts

This is a great talk for anyone in their first year of Rails, and a useful refresher for experienced developers who mentor others. It doesn't introduce new APIs. It changes how you *read* Ruby code you already see every day.

If you have 30 minutes, it's worth watching. Next time you see `has_many`, try mentally adding `self.` and the parentheses.
