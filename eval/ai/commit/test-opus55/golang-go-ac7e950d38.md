go/types: sort to reduce computational complexity of initOrder

The dependency graph used by initOrder is built in two phases. First,
a graph is constructed in which every package-level object (variables,
constants, functions) is a node. Then function nodes are removed from
the graph, because only the relative order of variable and constant
initialization matters. When a function node n is removed, each of its
predecessors is connected directly to each of its successors, so that
transitive dependencies through functions are preserved.

The cost of removing a single function node is proportional to
len(n.pred) * len(n.succ), and removing a node can increase the number
of edges on its neighbors. Function nodes were previously removed in
the order in which they appeared in the object map, which is
effectively arbitrary. For packages with many mutually referencing
functions, such as large generated files or packages with deep call
chains between helpers, a poor removal order could cause the edge sets
of the remaining nodes to grow rapidly. In the worst case this made
type checking such packages take time far out of proportion to their
size, dominated almost entirely by dependencyGraph.

This change sorts the function nodes before removal so that nodes with
the smallest cost, measured as the product of their in-degree and
out-degree, are removed first. Removing cheap nodes first keeps the
intermediate edge sets small, and in the common case where most
functions have few callers or few callees, it avoids the blowup
entirely. Ties are broken by source order so the result remains
deterministic and independent of map iteration order.

The order in which function nodes are removed does not affect the
resulting graph: after all function nodes are gone, the edges between
the remaining variable and constant nodes are the same regardless of
removal order. Consequently the computed initialization order, and any
reported initialization cycles, are unchanged. Only the amount of work
done to reach that result differs.

On a synthetic package containing several thousand interdependent
functions, type checking time drops from many seconds to well under
one second. Typical packages see no measurable difference, since their
function graphs are small enough that the removal order never
mattered.

The corresponding change in types2 is generated from this one via
go generate, keeping the two implementations in sync.

A test is added that constructs a package whose function graph
triggered the pathological behavior and checks that type checking
completes, along with existing initorder tests confirming the
initialization order is unchanged.
