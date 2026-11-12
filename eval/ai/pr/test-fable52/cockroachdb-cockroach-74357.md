This PR is a series of small cleanups in `pkg/sql/rowenc`, done while things
are quiet. Each commit stands alone and is best reviewed individually. None of
them is intended to change behavior.

#### rowenc: remove dead code

Several exported helpers have had no callers since the key-encoding logic was
reworked. They are removed, along with the tests that exercised only them.
Some of the remaining helpers were exported but used only within the package;
those are now unexported to shrink the package's surface area.

#### rowenc: move value-side encoding into its own subpackage

The package mixed three unrelated concerns: index key encoding, value-side
encoding of datums, and assorted utilities for index fetching. The value-side
encoding and decoding functions move to `rowenc/valueside`, mirroring the
existing split for key-side encoding. Callers are updated mechanically. This
also lets a few packages that only need to decode values stop depending on all
of `rowenc`, and by extension on its descriptor dependencies.

#### rowenc: simplify index key construction signatures

A number of functions took both a table descriptor and an index descriptor
when they only needed the index's key columns and directions. They now take
the narrower inputs. This removes a handful of redundant column map lookups at
call sites and makes it clearer what each function actually reads.

#### rowenc: clean up comments and naming

Comments that referred to interleaved tables, or to functions that no longer
exist, are corrected or deleted. A few parameters are renamed for consistency
(`colMap` vs. `colIDToRowIndex`), and the package doc comment now describes
what lives where.

### Notes for reviewers

- The move commit is large, but it is purely mechanical: no function bodies
  change, only their package and import paths.
- The signature change is the only commit that touches logic at call sites. I
  kept it separate so that it can be dropped or reverted independently if
  anyone objects.
- There are no new tests, since no behavior changes. Existing unit tests and
  logic tests cover the affected paths, and the encoding round-trip tests move
  with the code they cover.
- I ran the relevant microbenchmarks before and after and saw no difference
  outside of noise.

Epic: None

Release note: None
