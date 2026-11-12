tcp: TCP output method can request tcp_drop

The advanced TCP stacks (BBR, RACK) may decide to drop a connection
while they are performing output on it.  The default stack never does
this, so the existing framework assumes that tfb_tcp_output() always
returns with a locked and valid tcpcb.  This assumption does not hold
for the alternative stacks and leads to use-after-free conditions when
a caller touches the tcpcb after output.

Extend the KPI to satisfy the needs of the advanced stacks.  If the
output method returns a negative error code, the caller is required
to call tcp_drop() on the connection.

Provide three inline wrappers in tcp_var.h for calling the output
method:

- tcp_output() keeps the existing KPI and is used where we know we
  are working with the default stack, or where the return value is
  handled explicitly.
- tcp_output_unlock() calls tcp_drop() if requested and always
  returns with the inpcb unlocked.
- tcp_output_nodrop() asserts that the stack did not request a drop
  and returns the plain error code.

Convert the callers throughout the TCP code to use the appropriate
wrapper.

Reviewed by:	rrs, tuexen
Differential Revision:	https://reviews.freebsd.org/
