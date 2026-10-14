# Python Ticket Summary Verification Map

This directory contains the maintained feature verification map for the Python Ticket Summary CLI tool (`python-ticket-summary/ticket_summary.py`). Read this index before driving the application, then use the corresponding feature file as the execution recipe.

## Baseline Preconditions

- Python 3.10 or higher installed and accessible on `PATH`.
- No third-party Python runtime packages required (uses only standard library: `csv`, `datetime`, `argparse`, `sys`, `pathlib`).
- Working directory is the repository root or `python-ticket-summary/`.
- Entry point exists at `python-ticket-summary/ticket_summary.py`.
- Run doctor check `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py doctor` and require `overall_status: PASS`.
- Store all generated proof artifacts in `artifacts/verify-ticket-summary/`.

## Driving Conventions

- Treat all commands as literal. Keep argument flags and quotation unchanged.
- Drive standard CLI interactions with `python python-ticket-summary/ticket_summary.py <file> [flags]`.
- Drive automated programmatic runs with `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature <feature-name>`.
- Use isolated temporary directories for synthetic test CSV files.
- Never delete proof evidence files during scratch file cleanup.

## Proof and Skip Reporting

- Capture exit code (`0` for success, `1` for fatal errors), `stdout`, and `stderr`.
- CLI summary table proof requires verifying exact header sections, category totals, and formatted durations.
- Row-level warning proof requires inspecting `stderr` for targeted warnings while confirming valid rows process to `stdout`.
- JSON mode proof requires parsing `stdout` with a standard JSON parser to verify top-level keys and nested metric payloads.
- Record feature execution status in `artifacts/verify-ticket-summary/run_summary.json`.

## Feature Entry Contract

Each feature specification uses four standard sections in this exact order:

1. `Sub-features`: Bulleted list of short identifiers and behavioral descriptions.
2. `How to get to it (user POV)`: User entry points and invocation flags.
3. `Driving it with python ticket_summary.py`: Exact commands, input data, and observable outcomes.
4. `Gotchas`: Known traps and edge cases that invalidate or break verification.

## Features

- [Category Counts and Sorting](./category-counts-and-sorting.md) covers category grouping, whitespace trimming, and alphabetical sorting.
- [Average Resolution Time](./average-resolution-time.md) covers ISO-8601 parsing, duration calculations, overall/category averages, and N/A fallbacks.
- [Row Validation and Warnings](./row-validation-and-warnings.md) covers schema enforcement, row warnings on stderr, and continuous processing of valid rows.
- [Skipped Tickets Tracking](./skipped-tickets-tracking.md) covers identification and reporting of unresolved, corrupted, or inverted timestamps.
- [JSON Output Mode](./json-output-mode.md) covers the `--json` flag, JSON payload schema integrity, and stream separation.
- [Excel Data Anomalies](./excel-data-anomalies.md) covers slash dates, impossible dates, casing variance (Billing * 3), compound comma categories, extra columns, and escalate statuses.
