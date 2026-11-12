## Implement generating a new template

This PR adds a `new` command to the Zagreus generator. It scaffolds a fresh template project so users no longer have to copy and strip down an existing template by hand.

### What it does
- Adds a `new <name>` subcommand to the generator CLI.
- Creates a new directory named after the template, containing:
  - a minimal `zagreus-template.yaml` with the template name and sensible defaults for the dev server and build options
  - a starter SVG with a placeholder element, ready to open in Inkscape
  - empty `animations.yaml` and `elements.yaml` files that show the expected structure
  - a basic `.gitignore` for build output
- Stops with a clear error if the target directory already exists and is not empty, so existing work is never overwritten.

### Notes
- Template files are embedded in the binary, so the command works offline.
- The README now covers the new command in the getting-started section.

### Testing
- Ran `zagreus-generator new my-template`, then `build` and `watch` on the result. Both succeeded without changes.
- Confirmed that running it against a non-empty directory fails as expected.
