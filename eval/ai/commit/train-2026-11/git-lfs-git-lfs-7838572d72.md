Support submodule.recurse = true

When a user sets submodule.recurse to true, Git makes many commands
behave as though --recurse-submodules had been passed. This affects
the Git commands Git LFS runs internally. Commands that read or
update the index and working tree then try to recurse into each
submodule.

Git LFS doesn't expect that. Our internal invocations operate on the
current repository only, and we handle submodules ourselves where
needed. When Git recurses on our behalf, a simple checkout or pull
can fail outright. It can also try to run the LFS filters in
submodules that don't use Git LFS at all, or pass paths that are
correct for the superproject but not for the submodule. Users have
reported "git lfs pull" and "git lfs checkout" failing with errors
about missing objects or unexpected paths after enabling the option.

The user's setting is meant for their own porcelain commands, not
for the plumbing we run underneath them. So pass
"-c submodule.recurse=false" to the Git subprocesses we spawn. This
restores the behavior we get when the option is unset. It doesn't
change how Git itself behaves when the user runs a recursive command
directly.

Add a test that sets submodule.recurse in a repository with a
submodule and verifies that pulling and checking out LFS objects
works as expected.
