Simplify swi for bus_dma.

When a DMA request using bounce pages completes, a swi is triggered to
schedule pending DMA requests using the just-freed bounce pages.  For
a long time this bus_dma swi has been tied to a "virtual memory" swi
(swi_vm).  However, all of the swi_vm implementations are the same and
consist of checking a flag (busdma_swi_pending) which is always true
and, if set, calling busdma_swi.  I suspect this dates back to the
pre-SMPng days and that the intention was for swi_vm to serve as a
mux.  However, in the current scheme there is no need for the mux.

Instead, remove swi_vm and vm_ih.  Each bus_dma implementation now
registers a private swi handler (busdma_ih) that runs busdma_swi
directly, and the busdma_swi_pending flag goes away.  The handler is
registered from a SYSINIT in each implementation rather than from the
MD startup code.

No functional change intended.
