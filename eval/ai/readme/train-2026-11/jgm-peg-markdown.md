# peg-markdown

An implementation of markdown in C, using a PEG grammar.

peg-markdown reads Markdown text and produces HTML, LaTeX, groff, or other output formats. Instead of the regular-expression substitutions used by the original `Markdown.pl`, it parses the input with a formal [parsing expression grammar](https://en.wikipedia.org/wiki/Parsing_expression_grammar) compiled to C by the `leg` tool. The result is fast, predictable, and easy to extend.

## Table of contents

- [Why a PEG grammar?](#why-a-peg-grammar)
- [Features](#features)
- [Requirements](#requirements)
- [Building](#building)
- [Usage](#usage)
- [Extensions](#extensions)
- [Output formats](#output-formats)
- [Project layout](#project-layout)
- [Testing](#testing)
- [Using the parser as a library](#using-the-parser-as-a-library)
- [Contributing](#contributing)
- [License](#license)

## Why a PEG grammar?

Markdown's syntax is ambiguous in many corners: nested lists, emphasis inside links, and block quotes containing code. Most implementations deal with this by running a long chain of regular expressions over the text, and the order of those passes matters. Small changes can break unrelated constructs, and performance can degrade badly on pathological input.

A PEG describes the language directly, as ordered rules that the parser tries in sequence. This gives you:

- **A single source of truth.** The grammar file defines what is and isn't Markdown, rather than a pile of substitutions.
- **Linear-time parsing.** The generated parser memoizes where needed and avoids the exponential blowups common with backtracking regexes.
- **Easy extension.** New syntax is added by writing new rules, not by threading another regex through the pipeline.
- **A real syntax tree.** The parser builds an element tree first, and separate writers turn that tree into each output format.

## Features

- Complete implementation of the Markdown syntax, including reference links, nested block quotes, lists, and code blocks
- Grammar-driven parser generated with `leg`
- Multiple output formats from the same parse: HTML, LaTeX, and groff
- Optional extensions: smart typography, footnotes, and raw-HTML control
- Reads from files or standard input, writes to a file or standard output
- Small codebase with no runtime dependencies beyond the C standard library
- Usable as a command-line tool or linked into other programs

## Requirements

To build peg-markdown you need:

- A C compiler (GCC or Clang)
- GNU Make
- [`peg/leg`](https://www.piumarta.com/software/peg/) by Ian Piumarta, which turns the grammar into C
- [GLib 2](https://developer.gnome.org/glib/), used for strings and lists

On Debian or Ubuntu:

```sh
sudo apt-get install build-essential libglib2.0-dev
```

On macOS with Homebrew:

```sh
brew install glib pkg-config
```

On Windows, use MSYS2 or WSL and install the equivalent packages there.

The `peg/leg` source is included as a submodule or bundled directory in the repository, so you don't need to install it separately. Fetch it with:

```sh
git submodule update --init
```

## Building

From the top-level directory:

```sh
make
```

This builds `leg`, generates the parser from the grammar, and compiles the `markdown` executable. To remove build products:

```sh
make clean
```

To build with optimizations or debugging symbols, override the usual variables:

```sh
make CFLAGS="-O3"
make CFLAGS="-g -O0"
```

## Usage

Convert a file to HTML:

```sh
./markdown README.text > README.html
```

Read from standard input:

```sh
echo "Hello, *world*." | ./markdown
```

Produce another format with `-t`:

```sh
./markdown -t latex document.text > document.tex
./markdown -t groff document.text > document.roff
```

Write to a named file with `-o`:

```sh
./markdown -o output.html input.text
```

Show all options:

```sh
./markdown --help
```

Typical options:

| Option | Meaning |
| --- | --- |
| `-t FORMAT` | Output format: `html`, `latex`, or `groff` |
| `-o FILE` | Write output to `FILE` instead of standard output |
| `-x`, `--extensions` | Enable all extensions |
| `-v`, `--version` | Print the version and exit |
| `-h`, `--help` | Print usage information and exit |

Multiple input files are concatenated and parsed as one document.

## Extensions

Extensions are off by default so that plain Markdown behaves as expected. Enable them all with `-x`, or turn on individual ones with the options below.

- **Smart typography** (`--smart`): converts straight quotes to curly quotes, `--` and `---` to en and em dashes, and `...` to an ellipsis.
- **Footnotes** (`--notes`): supports inline notes written as `^[like this]` and reference-style notes.
- **Raw HTML filtering** (`--filter-html`): removes inline HTML from the input.
- **Style filtering** (`--filter-styles`): removes `<style>` blocks from the input.

Example:

```sh
./markdown --smart --notes essay.text
```

Input:

```markdown
"Smart quotes" -- and dashes... work.^[Footnotes too.]
```

Output (abridged):

```html
<p>“Smart quotes” – and dashes… work.<a class="note" href="#note1">[1]</a></p>
```

## Output formats

All writers walk the same element tree, so adding a format means adding one new writer rather than touching the grammar.

- **HTML**: clean, semantic markup for headings, lists, code blocks, and tables of references.
- **LaTeX**: output ready to include in a document. Special characters are escaped, and headings map to `\section` and friends.
- **groff**: suitable for rendering with `groff -mm` or similar macro packages.

## Project layout

```
.
├── markdown.c           # Command-line driver
├── markdown_lib.c       # Library entry points
├── markdown_parser.leg  # The PEG grammar
├── markdown_peg.h       # Shared types and declarations
├── parsing_functions.c  # Helpers called from grammar actions
├── utility_functions.c  # String and list utilities
├── odf.c / html.c / latex.c / groff.c  # Output writers
├── peg/                 # Bundled peg/leg parser generator
├── tests/               # Test inputs and expected outputs
├── Makefile
└── README.md
```

The file to read first is `markdown_parser.leg`. Block-level rules (paragraphs, lists, block quotes, verbatim blocks) come before inline rules (emphasis, links, code spans), and each rule carries an action that builds part of the tree.

## Testing

The test suite runs the converter over a set of input files and compares the results with expected output. To run it:

```sh
make test
```

The tests include the classic Markdown test suite, plus additional cases for edge conditions such as deeply nested lists, unusual emphasis combinations, and malformed links. If a test fails, the runner prints a diff between the actual and expected output.

When you fix a bug or add a feature, add a test pair to the `tests/` directory: one input file and one file containing the expected output.

## Using the parser as a library

The converter can be embedded in other C programs. Include the header, call the conversion function, and free the result:

```c
#include "markdown_lib.h"

int main(void) {
    char *html = markdown_to_string("Some *Markdown* text.",
                                    0 /* extensions */,
                                    HTML_FORMAT);
    puts(html);
    free(html);
    return 0;
}
```

Pass a bitwise OR of extension flags such as `EXT_SMART` and `EXT_NOTES` for the second argument. Link against GLib using `pkg-config`:

```sh
cc example.c markdown_lib.o markdown_parser.o utility_functions.o \
   $(pkg-config --cflags --libs glib-2.0) -o example
```

The parser is not thread-safe in a single shared state, so use one parser instance per thread or serialize calls.

## Contributing

Bug reports, test cases, and patches are welcome. A good contribution has these properties:

1. **It is focused.** Fix one problem or add one feature per change.
2. **It includes tests.** Add input and expected-output files for any behavior you change.
3. **It keeps the grammar readable.** Prefer small, well-named rules to clever ones, and comment any rule whose purpose isn't obvious.
4. **It passes `make test`.** Run the full suite before submitting.

When reporting a bug, include the smallest Markdown input that reproduces it, the output you got, and the output you expected.

## License

peg-markdown is dual-licensed under the GNU General Public License (version 2 or later) and the MIT license. You may use it under the terms of either. The bundled `peg/leg` generator is distributed under its own license, included in the `peg/` directory.
