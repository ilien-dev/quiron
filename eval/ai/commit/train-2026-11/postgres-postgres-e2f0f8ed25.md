Check for STATUS_DELETE_PENDING on Windows.

1.  Update our open() wrapper to check for NT's STATUS_DELETE_PENDING
    and translate it to the appropriate Unix-like errno.  When a file
    has been unlinked but other processes still hold handles to it,
    Windows keeps the directory entry around and fails new opens with
    ERROR_ACCESS_DENIED, which is indistinguishable from a real
    permissions problem.  The underlying NT status is retrieved with
    RtlGetLastNtStatus(), loaded dynamically from ntdll.dll.  A new file
    win32ntdll.c centralizes lookup of NT functions, in case we need
    more of them in the future.

2.  Remove non-working code that was trying to do something similar
    in our stat() wrapper, and instead reuse the open() wrapper's logic.
    As a side effect, stat() also gains resilience against transient
    sharing violation errors.

3.  Since stat() is called very early in process startup, remove the
    requirement that the Win32 signal event exist before
    pgwin32_open_handle() is reached.  Instead, teach pg_usleep() to
    fall back to a non-interruptible sleep if it is called before the
    signal event has been created.

This could be back-patched, but for now it goes into master only.
