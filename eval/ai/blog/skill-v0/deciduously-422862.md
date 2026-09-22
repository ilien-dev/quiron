# Using bitwise operators: why waste space use many bits when few bits do trick?

If you've spent most of your programming career in high-level languages, there's a good chance bitwise operators feel like a relic. They're something you vaguely remember from a computer science course, filed away next to assembly language and pointer arithmetic. But bitwise operations are still relevant, and understanding them can make you a sharper programmer even if you never write a line of C in your life.

In this post I'm going to go over what bitwise operators are, why they matter, and where you might still use them today.

## What are bits, really?

At the lowest level, every piece of data your computer works with is represented as a sequence of binary digits, or bits, each one either a 0 or a 1. A byte is a group of 8 bits. Everything from integers to characters to images is built up out of these tiny binary pieces.

When you write `int x = 5;` in most languages, that 5 is stored under the hood as `00000101` (in an 8-bit representation). Bitwise operators let you manipulate those individual bits directly. The number stops being an abstract whole and becomes a row of bits you can change one at a time.

## The basic bitwise operators

Most C-family languages (and plenty of others) support the same core set of bitwise operators:

- `&` (AND) returns 1 for each bit position where both operands have a 1.
- For `|` (OR), you get 1 for each bit position where at least one operand has a 1.
- `^` (XOR) returns 1 for each bit position where exactly one operand has a 1.
- The `~` (NOT) operator flips every bit.
- `<<` (left shift) shifts bits to the left, filling with zeros.
- And `>>` (right shift) shifts bits to the right.

I'll start with a quick example using AND:

```
  0101   (5)
& 0011   (3)
------
  0001   (1)
```

`5 & 3` equals `1`, because the last bit is the only one set to 1 in both numbers.

## Why would you ever use these?

Fair question, and one I'd ask too. Most modern developers spend their days working with arrays, objects and high-level abstractions, and they rarely touch raw bits. Bitwise operations still show up in a surprising number of places, though.

### 1. Flags and permissions

A classic use case is representing multiple boolean flags in a single integer. You can skip the pile of separate boolean variables and pack them into the bits of one number:

```c
#define READ    1  // 001
#define WRITE   2  // 010
#define EXECUTE 4  // 100

int permissions = READ | WRITE; // 011 — read and write, no execute
```

Then you can check for a specific permission using AND:

```c
if (permissions & WRITE) {
  // has write access
}
```

This pattern shows up in file permission systems, in game engines (for entity flags) and in plenty of low-level APIs.

### 2. Performance-critical code

Bitwise operations are extremely fast because they map directly to how the CPU processes data. There are no loops and no branching, just raw binary math. In performance-sensitive work like game development, embedded systems or graphics programming, swapping more "readable" logic for bitwise tricks can speed things up in a way you'll notice.

One common trick is multiplying or dividing by powers of two with shifts in place of the `*` or `/` operators:

```c
int doubled = x << 1;  // equivalent to x * 2
int halved  = x >> 1;  // equivalent to x / 2
```

Modern compilers often do this optimization automatically. I find that knowing the trick still helps you reason about performance when it matters.

### 3. Hashing and cryptography

Hashing algorithms and cryptographic functions are built on bitwise operators. XOR in particular shows up constantly. It's reversible, it's cheap to compute, and it has useful mathematical properties (like the fact that `a ^ a = 0` and `a ^ 0 = a`).

A classic example, if a slightly gimmicky one, is swapping two variables with XOR and no temporary variable:

```c
a = a ^ b;
b = a ^ b;
a = a ^ b;
```

I wouldn't use that in production code today. I still like it as a neat demonstration of how far you can push bitwise math.

### 4. Memory-constrained environments

Back when memory was scarce (and still today in embedded systems), packing multiple values into fewer bits mattered a lot. Why waste a full byte on a value that only needs 2 or 3 bits of information? Developers would pack several small values into a single byte or word with bit manipulation.

That's where I got the title of this post. Why waste space using many bits when a few bits will do the trick? If you only need to represent 4 possible states, you don't need a whole integer. Two bits will do just fine.

## Bitwise vs. logical operators

Here's a common source of confusion I want to call out: bitwise operators (`&`, `|`) are different from logical operators (`&&`, `||`). Logical operators work on boolean expressions as a whole, and they short-circuit. Bitwise operators work bit by bit on the binary representation of a value.

```js
5 & 3   // 1 (bitwise AND)
5 && 3  // 3 (logical AND, returns second operand if first is truthy)
```

Mixing these up is a classic source of bugs, especially in languages like JavaScript where the two look deceptively similar.

## Should you use bitwise operators in everyday code?

For most application-level code you probably won't reach for bitwise operators often. Readability usually wins over micro-optimizations, and most modern languages give you cleaner abstractions (like proper boolean arrays, enums or sets) for the same ideas bitwise flags used to handle.

I still think understanding bitwise operations is worth it. It deepens your understanding of how computers represent and process data. It comes in handy in specific domains: systems programming, graphics, embedded development, competitive programming and certain algorithm optimizations. And it helps you read legacy code or specialized libraries that do use these techniques.

## Wrapping up

Bitwise operators might feel like a throwback to lower-level programming, but they're still in use. They're fast, they're elegant in the right context, and computers are built on them. Even if you don't use them every day, I'd argue a solid grasp of AND, OR, XOR, NOT and bit shifting will make you a more well-rounded developer. It might even save the day the next time you're squeezed for performance or memory.

So the next time you're tempted to reach for a full integer to store a simple flag, ask yourself: why waste space using many bits when a few bits do the trick?
