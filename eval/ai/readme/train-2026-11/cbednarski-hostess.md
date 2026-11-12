# hostess

An idempotent command-line utility for managing your `/etc/hosts` file.

## Why hostess?

Editing `/etc/hosts` by hand is error-prone. Duplicate entries pile up, typos break name resolution, and scripts that append lines blindly leave the file messier on every run. **hostess** gives you a small set of predictable commands that always produce the same result, no matter how many times you run them. Add a host twice and you still get one entry. Remove a host that isn't there and nothing breaks.

This makes hostess a good fit for provisioning scripts, local development setups, and CI environments where repeatability matters.

## Installation

Download a prebuilt binary from the releases page and place it somewhere on your `PATH`, or build from source:

```sh
git clone https://github.com/your-org/hostess.git
cd hostess
make install
```

## Usage

Most commands modify a system file, so they usually require elevated privileges:

```sh
sudo hostess add local.dev 127.0.0.1
sudo hostess rm local.dev
hostess has local.dev
hostess ls
```

### Commands

| Command              | Description                                          |
|----------------------|------------------------------------------------------|
| `add <host> <ip>`    | Add or update an entry for a hostname                |
| `rm <host>`          | Remove all entries for a hostname                    |
| `on <host>`          | Enable a previously disabled entry                   |
| `off <host>`         | Disable an entry by commenting it out                |
| `has <host>`         | Exit with status 0 if the host exists, 1 otherwise   |
| `ls`                 | List all entries                                     |
| `fmt`                | Normalize formatting and remove duplicates           |
| `dump`               | Print entries as JSON                                |
| `apply <file>`       | Import entries from a JSON file                      |

### Options

- `-f`, `--force` — overwrite conflicting entries without prompting
- `-q`, `--quiet` — suppress non-error output
- `-n`, `--dry-run` — show the resulting file without writing it

## Configuration

By default hostess operates on `/etc/hosts` (or `C:\Windows\System32\drivers\etc\hosts` on Windows). Override the target with the `HOSTESS_PATH` environment variable:

```sh
HOSTESS_PATH=./test-hosts hostess ls
```

## Safety

Before writing, hostess validates every entry and writes to a temporary file that is atomically moved into place. Comments and unrelated lines are preserved, so hostess plays nicely with entries managed by other tools.

## Contributing

Bug reports and pull requests are welcome. Please run the test suite with `make test` before submitting changes.

## License

MIT
