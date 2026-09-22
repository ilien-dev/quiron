# Talk Notes: "Implicit to Explicit: Decoding Ruby's Magical Syntax" (RailsConf 2021)

Ruby is famous for being expressive and pleasant to write. It's also famous for doing a lot of things behind the scenes, which can feel like magic, especially when you're new. At RailsConf 2021 I gave a talk about exactly that, called "Implicit to Explicit: Decoding Ruby's Magical Syntax". These are my notes from it, for anyone who wants a written version or a quick refresher.

## Why this talk?

When I was learning Ruby, I kept running into code that worked but that I couldn't really explain. Where are the parentheses? Where's the `return`? What is `&:` doing? And Rails adds even more layers on top.

So the idea was simple: take the common pieces of "magical" Ruby syntax and rewrite each one in its most explicit form. Once you see what's actually happening, the magic turns into something you understand and can use on purpose.

## 1. Optional parentheses

In Ruby, parentheses around method arguments are usually optional.

```ruby
puts "Hello"
puts("Hello")
```

These are the same thing, and that's also why so much Rails code reads like plain English:

```ruby
validates :email, presence: true
validates(:email, { presence: true })
```

The second line shows two pieces of syntax that are normally hidden: the parentheses, and the curly braces around the final hash argument.

## 2. Implicit return

Every Ruby method returns the value of the last expression it evaluated.

```ruby
def full_name
  "#{first_name} #{last_name}"
end

def full_name
  return "#{first_name} #{last_name}"
end
```

An explicit `return` is still useful for returning early, but you rarely need one at the end of a method.

## 3. Implicit `self`

Inside an instance method, a method called without a receiver is called on `self`.

```ruby
def greeting
  "Hi, #{name}"        # implicit
  "Hi, #{self.name}"   # explicit
end
```

There's one catch: when you're *assigning*, you need `self.` or Ruby will create a local variable instead.

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

The `&` converts the symbol `:upcase` into a proc by calling `to_proc` on it. That proc then calls the method with the same name on each element.

## 5. Operators are methods

Most operators in Ruby are just methods with special syntax.

```ruby
1 + 2
1.+(2)

array[0]
array.[](0)
```

That's why you can define `+`, `==` or `[]` on your own classes.

## 6. Blocks and `yield`

A method can take a block without declaring it, and `yield` calls it.

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

Making the block explicit with `&block` is useful when it has to be passed along to another method.

## What I'd take away

Ruby's "magic" is almost always syntactic sugar for something explicit. When code confuses you, try rewriting it in its most explicit form. Implicit syntax is great for readability once you understand what it's hiding. And `irb`, `method(:name).source_location` and reading the docs go a long way toward demystifying things.

Thank you to everyone who attended and asked questions! If you have favorite bits of Ruby magic that tripped you up, I'd love to hear about them in the comments.
