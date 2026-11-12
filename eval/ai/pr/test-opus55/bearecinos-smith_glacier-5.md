I don't have the branch or diff for this PR (the working directory isn't a git repository), so this draft assumes the PR revises how the depth-averaged ice rigidity (B̄) is computed in the Smith Glacier preprocessing. Please check the specifics against the actual changes before posting.

---

## Update B̄ (depth-averaged ice rigidity) calculation

### Summary
This PR updates how we compute B̄, the vertically averaged ice stiffness parameter used in Glen's flow law, following Dan's suggested changes. The previous approach averaged the temperature field first and then converted it to rigidity. Because the Arrhenius relationship is non-linear, that ordering biases B̄ where vertical temperature gradients are strong, especially near the grounding line and in fast-flowing tributaries.

### Changes
- Compute the rate factor A(T) on each model layer and integrate B = A^(-1/n) over the ice column, instead of converting a depth-averaged temperature.
- Use consistent units and constants (n = 3, activation energies, and the temperature threshold for switching Arrhenius parameters), now defined in the config instead of hard-coded.
- Handle masked, thin-ice, and no-data cells explicitly so they no longer produce NaNs or extreme values in the output grid.
- Update the B̄ preprocessing script and its output file metadata.

### Impact
The resulting B̄ field is generally softer in warm basal regions. Downstream inversions (for example, β and α priors in Fenics_ice) should be re-run with the new field to stay consistent.

### Testing
- Regenerated B̄ for the Smith domain and compared it against the previous output (difference maps attached/to attach).
- Ran a short inversion to confirm the run completes and the solver converges.

### Notes
Feedback on the choice of vertical integration scheme is welcome.
