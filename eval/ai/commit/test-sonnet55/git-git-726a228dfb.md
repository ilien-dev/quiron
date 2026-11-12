fast-export: fix surprising behavior with --first-parent

When fast-export is given --first-parent, the revision walk is limited
to the first-parent chain of the starting points. The commits that come
out of that walk are written to the stream along with their parent
lists, and this is where the surprise comes from. fast-export emits a
"from" line for the first parent and "merge" lines for the remaining
ones without checking whether those parents were ever part of the walk.
The resulting stream refers to commits that were never exported and
that the importer has no way to resolve.

For a history such as

    A---B---M---N
         \ /
          C

running "git fast-export --first-parent N" walks N, M, B and A. Commit
C is skipped, which is what the user asked for. But M is still written
with a "merge" line naming C, and since no mark was ever allocated for
C, the stream is not self-consistent. That defeats the whole point of
producing a linear export of the mainline.

Without --first-parent, the revision machinery rewrites the parents of
the commits it shows so that they only name commits that were also
shown. With --first-parent the walk never visits the side branches, but
the parent list on the commit is left untouched, because the code in
fast-export reads commit->parents directly rather than relying on a
rewritten list.

Fix this by dropping every parent other than the first when
--first-parent is in effect. An exported merge then becomes an ordinary
commit with a single parent. Its tree is kept as is, so the content of
the mainline is identical to the original history. This matches what
users reasonably expect: the first-parent history as a linear sequence
of snapshots, where each merge appears as the single change that
brought in the side branch.

There was some temptation to handle this more generally by checking
each parent against the set of exported commits. That would also cover
other ways of limiting the walk, such as negative revisions or --since.
However, those cases already work through the existing parent rewriting
and boundary handling, and changing them risks altering output that
people depend on. The narrow fix leaves the behavior of every other
option unchanged.

Add tests covering three situations:

  - a simple merge, where the side branch must not appear in the
    stream and the merge must be exported with exactly one parent;

  - a stream piped back into fast-import, which must succeed and yield
    a history whose commit count and trees match the first-parent
    history of the source repository;

  - an octopus merge, where all parents beyond the first are dropped.

The tests check the fast-import round trip instead of only grepping
the stream, so that they notice a dangling reference regardless of how
it happens to be spelled in the output.

Also add a short note to the fast-export documentation saying that
--first-parent flattens merges into single-parent commits, so that the
behavior is no longer a surprise to the next person who tries it.
