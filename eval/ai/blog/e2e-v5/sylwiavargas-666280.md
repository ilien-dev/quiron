✨ **What is this post about**: As a part of my professional growth, I make time to watch conference talks on Ruby, Rails, JS, React, and tech writing. Previously, I'd just watch them but now I will take and publish notes for future reference. This talk was a part of RailsConf 2021 that I'm attending at the time of writing.

✨ **Talk:** 'Implicit to Explicit: Decoding Ruby's Magical Syntax' by [Justin Gordon](https://twitter.com/railsonmaui)

✨ **Short summary**: Rails leans heavily on Ruby's implicitness: `self`, variable declarations, parentheses. The goal of the talk is to learn to read code the way the interpreter reads it, so that you understand what you're writing instead of copy-pasting it.

✨ **Impression**: The talk ended up being mostly about pry, and I was blown away by Justin's `~/.pryrc`. I loved how calm and kind his explanations were. I need to re-watch the pry demo and code along with it.

---

## Table of contents:
- [Explicit JS vs implicit Ruby](#explicit-js-vs-implicit-ruby)
- [Pry](#pry)
- [Read more](#read-more)

---

## Explicit JS vs implicit Ruby

Next to JavaScript, a lot of Ruby looks like magic, because JS makes you spell things out:
- parentheses are required to call a function
- `this` is rarely implicit
- you `return` explicitly

Ruby lets you leave all of that out:

- **parentheses are optional**, so `user.first` could be a method call or an attribute and you can't tell from reading it. This is also why so much Rails code reads like plain English:

```ruby
validates :email, presence: true
validates(:email, { presence: true })
```

- **returns are implicit**: a method returns the value of its last expression, so these two are the same:

```ruby
def full_name
  "#{first_name} #{last_name}"
end

def full_name
  return "#{first_name} #{last_name}"
end
```

- **`self` is implicit when you read, but not when you write**. Calling `name` inside an instance method calls `self.name`. But if you assign without `self.`, Ruby creates a new local variable instead of calling the writer:

```ruby
self.name = "Ada"  # calls the name= method
name = "Ada"       # creates a local variable
```

This is what the talk means by reading code like the interpreter: if you know which of these rules is in play, you understand the line instead of copy-pasting it.

---

## Pry

Most of the talk was a pry demo, and it's the part I want to go back to with a terminal open. Justin's whole `~/.pryrc` is [in a gist](https://gist.github.com/justin808/1fe1dfbecc00a18e7f2a), and ShakaCode's forum has a thread on [running Puma for debugging with pry](https://forum.shakacode.com/t/running-puma-for-debugging-with-pry/2018).

---

## Read more

- [Justin's talks on the ShakaCode site](https://shakacode.com/talks)
- [the slides](https://drive.google.com/file/d/1UUePkLINNN-Gpm5x5kPGBjNafrn29DdK/view?usp=sharing)
- [Justin's ~/.pryrc](https://gist.github.com/justin808/1fe1dfbecc00a18e7f2a)
- [pry threads on the ShakaCode forum](https://forum.shakacode.com/search?q=pry)
- [running Puma for debugging with pry](https://forum.shakacode.com/t/running-puma-for-debugging-with-pry/2018)
