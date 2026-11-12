# pismo

**Extracts machine-readable metadata and content from Web pages.**

pismo takes a URL, a file, or a raw HTML string and returns structured data: title, author, publication date, language, main body text, lead image, keywords, feeds, and more. It is built for crawlers, content pipelines, link-preview services, and research tools that need clean, predictable output from messy markup.

---

## Table of contents

- [Why pismo](#why-pismo)
- [Installation](#installation)
- [Quick start](#quick-start)
- [What gets extracted](#what-gets-extracted)
- [Usage](#usage)
- [Configuration](#configuration)
- [Command-line interface](#command-line-interface)
- [How it works](#how-it-works)
- [Limitations](#limitations)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Why pismo

Web pages describe themselves in many overlapping ways: Open Graph tags, Twitter Cards, JSON-LD, microdata, Dublin Core, classic `<meta>` tags, feed links, and plain visible markup. Few pages use all of them consistently, and fewer still use them correctly.

pismo reads all of these sources, reconciles conflicts, and falls back to content analysis when explicit metadata is missing. You get one consistent object instead of writing a dozen special cases.

Design goals:

- **Predictable output.** The same fields are always present, and missing values are `nil`, not surprises.
- **Graceful degradation.** Explicit metadata wins, but heuristics fill the gaps.
- **No network assumptions.** Parse documents you already have, or let pismo fetch them.
- **Small footprint.** Minimal dependencies and no headless browser.

## Installation

Add pismo to your Gemfile:

```ruby
gem "pismo"
```

Then run:

```sh
bundle install
```

Or install it directly:

```sh
gem install pismo
```

pismo supports Ruby 3.0 and newer.

## Quick start

```ruby
require "pismo"

doc = Pismo::Document.new("https://example.com/articles/hello-world")

doc.title         # => "Hello, World"
doc.author        # => "Ada Example"
doc.published_at  # => 2025-03-14 09:30:00 UTC
doc.lede          # => "A short opening paragraph..."
doc.body          # => "Full article text, with boilerplate removed..."
doc.image         # => "https://example.com/img/hello.jpg"
doc.language      # => "en"
```

## What gets extracted

| Field          | Description                                              | Primary sources                                   |
| -------------- | -------------------------------------------------------- | ------------------------------------------------- |
| `title`        | Cleaned page or article title                            | `og:title`, JSON-LD `headline`, `<title>`, `<h1>` |
| `author`       | Byline or author name(s)                                 | JSON-LD, `meta[name=author]`, `rel=author`        |
| `published_at` | Original publication time                                | `article:published_time`, JSON-LD, `<time>`       |
| `modified_at`  | Last modification time                                   | `article:modified_time`, JSON-LD                  |
| `description`  | Summary supplied by the page                             | `og:description`, `meta[name=description]`        |
| `lede`         | First meaningful paragraph of the body                   | Content analysis                                  |
| `body`         | Main text with navigation, ads, and footers removed      | Content analysis                                  |
| `image`        | Best representative image, as an absolute URL            | `og:image`, `twitter:image`, JSON-LD              |
| `keywords`     | Declared and inferred keywords                           | `meta[name=keywords]`, term frequency             |
| `language`     | BCP 47 language tag                                      | `<html lang>`, `og:locale`, detection             |
| `canonical`    | Canonical URL                                            | `link[rel=canonical]`, `og:url`                   |
| `feeds`        | RSS and Atom feed URLs                                   | `link[rel=alternate]`                             |
| `favicon`      | Site icon URL                                            | `link[rel=icon]`                                  |
| `site_name`    | Name of the publishing site                              | `og:site_name`, JSON-LD publisher                 |

Every field has a matching entry in `doc.to_h`, and each can report where its value came from. See [Provenance](#provenance).

## Usage

### From a URL

```ruby
doc = Pismo::Document.new("https://example.com/post")
```

### From a file

```ruby
doc = Pismo::Document.new(File.read("page.html"), url: "https://example.com/post")
```

Passing `url:` lets pismo resolve relative links and images into absolute URLs.

### From a string

```ruby
html = "<html><head><title>Test</title></head><body><p>Hi.</p></body></html>"
doc  = Pismo::Document.new(html)
doc.title # => "Test"
```

### As a hash or JSON

```ruby
doc.to_h
# => { title: "Hello, World", author: "Ada Example", ... }

doc.to_json
```

### Provenance

If you need to know why a value was chosen, ask:

```ruby
doc.source_for(:title)  # => :open_graph
doc.source_for(:body)   # => :content_analysis
```

This is useful for debugging extraction or assigning confidence scores downstream.

## Configuration

Options are passed as keyword arguments:

```ruby
Pismo::Document.new(
  url,
  timeout:      10,
  user_agent:   "my-crawler/1.0",
  max_bytes:    5_000_000,
  follow_redirects: 5,
  prefer:       :structured   # or :heuristic
)
```

| Option             | Default            | Description                                                   |
| ------------------ | ------------------ | ------------------------------------------------------------- |
| `timeout`          | `10`               | Seconds to wait for a response                                |
| `user_agent`       | `pismo/<version>`  | User-Agent header sent when fetching                          |
| `max_bytes`        | `5_000_000`        | Stop reading responses larger than this                       |
| `follow_redirects` | `5`                | Maximum redirects to follow                                   |
| `prefer`           | `:structured`      | Whether explicit metadata or content analysis wins conflicts  |

Set a descriptive `user_agent` when crawling, and respect each site's `robots.txt` and terms of use. pismo does not enforce either for you.

## Command-line interface

pismo ships with a small CLI for quick inspection:

```sh
pismo https://example.com/post
pismo --format json https://example.com/post
pismo --field title --field author page.html
cat page.html | pismo --url https://example.com/post -
```

Exit codes: `0` on success, `1` on fetch errors, `2` on parse errors.

## How it works

1. **Fetch.** If given a URL, pismo downloads the document with size and time limits, then detects the character encoding.
2. **Parse.** The HTML is parsed into a tolerant DOM that survives unclosed tags and invalid nesting.
3. **Collect structured data.** Open Graph, Twitter Cards, JSON-LD, microdata, Dublin Core, and standard meta tags are gathered into a normalized set of candidates.
4. **Analyze content.** Text blocks are scored by length, link density, tag semantics, and position. High-scoring adjacent blocks form the article body, and everything else is treated as boilerplate.
5. **Reconcile.** Candidates for each field are ranked, cleaned (for example, stripping `" | Site Name"` suffixes from titles), and the best one is returned.

## Limitations

- pismo does not execute JavaScript. Pages that render content client-side may return little or no body text unless you supply pre-rendered HTML.
- Content analysis is heuristic. Forums, product listings, and index pages have no single "main article," so results vary.
- Language detection on very short text is unreliable.
- Paywalled or login-gated content is out of scope.

## Development

```sh
git clone https://github.com/your-org/pismo.git
cd pismo
bundle install
bundle exec rake test
```

Test fixtures live in `test/fixtures/`, grouped by site type. When fixing an extraction bug, add a minimal HTML fixture that reproduces it along with the expected output.

Useful tasks:

- `rake test`: run the full suite
- `rake lint`: run the style checker
- `rake bench`: benchmark extraction on the fixture set

## Contributing

Bug reports and pull requests are welcome. Please:

1. Open an issue describing the problem or proposal first for anything non-trivial.
2. Include a sample page, or a trimmed fixture, that demonstrates the issue.
3. Add tests for new behavior and keep the suite green.
4. Keep changes focused; unrelated refactors belong in separate pull requests.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
