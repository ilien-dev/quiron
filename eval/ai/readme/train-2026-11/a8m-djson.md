# djson

**Fast Go decoder for dynamic JSON.**

djson decodes JSON into Go values whose shape you don't know ahead of time. It skips the reflection-heavy paths in `encoding/json` when you only need to read a few fields, and it avoids building intermediate trees when you only need to walk a document once.

## Why djson?

Most Go JSON work falls into one of two cases:

1. **The schema is known.** Define a struct and use `encoding/json` or a code generator. This is the right choice for most application code.
2. **The schema is dynamic.** Webhooks, log pipelines, third-party APIs, and configuration files often have fields that vary by message type, version, or tenant. Decoding into `map[string]any` works, but it is slow, allocates heavily, and forces type assertions everywhere.

djson targets the second case. It provides a small set of primitives for reading dynamic JSON quickly and safely.

## Features

- **Path-based access.** Pull values out of nested documents with a dot-and-index path such as `user.roles[0].name`, without decoding the whole document.
- **Lazy decoding.** Values are parsed only when you ask for them.
- **Typed accessors.** Read values as `string`, `int64`, `float64`, `bool`, `[]byte`, or nested documents, with explicit errors for type mismatches.
- **Single-pass walking.** Iterate over objects and arrays once, with a callback per key or element.
- **Low allocation.** Reuse buffers across calls with a `Decoder` value and `sync.Pool`-backed helpers.
- **No reflection on the hot path.** Dynamic lookups do not go through `reflect`.
- **Strict and lenient modes.** Choose whether unknown escapes, duplicate keys, or trailing data are errors.

## Installation

Requires Go 1.22 or later.

```sh
go get github.com/example/djson
```

Import it in your code:

```go
import "github.com/example/djson"
```

## Quick start

### Read a single field

```go
package main

import (
    "fmt"
    "log"

    "github.com/example/djson"
)

func main() {
    data := []byte(`{"user":{"id":42,"name":"Ada","roles":["admin","dev"]}}`)

    id, err := djson.Int64(data, "user.id")
    if err != nil {
        log.Fatal(err)
    }

    name, err := djson.String(data, "user.name")
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println(id, name) // 42 Ada
}
```

### Read an array element

```go
role, err := djson.String(data, "user.roles[0]")
if err != nil {
    log.Fatal(err)
}
fmt.Println(role) // admin
```

### Walk an object

```go
err := djson.ForEachKey(data, "user", func(key string, value djson.Value) error {
    fmt.Printf("%s: %s\n", key, value.Raw())
    return nil
})
if err != nil {
    log.Fatal(err)
}
```

### Reuse a decoder

When you process many documents, create one `Decoder` and reuse it. This avoids repeated buffer allocation.

```go
dec := djson.NewDecoder(djson.Strict())

for _, msg := range messages {
    v, err := dec.Parse(msg)
    if err != nil {
        continue // skip malformed input
    }
    kind, _ := v.String("type")
    switch kind {
    case "order.created":
        // handle
    case "order.cancelled":
        // handle
    }
}
```

### Convert to a Go value

When you need the full document as ordinary Go values, use `Unmarshal`. It is equivalent to `encoding/json` into `any`, but it uses djson's parser:

```go
var out any
if err := djson.Unmarshal(data, &out); err != nil {
    log.Fatal(err)
}
```

## Error handling

Errors are typed so you can distinguish them:

| Error | Meaning |
|---|---|
| `djson.ErrNotFound` | The path does not exist in the document. |
| `djson.ErrType` | The value exists but cannot be read as the requested type. |
| `djson.ErrSyntax` | The input is not valid JSON. The error includes a byte offset. |
| `djson.ErrPath` | The path expression is malformed. |

Use `errors.Is` to check them:

```go
if errors.Is(err, djson.ErrNotFound) {
    // field is optional; use a default
}
```

## Options

Options are passed to `NewDecoder`:

- `djson.Strict()`: reject duplicate keys, trailing data, and invalid UTF-8.
- `djson.MaxDepth(n)`: limit nesting depth (default 512). Protects against malicious input.
- `djson.MaxSize(n)`: limit input size in bytes.
- `djson.UseNumber()`: keep numbers as their original text until you request a type.

Example:

```go
dec := djson.NewDecoder(
    djson.Strict(),
    djson.MaxDepth(64),
    djson.MaxSize(1 << 20), // 1 MiB
)
```

## Performance

djson is designed for workloads where you read a small part of each document. Its advantage shrinks when you need every field as a Go value, and in that case `encoding/json` into a typed struct is usually fastest.

To measure performance on your own data, run the included benchmarks:

```sh
go test -bench=. -benchmem ./...
```

To compare against `encoding/json` on your own payloads:

```sh
go test -bench=Compare -benchmem -args -corpus=path/to/samples
```

Results depend heavily on document shape, size, and hardware. Measure with representative input before choosing a decoder.

## When not to use djson

- Your schema is fixed and you control both ends. Use structs and `encoding/json`.
- You need full JSON Schema validation. djson does not validate against schemas.
- You need to write or modify JSON in place. djson is read-only.

## Project status

djson is pre-1.0. The path syntax and public API may change between minor versions. Breaking changes are listed in `CHANGELOG.md`.

## Contributing

1. Fork the repository and create a branch.
2. Add tests for any behavior change. Run `go test ./...` and `go vet ./...`.
3. Run `gofmt -s -w .` before committing.
4. Open a pull request with a short description of the problem and the fix.

Bug reports should include a minimal JSON input, the path expression used, the expected result, and the actual result. Fuzzing corpora that trigger crashes are especially welcome.

To run the fuzz tests:

```sh
go test -fuzz=FuzzParse -fuzztime=60s ./...
```

## License

Released under the MIT License. See `LICENSE` for details.

---

*Note: The import path, function names, and option names above are written as a design draft. I didn't have the djson source in this session, so check them against the actual code and update the examples before publishing. Word count is approximately 800.*
