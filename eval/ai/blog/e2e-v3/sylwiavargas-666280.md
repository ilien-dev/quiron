# Talk notes: "Implicit to Explicit: Decoding Ruby's Magical Syntax" (RailsConf 2021)

Ruby is famous for being expressive and pleasant to write. It's also famous for doing plenty behind the scenes, which can feel like magic to a beginner. At RailsConf 2021 I gave a talk about exactly that, called **"Implicit to Explicit: Decoding Ruby's Magical Syntax"**. These are my notes from it, for anyone who wants a written version or a quick refresher.

When I was learning Ruby I kept running into code that worked but that I couldn't really explain. Where are the parentheses? Where's the `return`? And I had no idea what `&:` was doing. In Rails even more is layered on top. The idea of the talk was simple: take the common bits of "magical" Ruby syntax and rewrite each one in its most explicit form. Once the mechanism is visible, the magic turns into something you understand and can use on purpose.

## Parentheses and return

Parentheses around method arguments are usually optional in Ruby.

```ruby
puts "Hello"
puts("Hello")
```

Those two lines do the same thing. It's also why so much Rails code reads like plain English:

```ruby
validates :email, presence: true
validates(:email, { presence: true })
```

The second line there shows two pieces of hidden syntax, the parentheses and the curly braces around the final hash argument.

The `return` is hidden too. Every Ruby method returns the value of the last expression it evaluated.

```ruby
def full_name
  "#{first_name} #{last_name}"
end

def full_name
  return "#{first_name} #{last_name}"
end
```

An explicit `return` is still useful for returning early, but at the end of a method it's rarely needed.

## Implicit `self`

Inside an instance method, a call to another method without a receiver is a call on `self`.

```ruby
def greeting
  "Hi, #{name}"        # implicit
  "Hi, #{self.name}"   # explicit
end
```

There's one catch: in an *assignment*, `self.` is required, or Ruby creates a local variable instead.

```ruby
self.name = "Ada"  # calls the name= method
name = "Ada"       # creates a local variable
```

## `&:` and operators

Symbol to proc confuses almost everyone at first.

```ruby
names.map(&:upcase)
names.map { |name| name.upcase }
```

The `&` turns the symbol `:upcase` into a proc by calling `to_proc` on it. That proc then calls the method of the same name on each element.

Operators are less magic than they look, because most of them are just methods with special syntax:

```ruby
1 + 2
1.+(2)

array[0]
array.[](0)
```

That's why you can define `+`, `==` or `[]` on your own classes.

## Blocks and `yield`

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

Almost all of Ruby's "magic" is syntactic sugar for something explicit, and implicit syntax is great for readability once you know what it's hiding. When some code confuses you, try writing it out in its most explicit form. `irb`, `method(:name).source_location` and the docs will get you a long way.

Thank you to everyone who came to the talk and asked questions! If some bit of Ruby magic tripped you up, I'd love to hear about it in the comments.
