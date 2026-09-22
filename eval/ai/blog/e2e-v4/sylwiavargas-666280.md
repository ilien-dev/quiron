# Talk Notes: "Implicit to Explicit: Decoding Ruby's Magical Syntax" (RailsConf 2021)

✨ **What is this post about**: At RailsConf 2021 I gave a talk called **"Implicit to Explicit: Decoding Ruby's Magical Syntax"**. These are my notes from it, for anyone who wants a written version or a quick refresher.

✨ **One-paragraph summary**: Ruby is famous for being expressive and pleasant to write. It's also famous for doing a lot of things behind the scenes, which can feel like magic, especially when you're new. The talk takes common pieces of "magical" Ruby syntax and rewrites them in their most explicit form, because once you see what's actually happening, the magic turns into something you understand and can use on purpose.

---

## Why this talk?

When I was learning Ruby, I kept running into code that worked but that I couldn't really explain. Where did the parentheses and the `return` go? What is `&:` doing? And Rails adds even more layers on top of that.

---

## The magic, made explicit

**1. Optional parentheses.** In Ruby, parentheses around method arguments are usually optional, so these two are the same thing:

```ruby
puts "Hello"
puts("Hello")
```

This is also why so much Rails code reads like plain English:

```ruby
validates :email, presence: true
validates(:email, { presence: true })
```

That second line shows two pieces of hidden syntax: the parentheses, and the curly braces around the final hash argument.

**2. Implicit return.** Every Ruby method returns the value of its last evaluated expression.

```ruby
def full_name
  "#{first_name} #{last_name}"
end

def full_name
  return "#{first_name} #{last_name}"
end
```

An explicit `return` is still useful for returning early, but you rarely need it at the end of a method.

**3. Implicit `self`.** Inside an instance method, calling another method without a receiver means calling it on `self`.

```ruby
def greeting
  "Hi, #{name}"        # implicit
  "Hi, #{self.name}"   # explicit
end
```

There is one catch: when you're *assigning*, you need `self.` or Ruby will create a local variable instead.

```ruby
self.name = "Ada"  # calls the name= method
name = "Ada"       # creates a local variable
```

**4. Symbol to proc (`&:`).** This one confuses almost everyone at first.

```ruby
names.map(&:upcase)
names.map { |name| name.upcase }
```

The symbol `:upcase` is converted into a proc by `&`, which calls `to_proc` on it, and that proc calls the method with the same name on each element.

**5. Operators are methods.** Most operators in Ruby are just methods with special syntax:

```ruby
1 + 2
1.+(2)

array[0]
array.[](0)
```

That's why you can define `+`, `==` or `[]` on your own classes.

**6. Blocks and `yield`.** A method can take a block without declaring it, and `yield` calls it.

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

Making the block explicit with `&block` is useful when you need to pass it along to another method.

---

So Ruby's "magic" is almost always syntactic sugar for something explicit, and the implicit version is great for readability once you know what it's hiding. When code confuses you, try rewriting it in its most explicit form. `irb`, `method(:name).source_location` and the docs go a long way here too.

Thank you to everyone who attended and asked questions! If you have favorite bits of Ruby magic that tripped you up, I'd love to hear about them in the comments.
