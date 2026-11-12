# httpu

**The terminal-first http client**

httpu brings HTTP requests into the place where you already work: your terminal. Send a quick request, inspect a response, and keep moving without opening another application. From checking a local endpoint to exploring an unfamiliar API, httpu keeps the conversation between you and your server readable.

The goal is simple: make everyday HTTP work feel natural on the command line, with clear commands, useful output, and room to grow into scripts.

> This README describes the intended command-line experience. Installation instructions and available options should be verified against the current release.

## Why httpu?

Working with HTTP should not require a workspace full of tabs. Sometimes you only need to check a status code, send a JSON payload, or understand why an endpoint returned something unexpected.

httpu is built around those moments. Requests should be easy to compose, responses should be easy to inspect, and commands should be easy to share with a teammate.

A terminal-first client also fits naturally alongside your existing tools. Keep request examples in documentation, revisit commands through shell history, and connect responses to other programs when you need more control.

## Installation

Install httpu using the distribution method provided by the project’s releases. Package names, supported platforms, and installation commands will be documented as distributions become available.

Once installed, confirm that the executable is on your path:

```sh
httpu --version
```

For a summary of available commands and options:

```sh
httpu --help
```

## Your first request

Start with a URL:

```sh
httpu https://api.example.com/health
```

The simplest request should be the easiest one to write. When you need a specific HTTP method, make it explicit:

```sh
httpu GET https://api.example.com/users
```

Use a local address when developing or debugging a service:

```sh
httpu GET http://localhost:3000/health
```

These examples illustrate the intended interface; consult the installed version’s help output for supported syntax.

## Common workflows

### Send request headers

Headers let you specify the representation you want or provide information required by an endpoint:

```sh
httpu GET https://api.example.com/users \
  -H 'Accept: application/json'
```

Keep examples focused on the headers that matter so they remain easy to read and reproduce.

### Submit JSON

Use an explicit content type when sending a JSON body:

```sh
httpu POST https://api.example.com/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Ada","role":"developer"}'
```

For larger payloads, keep the source data in a file and use the file-input mechanism supported by your version. This makes request bodies easier to edit, review, and reuse.

### Work with authenticated endpoints

Provide authorization through the mechanism your API expects. For bearer authentication, that usually means an `Authorization` header.

Avoid putting real credentials in committed examples. Prefer environment variables or your existing secret-management workflow, and remember that expanded arguments may be visible to local process inspection.

### Use your shell

A terminal client becomes more useful when it works predictably with other tools. Where supported, select body-only output before piping a JSON response into a processor such as `jq`.

Check output and exit-status options before relying on a command in automation. An HTTP error response and a connection failure represent different problems and may need different handling.

## Design principles

- **Readable by default.** Make the important parts of a request and response easy to find.
- **Explicit when necessary.** Let users control methods, headers, bodies, and output without hiding what gets sent.
- **Comfortable in the terminal.** Respect shell workflows and keep common tasks concise.
- **Useful beyond the first request.** Support repeatable work without making simple interactions complicated.

## Contributing

Bug reports, documentation improvements, and focused contributions are welcome.

When reporting a problem, include your httpu version, operating system, a minimal command that reproduces the issue, and the behavior you expected. Remove credentials and private data before sharing output.

For larger changes, open an issue first to discuss the problem and proposed approach.

## Project status

httpu is taking shape. Until release documentation establishes the supported interface, treat the examples above as a guide to the project’s direction rather than a compatibility guarantee.
