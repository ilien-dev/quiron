# Polymer conformation

## Summary

This PR adds `PolymerConformation`, a new species type that represents one or more `OrderedPolymerSpecies` held together by complexes formed between their monomers. Until now, a `ComplexSpecies` could only describe binding at a single position in a polymer, so there was no way to represent looping, bridging between two polymers, or any other structure where non-adjacent monomers interact.

## Changes

- **`PolymerConformation` class** (`species.py`): stores a set of polymers plus the complexes that connect them. Each complex keeps references to the monomers it contains, including their parent polymer and position, so the conformation can be reconstructed and compared unambiguously.
- **`Complex()` wrapper**: when the species passed in are monomers that sit inside one or more `OrderedPolymerSpecies`, it now returns a `PolymerConformation` instead of a flat `ComplexSpecies`. Existing behavior for free species and single-position binding is unchanged.
- **Naming and equality**: conformations get a canonical string representation, so two conformations built in a different order compare equal and are not duplicated in the CRN.
- **Parent and position handling**: `OrderedMonomer` copying was adjusted so that monomers inside a conformation retain the correct parent when polymers are copied or replaced.
- **Tests**: new unit tests cover construction, equality, naming, merging of conformations, and the updated `Complex()` logic.

## Motivation

This is groundwork for modeling DNA looping, multi-site transcription factor binding, integrase-mediated recombination between sites, and RNA secondary structure, all of which need a species that knows which parts of which polymers are in contact.

## Compatibility

No changes to the public API for existing models. Mixtures, components, and mechanisms that do not use polymers produce the same CRNs as before.

## Testing

`pytest` passes locally with the new tests included. Examples in the `examples/` folder were rerun to confirm that the output is unchanged.

## Follow-up

Mechanisms and components that generate conformations automatically will come in a separate PR.
