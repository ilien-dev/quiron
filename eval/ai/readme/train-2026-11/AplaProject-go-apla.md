# go-apla

**A blockchain platform with a simplified programming language**

go-apla is a blockchain platform written in Go. It is designed so that building decentralized applications does not require deep expertise in cryptography or distributed systems. It combines a permissioned blockchain network with a compact contract language and a declarative interface layer. Developers write business logic that is easy to read and audit, and ship it to users quickly.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [The Contract Language](#the-contract-language)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running a Network](#running-a-network)
- [API](#api)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Most blockchain platforms ask developers to learn a complex smart-contract language, manage gas economics, and reason about low-level state. go-apla takes a different approach. It offers a small, purpose-built language for contracts, a built-in data model based on tables, and a permission system that governs who can read, write, or change any part of the system.

The platform is organized around **ecosystems**. An ecosystem is a self-contained environment with its own members, roles, contracts, tables, and user interface pages. Ecosystems share the same underlying blockchain, so organizations can run isolated applications while still interacting through well-defined contracts.

## Key Features

- **Simplified contract language**: A concise, C-like syntax with typed variables, built-in functions for working with data, and clear `data`, `conditions`, and `action` sections.
- **Table-based storage**: Contract state lives in relational-style tables. You can query and update them without hand-rolling key-value schemes.
- **Granular permissions**: Every table, column, contract, and page has access rules. Those rules are written in the same language as contracts.
- **Ecosystems**: Multiple independent applications run side by side on one network, each with its own governance.
- **Declarative UI templates**: Interface pages are described in a lightweight template language and rendered by client applications.
- **Proof-of-Authority consensus**: A known set of validating nodes takes turns producing blocks. This gives predictable block times and low resource usage.
- **REST API**: A full HTTP API for authentication, sending transactions, querying data, and fetching interface content.

## Architecture

A go-apla node has these main components:

| Component | Responsibility |
|-----------|----------------|
| **Block generator** | Builds new blocks from pending transactions when it is the node's turn |
| **Block collector** | Downloads and validates blocks produced by other nodes |
| **Transaction queue** | Holds incoming transactions until they are included in a block |
| **Virtual machine** | Compiles and executes contracts in a sandboxed environment |
| **Storage layer** | Persists blocks and ecosystem tables in PostgreSQL |
| **Cache** | Uses Redis or in-memory caching to speed up frequent lookups |
| **API server** | Exposes REST endpoints to clients and other services |

Nodes talk to each other over TCP to exchange blocks and transactions. Clients talk to nodes over HTTP.

## The Contract Language

Each contract is split into three sections. Here is a small example that records a greeting:

```
contract SaveGreeting {
    data {
        Message string
    }

    conditions {
        if Size($Message) == 0 {
            error "Message cannot be empty"
        }
    }

    action {
        DBInsert("greetings", {message: $Message, author: $key_id})
    }
}
```

- **`data`** declares the parameters the contract accepts.
- **`conditions`** validates input and permissions before anything is written.
- **`action`** performs the state changes.

The language includes control flow, maps, arrays, and a standard library. That library covers database access, cryptography, string handling, and calling other contracts. The virtual machine limits execution resources, so a faulty contract cannot stall the network.

## Getting Started

### Prerequisites

- Go (a recent stable release)
- PostgreSQL 10 or newer
- Redis (optional, for caching)
- Git

### Build from Source

```bash
git clone https://github.com/AplaProject/go-apla.git
cd go-apla
go build -o go-apla .
```

This produces a single `go-apla` binary in the project directory.

### Prepare the Database

Create a database and a user for the node:

```sql
CREATE USER apla WITH PASSWORD 'change-me';
CREATE DATABASE apla OWNER apla;
```

### Initialize a Node

Generate a configuration file and the node keys:

```bash
./go-apla config --dataDir=./data --dbName=apla --dbUser=apla --dbPassword=change-me
./go-apla generateKeys
./go-apla generateFirstBlock
./go-apla initDatabase
```

### Start the Node

```bash
./go-apla start
```

By default the API listens on `http://localhost:7079`.

## Configuration

Settings are stored in `config.toml` inside your data directory. The most commonly adjusted options are:

| Setting | Description |
|---------|-------------|
| `DataDir` | Directory for keys, logs, and runtime files |
| `DB.*` | PostgreSQL host, port, name, user, and password |
| `HTTP.Host` / `HTTP.Port` | Address the API server binds to |
| `TCPServer.Host` / `TCPServer.Port` | Address used for node-to-node traffic |
| `NodesAddr` | Addresses of existing nodes to connect to |
| `Log.LogLevel` | Logging verbosity (`DEBUG`, `INFO`, `WARN`, `ERROR`) |

Any option can also be passed as a command-line flag. Run `./go-apla config --help` to see the full list.

## Running a Network

To form a network with multiple validators:

1. Start the first node and generate the first block as shown above.
2. On each additional machine, build go-apla, create a database, and generate keys.
3. Set `NodesAddr` in each new node's configuration so it points at an existing node.
4. Add each new node's public key and address to the validator list through the platform's governance contracts.
5. Start the new nodes. They will sync the chain and join block production once they are approved.

For local development you can run several nodes on one machine. Give each node its own data directory, database, and set of ports.

## API

The REST API lets clients:

- Authenticate with a key pair and receive a session token
- Prepare, sign, and submit contract transactions
- Check transaction status
- Read rows from ecosystem tables
- Fetch and render interface pages and menus
- List contracts, tables, and ecosystem parameters

All responses are JSON. Authenticated endpoints require the token in the `Authorization` header.

## Contributing

Contributions are welcome. To get started:

1. Fork the repository and create a feature branch.
2. Follow standard Go conventions and run `gofmt` before committing.
3. Add or update tests for your changes and make sure `go test ./...` passes.
4. Open a pull request with a clear description of what changed and why.

Please use the issue tracker to report bugs or propose larger changes before you start work on them.

## License

go-apla is released under the MIT License. See the `LICENSE` file for details.
