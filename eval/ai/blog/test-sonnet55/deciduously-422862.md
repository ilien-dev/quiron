There's a famous line from *The Office* where Kevin explains his philosophy of communication: "Why waste time say lot word when few word do trick?"

Bitwise operators are that philosophy applied to data. Why store eight booleans in eight bytes when one byte holds them all? Why use a 32-bit integer for a number between 0 and 15? Why divide when a shift does the job?

Most of us learn `&`, `|`, `^`, `~`, `<<` and `>>` in school, pass the exam, and never touch them again. That's a shame, because they show up constantly in real systems: file permissions, network protocols, graphics, compilers, game engines, embedded firmware, and databases. This post is a practical tour of where they pay off, and where they'll bite you.

Examples are in C, since it makes the bit widths explicit, but the ideas carry over to almost any language.

## A 60-second refresher

| Operator | Name | Example (4 bits) | Result |
|---|---|---|---|
| `a & b` | AND | `1100 & 1010` | `1000` |
| `a \| b` | OR | `1100 \| 1010` | `1110` |
| `a ^ b` | XOR | `1100 ^ 1010` | `0110` |
| `~a` | NOT | `~1100` | `0011` |
| `a << n` | Shift left | `0011 << 2` | `1100` |
| `a >> n` | Shift right | `1100 >> 2` | `0011` |

A useful mental model for the first four is that each one works on every bit position independently. A shift slides the whole pattern left or right. A left shift by `n` multiplies by 2ⁿ, and a right shift on an unsigned value divides by 2ⁿ (rounding down).

## Use case 1: Flags in a single byte

Suppose you're modeling permissions. The naive approach is three booleans:

```c
bool can_read, can_write, can_exec;
```

That's at least three bytes, plus padding, and passing them around is clumsy. With bit flags, it's one byte:

```c
#include <stdint.h>

enum {
    PERM_READ  = 1u << 0,  // 0b001
    PERM_WRITE = 1u << 1,  // 0b010
    PERM_EXEC  = 1u << 2,  // 0b100
};

uint8_t perms = 0;

perms |= PERM_READ | PERM_WRITE;   // grant read + write
perms &= ~PERM_WRITE;              // revoke write
perms ^= PERM_EXEC;                // toggle exec

if (perms & PERM_EXEC) {
    // exec bit is set
}
```

The four operations you'll use constantly:

- **Set** a bit: `flags |= MASK`
- **Clear** a bit: `flags &= ~MASK`
- **Toggle** a bit: `flags ^= MASK`
- **Test** a bit: `(flags & MASK) != 0`

This is exactly how Unix file modes (`rwxr-xr-x`), Linux syscall options like `O_RDONLY | O_CREAT`, and Win32 API flags work. Once you recognize the pattern you'll see it everywhere.

A nice side effect is that combining options is a single `|`, and a function can take a whole set of options in one integer parameter instead of a long list of booleans.

## Use case 2: Bitsets, where the savings get dramatic

A `bool` array uses one byte per element, even though a boolean needs one bit. For small arrays, who cares. For a billion entries, that's 1 GB versus 125 MB.

Here's a minimal bitset:

```c
#include <stdint.h>
#include <stdlib.h>

typedef struct {
    uint64_t *words;
    size_t nbits;
} Bitset;

Bitset *bitset_new(size_t nbits) {
    Bitset *b = malloc(sizeof *b);
    b->nbits = nbits;
    b->words = calloc((nbits + 63) / 64, sizeof(uint64_t));
    return b;
}

void bitset_set(Bitset *b, size_t i)   { b->words[i >> 6] |=  (1ULL << (i & 63)); }
void bitset_clear(Bitset *b, size_t i) { b->words[i >> 6] &= ~(1ULL << (i & 63)); }
int  bitset_test(const Bitset *b, size_t i) {
    return (b->words[i >> 6] >> (i & 63)) & 1;
}
```

Two bitwise tricks do the work here. `i >> 6` is `i / 64`, which picks the word. `i & 63` is `i % 64`, which picks the bit inside that word.

This is the engine behind the Sieve of Eratosthenes at scale, visited-sets in graph algorithms, Bloom filters, and the allocation bitmaps used by filesystems and memory allocators. It also makes set operations cheap. Union is `|` across words, intersection is `&`, and each instruction processes 64 elements at once.

## Use case 3: Packing fields together

Sometimes you have several small values that don't need a full integer each. A classic example is the RGB565 color format, common in embedded displays. Instead of 24 bits per pixel (8 each for red, green, blue), it uses 16: 5 bits red, 6 bits green, 5 bits blue. Green gets the extra bit because our eyes are more sensitive to it.

```c
uint16_t pack565(uint8_t r, uint8_t g, uint8_t b) {
    return (uint16_t)(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}

void unpack565(uint16_t c, uint8_t *r, uint8_t *g, uint8_t *b) {
    uint8_t r5 = (c >> 11) & 0x1F;
    uint8_t g6 = (c >> 5)  & 0x3F;
    uint8_t b5 =  c        & 0x1F;
    // Expand back to 8 bits, replicating the top bits into the low bits
    *r = (r5 << 3) | (r5 >> 2);
    *g = (g6 << 2) | (g6 >> 4);
    *b = (b5 << 3) | (b5 >> 2);
}
```

