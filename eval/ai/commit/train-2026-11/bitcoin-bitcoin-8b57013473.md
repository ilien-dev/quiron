[net processing] Remove nStartingHeight check from block relay

When a new block is connected, UpdatedBlockTip() queues it for
announcement to every peer, except peers whose nStartingHeight is more
than 2000 blocks above the new tip. The check dates from early versions
of the software. Its purpose was to avoid sending inventory for old
blocks to peers that were already far ahead of us, for example while we
were still catching up to the chain.

The check is no longer needed:

- UpdatedBlockTip() already returns early while we are in initial block
  download, so blocks are not announced during IBD at all.
- SendMessages() skips announcing any block that the peer is already
  known to have (PeerHasHeader()), and peers ahead of us will have sent
  us headers covering those blocks.
- nStartingHeight is self-reported in the peer's version message and is
  never validated. A peer that sets it too high only opts itself out of
  block announcements. This makes it unsuitable as an input to relay
  decisions.

Removing the check makes the block announcement logic simpler. It also
removes one of the last places where net processing acts on the
unverified starting height. The value is still kept for informational
purposes such as getpeerinfo.

There is no meaningful change in behaviour for honest peers.
