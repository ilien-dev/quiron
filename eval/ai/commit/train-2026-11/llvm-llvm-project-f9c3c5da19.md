[OpenMP][IR-Builder] Introduce the finalization stack

Some OpenMP constructs need code emitted at the end of a region, such as
cancellation branches, destructor calls for privatized objects, and
barrier insertion. Callers of OpenMPIRBuilder currently track and emit
this finalization code themselves, which makes nested constructs hard to
get right when a cancel or early exit jumps out of several regions at
once.

This patch adds a finalization stack to OpenMPIRBuilder. When a region
is entered, the frontend pushes a FinalizationInfo entry holding a
callback that emits the cleanup code, along with a flag that says
whether the cleanup must also run on cancellation paths. Popping the
entry runs the callback at the correct insertion point. When a cancel
branch needs to reach enclosing finalizers, the builder walks the stack
from innermost to outermost, so each region's cleanup runs exactly once
and in the correct order.

No functional change is intended for existing code paths. The stack is
consulted only by the new paths added here, and the existing
finalization calls keep their current behavior.
