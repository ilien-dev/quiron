IPv4: fix redirect sending conditions

The IPv4 fast-forwarding path can send ICMP redirects to gateways
that are not on a directly connected network. Such multi-hop redirects
do not provide the sender with a valid next hop and can result in
incorrect routing behavior.

Correct the checks used by ip_tryforward() to prevent redirects in
cases where they should not be sent. Keep most of the decision logic
in ip_redir_alloc(), and copy the packet mbuf only after determining
that a redirect will be sent.

The redirect conditions originate in RFCs 792, 1009, and 1122 and
were further refined by RFC 1812. Update the comments in the
forwarding paths to describe which conditions are checked and where,
making it easier to compare their behavior.

Reported by: pi (on net@, 2021-12-04)
Differential Revision: https://reviews.freebsd.org/D33274
