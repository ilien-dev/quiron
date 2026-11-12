# tslint-immutable

TSLint rules to disable mutation in TypeScript.

`tslint-immutable` is a set of custom [TSLint](https://palantir.github.io/tslint/) rules that flag mutating operations in TypeScript code. Use them to enforce immutable data patterns: `const` bindings, read-only objects and arrays, and functional updates that return new values instead of changing existing ones.

> **Note:** TSLint was deprecated in 2019. This package is useful for existing TSLint setups and as a reference for porting similar rules to [ESLint](https://eslint.org/) or [typescript-eslint](https://typescript-eslint.io/).

## Contents

- [Why immutability?](#why-immutability)
- [Installation](#installation)
- [Configuration](#configuration)
- [Rules](#rules)
- [Examples](#examples)
- [Fixing violations](#fixing-violations)
- [Limitations](#limitations)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Why immutability?

Mutation makes code harder to reason about. When a value can change at any point, every reader must track every place that might modify it. Immutable code avoids this:

- **Predictable state.** A value that never changes cannot surprise you later.
- **Safer concurrency.** Shared data that is never modified needs no locks.
- **Easier testing.** Pure functions that return new values are simple to test in isolation.
- **Reliable change detection.** Frameworks such as React and Redux can compare references instead of walking whole structures.

TypeScript already offers `const`, `readonly`, and `ReadonlyArray<T>`, but none of them are enforced by default. `tslint-immutable` closes that gap by reporting violations at lint time.

## Installation

Install the package as a development dependency alongside TSLint and TypeScript:

```bash
npm install --save-dev tslint-immutable tslint typescript
```

or with Yarn:

```bash
yarn add --dev tslint-immutable tslint typescript
```

Requirements:

- Node.js 12 or later
- TSLint 5.x
- TypeScript 3.x or later

## Configuration

Add the rules to your `tslint.json`. Rules are loaded from the package through the `rulesDirectory` setting, and you enable each one under `rules`:

```json
{
  "extends": ["tslint:recommended"],
  "rulesDirectory": ["node_modules/tslint-immutable/rules"],
  "rules": {
    "no-let": true,
    "no-object-mutation": true,
    "no-array-mutation": true,
    "no-delete": true,
    "no-var-keyword": true
  }
}
```

If you use the TSLint `extends` option with a shareable configuration, you can also list the rules in a separate file and extend it:

```json
{
  "extends": ["tslint-immutable/all"],
  "rules": {
    "no-let": false
  }
}
```

The `all` preset enables every rule in the package. Disable individual rules as needed. Check the package's `README` for the presets that are currently available, because they may change between releases.

### Rule options

Some rules accept options. Pass them as an array after the severity value:

```json
{
  "rules": {
    "no-object-mutation": [true, { "ignore-prefix": "mutable" }]
  }
}
```

Options let you allow mutation in specific places, such as builder classes or test fixtures, by naming identifiers or prefixes that the rule should skip.

## Rules

| Rule | Flags | Typical fix |
| --- | --- | --- |
| `no-let` | `let` declarations | Use `const`, or restructure the code |
| `no-var-keyword` | `var` declarations | Use `const` |
| `no-object-mutation` | Assignments to object properties, such as `obj.x = 1` or `obj["x"] += 1` | Use spread syntax or `Object.assign({}, obj, { x: 1 })` |
| `no-array-mutation` | Mutating array methods such as `push`, `pop`, `splice`, `sort`, and `reverse` | Use `concat`, `slice`, spread, `map`, or `filter` |
| `no-delete` | The `delete` operator | Build a new object without the property |
| `no-this` | Assignments through `this` outside constructors | Return new instances or use function parameters |
| `no-expression-statement` | Expression statements whose only purpose is a side effect | Return values, or wrap side effects in clearly named functions |
| `no-method-signature` | Method signatures in interfaces | Use property signatures with function types |
| `no-throw` | `throw` statements | Return result types such as `Either` or `Result` |

Each rule's full behavior, including its options and edge cases, is documented in the source comments of its file in `rules/`.

## Examples

### Local bindings

```typescript
// Flagged by no-let
let total = 0;
for (const item of items) {
  total += item.price;
}

// Accepted
const total = items.reduce((sum, item) => sum + item.price, 0);
```

### Object updates

```typescript
// Flagged by no-object-mutation
function rename(user: User, name: string): User {
  user.name = name;
  return user;
}

// Accepted
function rename(user: User, name: string): User {
  return { ...user, name };
}
```

### Array updates

```typescript
// Flagged by no-array-mutation
function addItem(list: string[], item: string): string[] {
  list.push(item);
  return list;
}

// Accepted
function addItem(list: ReadonlyArray<string>, item: string): string[] {
  return [...list, item];
}
```

### Removing properties

```typescript
// Flagged by no-delete
delete config.debug;

// Accepted
const { debug, ...rest } = config;
```

### Sorting

`Array.prototype.sort` sorts in place and returns the same array, so it is flagged by `no-array-mutation`:

```typescript
// Flagged
const sorted = items.sort((a, b) => a.id - b.id);

// Accepted
const sorted = [...items].sort((a, b) => a.id - b.id);
```

## Fixing violations

Most violations have a direct replacement, as shown above. Some patterns need more work:

1. **Loops with accumulators.** Replace `for` loops that build up a value with `reduce`, `map`, or `filter`.
2. **Mutable builders.** Classes that construct large objects step by step may need a builder that returns a new instance on each call, or a single object literal assembled at the end.
3. **Interop with mutable libraries.** Some APIs require mutation. Isolate that code in one small function, document why it mutates, and disable the rule for that line only:

   ```typescript
   // tslint:disable-next-line:no-object-mutation
   legacyLib.config.enabled = true;
   ```

   Use line-level disables sparingly. Each one is a place where the guarantee does not hold.

4. **Performance-sensitive code.** Copying large arrays on every update has a cost. Profile before optimizing. If a hot loop must mutate, keep the mutation local to the function and return an immutable result.

## Limitations

- **Type information is not checked.** The rules inspect syntax, so they cannot tell whether a method such as `sort` is called on an array or on a custom type with the same method name. Some false positives are possible.
- **Deep mutation is not fully tracked.** A rule may catch `a.b.c = 1` but cannot always tell whether `a.b` came from a shared reference.
- **Third-party code is not checked.** The rules only lint files in your project.
- **TSLint is no longer maintained.** Future TypeScript syntax may not be supported. Test the rules when you upgrade TypeScript.

## Development

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd tslint-immutable
npm install
```

Common scripts:

```bash
npm run build   # Compile TypeScript sources
npm test        # Run the rule test suite
npm run lint    # Lint the project with its own rules
```

Each rule has a test file in `test/rules/` with the code to lint, the expected failures, and the expected fixes where applicable. To add a rule, create a file in `src/rules/`, add tests for valid and invalid cases, and document it in the table above.

## Contributing

Contributions are welcome. Before opening a pull request:

1. Open an issue to discuss significant changes.
2. Add or update tests for every behavior change.
3. Run `npm test` and `npm run lint` and confirm both pass.
4. Keep each pull request focused on a single change.

Bug reports should include the TSLint and TypeScript versions, the rule configuration, and a minimal code sample that reproduces the problem.

## License

Released under the MIT License. See `LICENSE` for details.

---

*I wrote this from the project description only and did not inspect the source. Before publishing, check the rule names and options in the table and the examples against the actual code, and fill in the repository URL, the preset names, and the license.*
