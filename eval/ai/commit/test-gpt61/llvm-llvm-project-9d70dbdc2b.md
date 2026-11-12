[InstCombine] use poison as placeholder for undemanded elems

Use poison instead of undef for vector elements that are not demanded by their users. This gives InstCombine a suitable placeholder when simplifying partially constructed vectors and avoids assigning unnecessary guarantees to lanes whose values are irrelevant.

Vectors built through insertelement chains commonly start from undef. When those chains are folded into shufflevector instructions, the distinction between undef and poison becomes significant. Under the existing shuffle semantics, an undef mask element produces an undef result element. That can block poison propagation and make otherwise natural rewrites invalid: replacing an undef result with an element from an input vector can introduce poison where the original expression could not produce it.

For example, a shuffle that combines an input vector with an inserted scalar can appear equivalent to inserting that scalar directly into the input vector. However, an unused shuffle lane may originally be undef, while the corresponding lane retained by the insertion may be poison. The replacement therefore strengthens the possible undefined behavior and fails refinement checking.

The underlying issue also appears when refining an undef shuffle index. Choosing an index that selects an undef input can produce undef, while choosing an index that selects a poisoned input can produce poison. Giving undef mask entries special behavior is inconsistent with these independently valid choices. Poison provides a representation that accommodates the least defined result and supports subsequent simplification. See the [shuffle semantics discussion](https://lists.llvm.org/pipermail/llvm-dev/2019-November/137242.html).

Update the affected regression expectations across InstCombine and downstream vectorization and code generation tests. Existing undef matchers also accept poison, so matching opportunities remain available. SelectionDAG currently lowers poison to UNDEF, preserving the backend representation.

This change advances the transition toward poison placeholders for vector construction. Related work includes updating IRBuilder::CreateVectorSplat and the semantics of undef shuffle mask elements. Local Alive2 checks with poison-based insertelement variants can help expose latent assumptions in existing folds.

Reviewed By: nikic

Differential Revision: [D93586](https://reviews.llvm.org/D93586)
