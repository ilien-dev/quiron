# Talk Notes: "Implicit to Explicit: Decoding Ruby's Magical Syntax" (RailsConf 2021)

Ruby is famous for being expressive and pleasant to write, and it's just as famous for doing a lot of things behind the scenes that feel like magic when you're new. At RailsConf 2021 I gave a talk about exactly that, called **"Implicit to Explicit: Decoding Ruby's Magical Syntax"**. These are my notes from it, for anyone who wants a written version or a quick refresher.

## Why this talk?

When I was learning Ruby I kept running into code that worked but that I couldn't explain. The parentheses were missing, the `return` was missing, and I had no idea what `&:` was doing. Rails adds even more layers on top.

So the idea was simple. Take common bits of "magical" Ruby syntax and rewrite them in their most explicit form. Once you see what's happening underneath, the magic turns into syntax you understand and can use on purpose.

## 1. Optional parentheses

In Ruby, parentheses around method arguments are usually optional.

```ruby
puts "Hello"
puts("Hello")
```

These are the same thing. It is also why so much Rails code reads like plain English:

```ruby
validates :email, presence: true
validates(:email, { presence: true })
```

That second line shows two pieces of hidden syntax: the parentheses and the curly braces around the final hash argument.

## 2. Implicit return

Every Ruby method returns the value of its last evaluated expression.

```ruby
def full_name
  "#{first_name} #{last_name}"
end

def full_name
  return "#{first_name} #{last_name}"
end
```

An explicit `return` is still useful for returning early, but it's rarely needed at the end of a method.

## 3. Implicit `self`

Inside an instance method, calling another method without a receiver means calling it on `self`.

```ruby
def greeting
  "Hi, #{name}"        # implicit
  "Hi, #{self.name}"   # explicit
end
```

The one catch: when *assigning*, you need `self.` or Ruby will create a local variable instead.

```ruby
self.name = "Ada"  # calls the name= method
name = "Ada"       # creates a local variable
```

## 4. Symbol to proc (`&:`)

This one confuses almost everyone at first.

```ruby
names.map(&:upcase)
names.map { |name| name.upcase }
```

The `&` calls `to_proc` on the symbol `:upcase` to turn it into a proc, and that proc calls the method with the same name on each element.

## 5. Operators are methods

In Ruby, most operators are methods with special syntax.

```ruby
1 + 2
1.+(2)

array[0]
array.[](0)
```

This is why you can define `+`, `==`, or `[]` on your own classes.

## 6. Blocks and `yield`

A method can take a block without declaring it, and the block is called with `yield`.

```ruby
def twice
  yield
  yield
end

def twice(&block)
  block.call
  block.call
end
```

Making the block explicit with `&block` is useful for passing it along to another method.

## If code confuses you

Ruby's "magic" is almost always syntactic sugar for something explicit, so when a line confuses you, try rewriting it in its most explicit form. The implicit version is great for readability once you know what it's hiding. `irb`, `method(:name).source_location` and the docs go a long way toward demystifying the rest.

Thank you to everyone who attended and asked questions! If you have favorite bits of Ruby magic that tripped you up, I'd love to hear about them in the comments.