The pattern is always the same: **shift to position, mask to isolate**. To write a field, shift it into place and OR it in. To read a field, shift it down and AND with a mask of the field's width (`0x1F` is five 1-bits, `0x3F` is six).

You see this in IPv4 headers (a 4-bit version and a 4-bit header length share a byte), in game engines packing entity IDs with generation counters, in compact serialization formats, and in hash functions.

If you'd rather not hand-roll it, C offers bit-fields (`unsigned r : 5;`), but their memory layout is implementation-defined, so explicit shifts and masks are the portable choice for anything that crosses a wire or a file.

## Use case 4: Small tricks worth knowing

A handful of idioms come up so often they're worth memorizing.

**Is it a power of two?**

```c
bool is_pow2(uint32_t n) { return n && !(n & (n - 1)); }
```

A power of two has exactly one bit set. Subtracting 1 flips that bit to 0 and every bit below it to 1, so the AND is zero.

**Clear the lowest set bit.** `n & (n - 1)` does it, and it's the basis of a fast population count (the number of 1-bits):

```c
int popcount(uint64_t n) {
    int count = 0;
    while (n) {
        n &= n - 1;   // drop the lowest set bit
        count++;
    }
    return count;
}
```

This loops once per set bit rather than once per bit position. (In real code, prefer your compiler's builtin, like `__builtin_popcountll` in GCC and Clang, which usually compiles to a single CPU instruction.)

**Isolate the lowest set bit.** `n & -n` gives you just that bit. It's the key move in Fenwick trees (binary indexed trees).

**Modulo by a power of two.** `x & (m - 1)` equals `x % m` when `m` is a power of two (for unsigned `x`). Hash tables use this to wrap an index into a table whose size is a power of two, avoiding a slow division.

**Swap without a temp.** You've probably seen this one:

```c
a ^= b; b ^= a; a ^= b;
```

It works, but I'd treat it as a curiosity. Modern compilers do a plain swap just as well, it's harder to read, and it breaks if `a` and `b` alias the same variable (you'd zero it out).

## The gotchas

Bitwise code is compact, and compact code is easy to get subtly wrong.

**1. Operator precedence will betray you.** In C, comparison binds tighter than bitwise AND:

```c
if (flags & MASK == 0)    // parsed as: flags & (MASK == 0)  -- wrong!
if ((flags & MASK) == 0)  // what you meant
```

When in doubt, add parentheses. Always parenthesize bitwise expressions mixed with comparisons.

**2. Signed integers and shifts.** Right-shifting a negative signed value is implementation-defined (usually an arithmetic shift that preserves the sign). Left-shifting into or past the sign bit is undefined behavior. `1 << 31` on a 32-bit `int` is a classic trap. Use unsigned types (`1u << 31`, `1ULL << 40`) for bit manipulation.

**3. Shifting by too much.** Shifting by an amount greater than or equal to the type's width is undefined behavior in C. `x << 32` on a 32-bit value is not zero; it's a bug waiting to happen.

**4. Integer promotion surprises.** In C, `uint8_t` values get promoted to `int` in expressions. `~some_uint8` produces an `int` with the upper bits set, so comparisons like `~b == 0xF0` can fail unexpectedly. Cast the result back (`(uint8_t)~b`) when you need the narrow type.

**5. JavaScript is its own world.** Bitwise operators in JS convert operands to *32-bit signed integers*. That means `1 << 31` is negative, and values beyond 32 bits get silently truncated. Use `>>> 0` to get an unsigned result, or `BigInt` for wider values.

**6. Endianness.** If you pack bits into bytes that get sent between machines or written to disk, byte order matters. Define your format explicitly and don't assume.

## When *not* to use them

I'm a fan of bit tricks, but "clever" is not the same as "good." A few guidelines:

- **Don't use shifts to replace multiplication or division for speed.** `x * 8` and `x << 3` compile to the same thing in any modern compiler, and the multiplication says what you mean. The compiler already knows the trick.
- **Don't pack data you don't need to pack.** If you have a hundred booleans, a `bool` array is clearer and fast enough. Reach for bitsets when memory or cache pressure is a measured problem, or when you want fast set operations.
- **Name your masks.** `flags & 0x14` is a riddle. `flags & (PERM_EXEC | PERM_SETUID)` is documentation.
- **Wrap the ugliness.** Put bit manipulation behind small functions or macros (`bitset_test`, `pack565`) so the rest of your code reads normally, and test those functions thoroughly.
- **Measure first.** Bit-packing trades CPU work (shifts and masks) for memory savings. That's usually a win because memory access is the bottleneck, but not always.

## Wrapping up

Bitwise operators are a small toolkit with outsized reach. Once you're comfortable with set, clear, toggle, and test, plus the shift-and-mask pattern for packing fields, a surprising number of problems get smaller and faster: permission systems, compact data structures, protocol parsers, hash tables, and more.

Kevin's rule of thumb holds up well. Use few bits when few bits do the trick, and keep the code readable enough that the next person (probably you, in six months) can tell which bits you meant.

If you want to practice, here are three exercises:

1. Implement a `bitset_union` and `bitset_intersect` on the `Bitset` above.
2. Write a function that reverses the bits of a `uint8_t`.
3. Pack a date (year 0–4095, month 1–12, day 1–31) into a single `uint32_t`, then unpack it.

Got a favorite bit trick, or a bitwise bug that cost you an afternoon? Share it in the comments.
