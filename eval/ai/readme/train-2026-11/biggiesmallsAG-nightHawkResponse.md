# nightHawkResponse

**Incident Response Forensic Framework**

nightHawkResponse is a framework for collecting, preserving, and analyzing forensic evidence during security incidents. It is built for incident responders, SOC analysts, and forensic examiners who need a repeatable way to triage systems, capture volatile data, and reconstruct what happened, without relying on ad hoc scripts that are hard to audit later.

The framework focuses on three goals:

1. **Preserve evidence.** Collect artifacts in a way that maintains integrity, records chain of custody, and minimizes changes to the target system.
2. **Speed up triage.** Give responders a fast first look at a host so they can decide what to escalate, isolate, or image.
3. **Make analysis reproducible.** Every collection and analysis step is logged, so another examiner can verify the results.

> **Scope and authorization:** nightHawkResponse is intended for defensive use: investigating incidents on systems you own or are authorized to examine. Do not run it against systems without permission. Collected data may contain sensitive personal information, credentials, or regulated data, so handle outputs according to your organization's policies and applicable law.

---

## Features

- **Live response collection.** Captures volatile data such as running processes, network connections, loaded modules, logged-in users, and scheduled tasks.
- **Artifact acquisition.** Gathers common forensic artifacts, including event logs, registry hives, prefetch and shimcache data, browser history, persistence mechanisms, and recently modified files.
- **Integrity verification.** Computes cryptographic hashes for every collected artifact and writes them to a signed manifest at collection time.
- **Chain-of-custody logging.** Records who ran each collection, when, from which host, and with which framework version.
- **Modular analysis.** Plugins parse raw artifacts into structured output, such as timelines, process trees, and persistence reports.
- **Timeline generation.** Merges timestamps from multiple artifact sources into a single chronological view.
- **Indicator matching.** Checks hashes, file names, IP addresses, domains, and registry keys against user-supplied indicator lists.
- **Report export.** Produces findings in Markdown, HTML, and JSON for handoff to case management systems or legal review.
- **Minimal footprint.** Prefers read-only APIs and avoids installing software on the target where possible.

---

## Architecture

nightHawkResponse is organized into four layers:

| Layer | Purpose |
|---|---|
| **Collectors** | Platform-specific modules that read volatile state and artifacts from the target host. |
| **Acquisition engine** | Handles hashing, manifest creation, compression, and optional encryption of collected data. |
| **Analyzers** | Plugins that parse collected artifacts and produce structured records. |
| **Reporting** | Converts analyzer output into human-readable and machine-readable reports. |

Collectors and analyzers are separated on purpose. You can collect evidence on a host that has no analysis tooling, copy the bundle to an analysis workstation, and run analyzers there. This keeps the target's footprint small and lets analysis happen on a clean system.

```
nightHawkResponse/
├── collectors/       # Platform collectors (Windows, Linux, macOS)
├── acquisition/      # Hashing, manifests, packaging
├── analyzers/        # Artifact parsers and timeline builders
├── reporting/        # Report templates and exporters
├── indicators/       # Sample indicator lists (IOCs)
├── docs/             # Extended documentation
└── tests/            # Unit and fixture-based tests
```

---

## Requirements

- Python 3.10 or later
- Administrative or root privileges for full collection (some artifacts require elevated access)
- Sufficient free disk space for the collection bundle, which can range from a few hundred megabytes to several gigabytes depending on scope
- For analysis: a workstation with enough memory to load large artifact sets

Supported platforms:

- **Windows** 10 and 11, Windows Server 2016 and later
- **Linux** distributions with systemd or common init systems
- **macOS** 12 and later (collector support may be more limited than Windows and Linux; see `docs/platform-support.md`)

---

## Installation

Clone the repository and install in a virtual environment:

