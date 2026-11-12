# webseclab

A set of web security test cases and a toolkit to construct new ones.

webseclab provides small, self-contained web pages that each demonstrate one well-understood vulnerability, plus the tooling to write, serve, and verify your own. Use it to benchmark scanners, train code reviewers, demonstrate attack classes, or regression-test defensive tooling.

> **Warning:** The test cases are intentionally vulnerable. Run them only on localhost or an isolated network. Never deploy them to a public host or next to real data or credentials.

## Why webseclab?

Real applications are noisy. When a scanner misses a bug, it is hard to tell whether the tool failed or the target was too complicated. webseclab isolates each weakness in a minimal page so that results are unambiguous:

- **Known ground truth.** Every case declares whether it is vulnerable, what the vulnerability is, and how to confirm it.
- **Controlled variation.** Related cases differ by one detail, such as the output context, the encoding applied, or the filter in front of the sink. This shows exactly where a tool's detection logic stops working.
- **Easy extension.** Adding a case takes a handler, a template, and a short metadata file.

## Features

- A growing catalog of cases covering cross-site scripting in several HTML, attribute, JavaScript, and URL contexts, plus open redirects, header injection, content-type confusion, and CSRF.
- Matching "safe" variants that apply correct output handling, so you can measure false positives as well as false negatives.
- A small server that exposes every case under a predictable URL.
- A scaffolding tool for generating new cases from a template.
- A test runner that checks each case against its declared expectation.
- Machine-readable metadata, suitable for scoring scanner output.

## Getting started

### Requirements

- Python 3.9 or newer
- `pip` and `venv`
- A modern browser for manual exploration

### Install

```bash
git clone https://github.com/<your-org>/webseclab.git
cd webseclab
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run the lab

```bash
python -m webseclab serve --host 127.0.0.1 --port 8080
```

Open `http://127.0.0.1:8080/` for an index of all cases. The server binds to localhost by default. Change that only if you understand the consequences.

### Run the checks

```bash
python -m webseclab test
```

The runner requests each case with its documented payload and confirms the observed behavior matches the metadata. A failure means either the case is broken or the metadata is wrong.

## Repository layout

```
webseclab/
├── cases/            # One directory per test case
│   └── xss-attr-01/
│       ├── case.toml     # Metadata and expected result
│       ├── handler.py    # Request handling
│       └── page.html     # Template
├── toolkit/          # Server, scaffolding, and runner code
├── docs/             # Background notes per vulnerability class
├── tests/            # Tests for the toolkit itself
└── requirements.txt
```

## Anatomy of a test case

Each case is a directory containing three parts.

**Metadata (`case.toml`)** describes the case:

```toml
id = "xss-attr-01"
title = "Reflected input in unquoted attribute"
category = "xss"
vulnerable = true
payload = "x onmouseover=alert(1)"
expect = "payload appears unescaped inside the attribute"
```

**Handler (`handler.py`)** takes the request and decides what to reflect, store, or redirect. It is deliberately short so the flaw is easy to find.

**Template (`page.html`)** is the markup that carries the sink.

## Writing a new case

Generate a skeleton:

```bash
python -m webseclab new --category xss --name my-case
```

Then:

1. Edit `handler.py` and the template to introduce (or correctly prevent) the behavior you want to test.
2. Fill in `case.toml`, including a payload and a plain-language expectation.
3. Run `python -m webseclab test --case my-case` until it passes.
4. Add a paired safe variant where practical.

Good cases are minimal, change one variable at a time, and have an unambiguous success condition. If you need more than a few dozen lines, consider splitting the case.

## Evaluating scanners

Point a scanner at the running server and compare its findings with the catalog metadata:

```bash
python -m webseclab manifest --format json > expected.json
```

The manifest lists every case, its URL, and whether it is vulnerable. Findings on safe variants are false positives, and misses on vulnerable cases are false negatives.

## Contributing

Contributions are welcome, especially new cases and safe counterparts to existing ones.

- Open an issue before starting large changes.
- Keep each case self-contained, with no external network dependencies.
- Include metadata and make sure `python -m webseclab test` passes.
- Document anything non-obvious in `docs/`.

Please report problems with the toolkit itself (as opposed to the intentional vulnerabilities in the cases) through the issue tracker.

## Responsible use

webseclab is for education, research, and defensive testing. Do not use techniques you learn here against systems you do not own or lack written permission to test.

## License

See `LICENSE` for details.

---

I wrote this as plain text without saving a file, and the repo layout, CLI commands (`serve`, `test`, `new`, `manifest`), and clone URL are placeholders I made up. Tell me the real structure and commands and I'll correct them, or I can write it to `README.md` in the working directory.
