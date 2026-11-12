# golang-geo

Geographical calculations in Go.

`golang-geo` is a project for working with geographic coordinates and calculations in Go. It provides a home for the mathematics behind location-aware applications, from comparing positions to reasoning about distances and directions on the Earth's surface.

Geographic calculations appear in mapping tools, delivery systems, travel applications, field research, and many other domains. The goal of this project is to make those calculations understandable, reusable, and straightforward to integrate into Go programs.

## Overview

Working with geographic data requires more than treating latitude and longitude as ordinary Cartesian coordinates. The Earth is curved, longitude wraps around, and a degree of longitude represents different distances at different latitudes.

`golang-geo` focuses on these geographic concerns. Its scope includes the foundations needed to represent positions, calculate relationships between locations, and build more specialized spatial workflows.

The repository's source code and tests should be treated as the authoritative reference for currently implemented functionality. Examples in this README describe usage concepts without assuming a particular exported API.

## Getting started

Install a recent Go toolchain and clone this repository:

```sh
git clone <repository-url>
cd golang-geo
```

Replace `<repository-url>` with the actual clone URL for your hosted copy of the project.

Inspect `go.mod`, when present, for the module path and minimum Go version. Use that module path when importing the project into another Go application.

Run the test suite from the repository root:

```sh
go test ./...
```

For additional checks during development:

```sh
go vet ./...
go test -race ./...
```

The race detector requires a supported operating system, architecture, and toolchain configuration.

## Core concepts

### Coordinates

A geographic position is typically expressed using latitude and longitude. Latitude measures angular distance north or south of the equator. Longitude measures angular distance east or west of the prime meridian.

When passing coordinates between systems, verify the expected ordering. Some formats use latitude followed by longitude; others use longitude followed by latitude. Mixing these conventions can produce plausible-looking but incorrect results.

### Units

Keep angular and linear units explicit. Coordinates commonly arrive in degrees, while trigonometric functions operate on radians. Distances may be expressed in meters, kilometers, miles, or another unit.

Convert units at clear boundaries in your application. Avoid silently combining values that use different conventions.

### Earth models

Different calculations make different assumptions about the Earth's shape. A spherical model can be useful for many application-level estimates. An ellipsoidal model accounts for flattening and may be appropriate when tighter accuracy is required.

Choose a calculation method according to your accuracy requirements, input quality, and performance constraints. Additional decimal places do not necessarily mean greater geographic accuracy.

## Typical workflow

A location-based application generally follows these steps:

1. Read coordinates from an input source.
2. Confirm coordinate ordering and units.
3. Validate values before performing calculations.
4. Apply the appropriate geographic operation.
5. Convert and format results for downstream consumers.

For example, a proximity feature might compare a user's position with several destinations, calculate a distance for each destination, and sort the results. A navigation feature might also need a bearing, while an analysis pipeline might aggregate measurements across many coordinate pairs.

Keep input parsing, geographic calculations, and presentation separate so each part remains easy to test.

## Accuracy and edge cases

Test geographic code with representative data, including situations that are easy to overlook:

- Identical coordinates.
- Positions near either pole.
- Locations on opposite sides of the antimeridian.
- Very short and very long distances.
- Invalid coordinates and non-finite numeric values.

Floating-point calculations can introduce small rounding differences. Where appropriate, compare results using a documented tolerance rather than exact equality.

Applications should also distinguish surface distance from route distance. A geographic calculation between two positions does not account for roads, terrain, access restrictions, or transportation networks.

## Development

Format Go code before submitting changes:

```sh
gofmt -w .
```

Keep changes focused and include tests for new behavior and bug fixes. For numerical work, document the formula, assumptions, units, and expected error tolerance.

Prefer examples that demonstrate practical behavior and remain consistent with the exported API. When changing an existing calculation, explain how the change affects results and whether callers need to adjust their expectations.

## Contributing

Bug reports are most useful when they include input coordinates, expected output, actual output, and the calculation method or reference used for comparison.

Feature proposals should explain the intended use case, required accuracy, and any relevant performance constraints. Discuss substantial API changes before investing in a large implementation.

## License

Consult the repository's license file for the terms governing use, modification, and distribution.
