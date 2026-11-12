iscsi: Handle large Text responses.

Discovery sessions can return target lists too large to fit in a single
Text response PDU. Add support for sending and receiving these responses
across multiple PDUs so that discovery can handle larger target lists.

Introduce a higher-level API in libiscsiutil that sends and receives key
sets, hiding the individual PDU exchanges from callers. The new routines
handle splitting outgoing responses and assembling incoming response data,
including the empty Text PDUs used to acknowledge intermediate responses.

Update ctld and iscsid discovery handling to use this API in place of
constructing and processing TextRequest and TextResponse PDUs directly.
This keeps the exchange logic in the shared library and lets both daemons
operate on complete key sets.

Text requests continue to use a single PDU, since there is currently no
use case requiring larger requests. Support for exchanges spanning
multiple PDUs is therefore limited to Text responses.

Reported by: Jithesh Arakkan @ Chelsio
Sponsored by: Chelsio Communications

[Source: FreeBSD D33548](https://reviews.freebsd.org/D33548)
