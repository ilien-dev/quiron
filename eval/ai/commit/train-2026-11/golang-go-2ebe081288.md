internal/fuzz: handle unrecoverable errors during minimization

When the fuzzing coordinator asks a worker to minimize an input, the
worker may hit an unrecoverable error, such as the process being killed
by the OS, running out of memory, or crashing in a way the worker cannot
report. Previously, minimizeInput treated any error from the fuzz
function as a failure to reproduce and carried on, and the coordinator
did not distinguish a worker that had exited from one that had simply
failed to shrink the input.

Now, when minimization encounters a fatal error, the worker stops
minimizing and returns the error. The coordinator records it, restarts
the worker if needed, and reports the crash using the best input found
so far rather than discarding it. If the original unminimized input
already caused the failure, it is still written to testdata/fuzz so that
the user can reproduce the problem.

This also avoids a hang where the coordinator waited on a minimization
result that would never arrive from a dead worker.

Add tests that simulate a worker exiting during minimization and check
that the coordinator reports the failure, keeps the crashing input, and
terminates cleanly instead of looping or blocking.
