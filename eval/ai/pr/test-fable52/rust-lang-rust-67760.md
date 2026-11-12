**Clear out target directory if compiler has changed**

Currently, rustbuild decides whether to wipe a stage's cargo output directory by comparing the mtime of a stamp file against its inputs. That misses the case where the compiler used to build the artifacts has itself changed, for example after bumping the bootstrap compiler or rebuilding an earlier stage with different codegen. Cargo then tries to reuse the stale artifacts, and the build fails with confusing errors such as "found crate compiled by an incompatible version of rustc" or metadata mismatches. The usual fix is a manual `rm -rf build`.

This PR makes `clear_if_dirty` aware of the compiler:

- Each cargo output directory records the compiler that produced its contents in a `.stamp` file.
- Before invoking cargo, rustbuild compares the stamp against the `rustc` it is about to use. If the stamp is older than that compiler, the directory is removed and recreated.
- The existing dependency-based checks (e.g. clearing libtest when libstd changes) are unchanged and go through the same path.

The cost is an occasional extra rebuild when the compiler really has changed, which was already required for correctness. Unchanged compilers do not trigger additional rebuilds, so incremental `x.py build` runs are unaffected.

Tested locally by building, swapping the stage0 compiler, and confirming that the affected directories were cleared and the build succeeded without manual cleanup.

r? @alexcrichton
