# FlowCLI

[![CI](https://github.com/FarexEclipsee/flowcli/actions/workflows/ci.yml/badge.svg)](https://github.com/FarexEclipsee/flowcli/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A git-aware task and time-tracking CLI built for developers who live in the
terminal. Track what you're working on, how long it takes, and which branch
it happened on — then export a report in the format you need.

```
$ flow task add "Fix login race condition" --tag bug
Added task #1: Fix login race condition (project: flowcli)

$ flow timer start 1
Started session #1 on task #1: Fix login race condition

$ flow timer stop --note "root cause found, patch pending review"
Stopped session #1 on task #1 (Fix login race condition) (42m 10s)

$ flow report --format markdown
| Task                        | Project | Branch | Started             | Duration |
|-----------------------------|---------|--------|----------------------|----------|
| Fix login race condition    | flowcli | main   | 2026-07-17 09:12     | 42m 10s  |

**Total tracked time:** 42m 10s
```

## Features

- **Task management** — add, list, complete, and remove tasks with projects and tags.
- **Time tracking** — start/stop a single active session, with automatic duration calculation.
- **Git-aware** — auto-detects the current repo name and branch and tags tasks/sessions with them.
- **Pluggable exporters** — built-in CSV, JSON, and Markdown reports; third-party packages can
  register new formats via a `flowcli.exporters` entry point, no core code changes required.
- **Local-first** — everything lives in a single SQLite file at `~/.flowcli/flowcli.db`.
- **Rich terminal output** — colorized tables and status messages via [Rich](https://github.com/Textualize/rich).
- **Fully tested** — pytest suite covering the database layer, every command, and every exporter.

## Installation

```bash
pip install flowcli
```

Or, from source:

```bash
git clone https://github.com/FarexEclipsee/flowcli.git
cd flowcli
pip install -e ".[dev]"
```

## Usage

### Tasks

```bash
flow task add "Refactor auth module" --project backend --tag refactor
flow task list                 # open tasks (default)
flow task list --status all    # everything
flow task list --project backend
flow task done 3
flow task rm 3
```

### Time tracking

```bash
flow timer start 1
flow timer status
flow timer stop --note "context on what got done"
```

Only one session can run at a time — `flow timer status` always tells you
what's active.

### Reports

```bash
flow report                                   # markdown to stdout
flow report --format csv --output report.csv
flow report --format json --since 2026-07-01
flow report --project backend
```

## Writing a custom exporter

Third-party packages can add new report formats without touching FlowCLI's
source. Implement the `Exporter` interface and register it as an entry point:

```python
# my_plugin/html_exporter.py
from flowcli.exporters.base import Exporter

class HtmlExporter(Exporter):
    name = "html"

    def export(self, sessions):
        rows = "".join(f"<tr><td>{s['description']}</td></tr>" for s in sessions)
        return f"<table>{rows}</table>"
```

```toml
# my_plugin's pyproject.toml
[project.entry-points."flowcli.exporters"]
html = "my_plugin.html_exporter:HtmlExporter"
```

Once installed alongside FlowCLI, `flow report --format html` picks it up
automatically.

## Configuration

FlowCLI stores its config at `~/.flowcli/config.yaml`:

```yaml
db_path: /home/you/.flowcli/flowcli.db
default_project: null
date_format: "%Y-%m-%d %H:%M"
```

Set `FLOWCLI_HOME` to relocate the config/database directory (used
internally by the test suite for isolation).

## Development

```bash
pip install -e ".[dev]"
pytest --cov=flowcli
ruff check src tests
black src tests
```

CI runs the same checks (lint, format check, tests) across Python 3.9–3.12
on every push and pull request.

## Project layout

```
src/flowcli/
├── cli.py            # top-level click group, wires everything together
├── config.py          # YAML config loading
├── db.py               # SQLite persistence
├── git_utils.py        # git branch/repo detection
├── models.py            # duration formatting helpers
├── commands/
│   ├── task.py
│   ├── timer.py
│   └── report.py
└── exporters/
    ├── base.py
    ├── csv_exporter.py
    ├── json_exporter.py
    └── markdown_exporter.py
tests/
```

## License

MIT — see [LICENSE](LICENSE).
