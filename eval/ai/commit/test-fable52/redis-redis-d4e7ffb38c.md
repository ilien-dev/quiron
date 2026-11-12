Improve active defrag in jemalloc 5.2 (#9778)

Background:
Following the upgrade to jemalloc 5.2, a defrag test that used to be
flaky started failing consistently (on 32bit), so we disabled it
(see #9645).

The test creates fragmentation in a single bin and expects active
defrag to bring it back down. With jemalloc 5.2 the defragger would
often stagnate: it kept scanning the keyspace and burning CPU, but
fragmentation stopped dropping well before it reached the target.

Root cause:
The defrag hint we patch into jemalloc used to hand back two numbers,
the utilization of the bin and the utilization of the slab holding
the pointer, and redis decided to move the allocation if the slab was
below the bin average. That logic has a few weaknesses, which became
far more visible with the way 5.2 manages slabs:

1. The bin average included slabcur, the slab that new allocations
   are currently served from. That slab is usually either nearly
   empty or nearly full, so it skews the average. With a small number
   of slabs in the bin (as in the test, and easily on 32bit) the skew
   is enough to make every other slab look "above average", so
   nothing gets moved.
2. A strict "less than average" comparison means that when the
   remaining slabs all have about the same utilization, none of them
   qualifies and the defragger can never finish the job.
3. Full slabs were still being considered, although moving an
   allocation out of a full slab gains nothing.

Solution:
Move the whole decision into jemalloc, where we hold the bin lock and
can look at the real state, and have the hint return a plain boolean:

- Never move allocations out of slabcur, new allocations are going to
  land there anyway.
- Never move allocations out of a full slab.
- Subtract slabcur's regions and slab count from the bin statistics
  before computing the average utilization.
- Defrag when the slab's utilization is lower than or equal to the
  average plus a 12.5% margin, so that slabs sitting right at the
  average are still drained instead of being left behind forever.

On the redis side, defrag.c no longer does any utilization math; it
just asks je_get_defrag_hint(ptr) whether the pointer should be
reallocated. The bin_util / run_util output arguments are gone.

Other changes:
- Re-enable the test that was disabled in #9645, now that it passes
  reliably on both 32bit and 64bit builds.
- Update the comments on the jemalloc patch so the next jemalloc
  upgrade can carry it forward more easily.