```bash
git clone <repository-url> nightHawkResponse
cd nightHawkResponse
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Install the package:

```bash
pip install -e .
```

Verify the installation:

```bash
nhr --version
```

---

## Quick Start

### 1. Collect evidence on a target host

Run from an elevated shell on the system under investigation:

```bash
nhr collect --profile standard --output /path/to/evidence/HOST01
```

Available profiles:

| Profile | What it collects | Typical use |
|---|---|---|
| `triage` | Volatile data and key persistence locations | First look during an active incident |
| `standard` | Triage plus event logs, registry, and common artifacts | Most investigations |
| `full` | Everything in `standard` plus file system metadata and extended artifacts | Deep-dive or legal-hold collection |

Each run produces a case directory containing:

- `manifest.json`: file list with SHA-256 hashes and timestamps
- `manifest.sig`: signature over the manifest (if signing is configured)
- `custody.log`: who ran the collection, from where, and when
- `artifacts/`: collected data, organized by category

### 2. Verify the evidence bundle

Before analysis, confirm that nothing has changed since collection:

```bash
nhr verify --case /path/to/evidence/HOST01
```

A verification failure means at least one artifact no longer matches its recorded hash. Do not proceed with analysis until you have determined why.

### 3. Analyze the bundle

```bash
nhr analyze --case /path/to/evidence/HOST01 --analyzers all
```

To run only specific analyzers:

```bash
nhr analyze --case /path/to/evidence/HOST01 --analyzers timeline,persistence,network
```

### 4. Check against indicators

```bash
nhr match --case /path/to/evidence/HOST01 --indicators indicators/sample-iocs.csv
```

Indicator files are CSV or JSON with one indicator per row. Supported types include SHA-256 hashes, file names, IPv4 and IPv6 addresses, domains, and registry key paths.

### 5. Generate a report

```bash
nhr report --case /path/to/evidence/HOST01 --format html --output report.html
```

Supported formats: `md`, `html`, `json`.

---

## Configuration

Settings are read from `nhr.toml` in the working directory, or from a path given with `--config`:

```toml
[case]
examiner = "analyst-id"
case_id = "IR-2026-0042"

[collection]
profile = "standard"
exclude_paths = ["C:\\Users\\*\\AppData\\Local\\Temp\\large-cache"]
max_file_size_mb = 500

[integrity]
hash_algorithm = "sha256"
sign_manifest = true
signing_key = "/secure/keys/examiner.pem"

[analysis]
timezone = "UTC"
```

Credentials and signing keys should never be committed to version control. Store key files outside the repository and reference them by path.

---

## Chain of Custody and Integrity

Forensic credibility depends on demonstrating that evidence has not been altered. nightHawkResponse supports this in the following ways:

- Every artifact is hashed at the moment of collection, before any analysis runs.
- The manifest records the framework version, the examiner identifier, and the host identity.
- `custody.log` is append-only. Each action, including verification, analysis, and export, adds an entry.
- Analysis never writes to the original artifacts. Parsed output goes to a separate `analysis/` directory.

These features support good practice but do not replace your organization's procedures. Consult your legal and compliance teams about requirements for evidence handling in your jurisdiction.

---

## Extending the Framework

### Writing a collector

Collectors subclass `BaseCollector` and implement `collect(context)`, which yields `Artifact` objects:

```python
from nhr.collectors.base import BaseCollector, Artifact

class ScheduledTasksCollector(BaseCollector):
    name = "scheduled_tasks"
    platforms = ["windows"]

    def collect(self, context):
        for task_file in context.glob(r"C:\Windows\System32\Tasks\**\*"):
            yield Artifact(
                category="persistence",
                source=task_file,
                copy=True,
            )
```

### Writing an analyzer

Analyzers subclass `BaseAnalyzer` and implement `analyze(case)`, which returns a list of `Finding` records. Each finding should include a timestamp, a source artifact reference, and a short description. This keeps results traceable to their evidence.

Place new modules in the matching directory and register them in `plugins.toml`. Run `nhr plugins list` to confirm they load.

---

## Development

Install development dependencies and run the test suite:

```bash
pip install -e ".[dev]"
pytest
```

Tests use synthetic fixtures under `tests/fixtures/`. Do not add real evidence, real credentials, or real indicators from active investigations to the repository. Use sanitized or generated data.

Style and linting:

```bash
ruff check .
mypy nhr
```

Contributions are welcome. Please open an issue before starting large changes, and include tests with new collectors or analyzers.

---

## Limitations

- Live response on a compromised host carries risk. Attackers may detect collection activity, and some tools can alter timestamps or artifacts. Treat live data as a snapshot, not a complete record.
- Memory acquisition is not included in the core framework. Use a dedicated memory acquisition tool and ingest its output as an external artifact.
- Some artifacts require parsing libraries that are optional and must be installed separately.
- Analyzers reflect the parsing logic available at the time of release. Verify important findings with a second tool before acting on them.

---

## Documentation

- `docs/platform-support.md`: per-platform collector coverage
- `docs/manifest-format.md`: manifest and custody log schemas
- `docs/analyzer-reference.md`: list of analyzers and their outputs
- `docs/case-workflow.md`: recommended investigation workflow

---

## Contributing and Security

Report security vulnerabilities in nightHawkResponse privately rather than in public issues. See `SECURITY.md` for contact details.

---

## License

Released under the license specified in the `LICENSE` file at the root of the repository.

---

*nightHawkResponse: collect carefully, verify everything, and document each step.*

---

**Notes on what I wrote:** I worked from the project name and tagline only. I didn't have access to the codebase, so the commands, directory layout, config keys, profiles, and plugin API are illustrative placeholders. Before publishing, check them against the real implementation, and fill in the repository URL, supported platforms, and license. If you share the source or existing docs, I can make the README match the code exactly.
