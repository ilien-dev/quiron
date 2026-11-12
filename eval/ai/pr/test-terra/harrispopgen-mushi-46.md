**Draft PR description**

This PR introduces Aitchison geometry for working with mutation spectra as compositional data. A mutation spectrum describes the relative rates of mutation types, so its components are constrained to sum to one. Representing those proportions in log-ratio coordinates provides a way to work with their relative changes while avoiding direct optimization over the simplex.

The change provides compositional operations and transforms through `mushi.composition`, adapted from scikit-bio for compatibility with JAX. These include:

- Closure, perturbation, inverse perturbation, powering, and the Aitchison inner product.
- Centered log-ratio (CLR) and isometric log-ratio (ILR) transforms and their inverses.
- A Gram–Schmidt-derived basis for ILR coordinates, with support for checking a supplied basis.
- Multiplicative replacement for zero components and centralization around a geometric average.

The ILR transform maps a spectrum with *K* mutation types to *K − 1* real-valued coordinates. This representation supports inference of mutation spectrum history in an unconstrained coordinate space; the inverse transform maps results back to relative proportions. JAX compatibility also makes these operations suitable for use with automatic differentiation and just-in-time compilation.

Log-ratio methods require positive components. Inputs containing zeros therefore need a treatment such as multiplicative replacement before transformation. The module documentation describes the operations and includes examples. [Composition module documentation](https://harrispopgen.github.io/mushi/stubs/mushi.composition.html)

I couldn’t access the PR diff, so this draft is based on the published module documentation and should be checked against the actual changes before use.
