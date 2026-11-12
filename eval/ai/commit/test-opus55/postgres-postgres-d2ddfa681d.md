xlog.c: Remove global variables ReadRecPtr and EndRecPtr.

In most places, these variables necessarily hold the same values as
the eponymous members of the XLogReaderState that we use during WAL
replay, because ReadRecord() copies the structure members into the
global variables immediately after XLogReadRecord() returns. The one
exception is the window between a call to XLogBeginRead(), which
adjusts the structure members but not the globals, and the completion
of the next XLogReadRecord(). Outside that window, the two copies
must be identical.

Analysis of the existing call sites shows that the only place where
either global is referenced at a point where it might differ from the
corresponding structure member is the use of EndRecPtr inside
XLogPageRead(). Everywhere else, we can simply consult the
XLogReaderState directly, so this commit switches those references
over and removes the global variables altogether.

For XLogPageRead(), the existing reference to EndRecPtr is replaced
with xlogreader->EndRecPtr. During the window described above, this
value may now be the one set by XLogBeginRead() rather than a stale
value left over from the previously read record. That is arguably
more correct, since the purpose of the check is to decide whether we
are about to read the record at the reader's current position, and
in practice the difference does not affect behavior because the
relevant code paths only examine the value after a record has been
successfully read.

Keeping two copies of the same state that can silently drift apart
makes the WAL replay code harder to reason about, and has been a
source of confusion when reviewing patches that touch recovery. Since
the reader state is already passed to, or reachable from, all the
functions involved, removing the duplicates simplifies the code
without requiring any new plumbing. Callers that previously relied on
the globals now consult xlogreader->ReadRecPtr and
xlogreader->EndRecPtr instead.

Reviewed-by: (reviewers)
Discussion: (mailing list thread link)
