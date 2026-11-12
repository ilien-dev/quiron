blockjob: drop BlockJob.blk field

Remove BlockJob.blk now that block-stream has its own BlockBackend.
It was the last block job that meaningfully used the shared field;
other jobs already maintain their own objects for accessing source
nodes.

Block jobs commonly operate on multiple nodes, so keeping a single
BlockBackend in the common structure is a poor fit. Let each job
manage the objects it needs in its own state, treating source and
target nodes symmetrically where appropriate.

The remaining use of BlockJob.blk is permission handling. Move those
permissions to the block-job child created by block_job_create(),
preserving the required access without retaining an otherwise unused
BlockBackend.

Also remove mirror's code for restoring the shared backend's state.
With BlockJob.blk gone, that cleanup is unnecessary; it likely became
redundant when the bs->job pointer was removed.

Update iotest 141's expected output because qmp_blockdev_del() no
longer fails its bdrv_has_blk(bs) check. Deletion is still rejected,
but the resulting error describes the remaining blocker more directly.

Give the job in iotest 283 an explicit ID. Moving permission checks
from the backend to the block-job child makes job ID validation occur
earlier, so the test otherwise reports "Invalid job ID" before reaching
the intended permission failure.

[Source](https://git.zx2c4.com/qemu/log/include/block/blockjob.h?showmsg=1)
