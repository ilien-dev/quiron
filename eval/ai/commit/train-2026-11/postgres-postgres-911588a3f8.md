Add fast path for validating UTF-8 text

Accelerate UTF-8 validation by processing larger blocks with fewer branches.
The existing validator checks individual bytes with comparisons and branches,
providing an exact count of validated bytes at a significant performance
cost. This work can account for a substantial share of COPY FROM execution,
and improvements to parallelism or line parsing will make validation an
increasingly important bottleneck.

Introduce fast paths covering ASCII input and general UTF-8 sequences.
Check ASCII data in 16-byte blocks using bitwise operations. When a block
contains non-ASCII bytes, validate it with a shift-based deterministic finite
automaton that handles multibyte characters. Both paths minimize branching,
keeping performance robust across different input byte patterns.

Retain the existing pg_utf8_verifystr() implementation for short strings
and whenever the fast validator detects an error. This preserves precise
reporting of the valid prefix while allowing longer, valid inputs to use
the faster algorithms.

UTF-8 validation is several times faster with these changes, with the
actual improvement depending on the platform and input byte distribution.

Review, performance testing, and additional development by Heikki
Linnakangas, Vladimir Sitnikov, Amit Khandekar, Thomas Munro, and Greg Stark.

[Source](https://git.postgresql.org/pg/commitdiff/911588a3f816d875261d8f7d89e2517978831cd5)
