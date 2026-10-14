---
name: verify-ticket-summary
description: Verify the Python Ticket Summary CLI tool. Use to validate CSV parsing, schema checks, row warnings, skipped ticket tracking, resolution metrics, and JSON output against regressions.
---

# Verify Python Ticket Summary CLI

Use this skill to verify the behavior and schema compliance of the Python Ticket Summary CLI tool (`python-ticket-summary/ticket_summary.py`). It exercises the tool through real command line invocations, tests edge cases and error handling, and records persistent evidence.

## Launch

The application is a short-lived Python CLI utility. There is no background daemon or persistent server port to maintain.

1. **Prerequisites & Dependencies**:
   - Python 3.10 or higher.
   - Standard library only (`csv`, `datetime`, `argparse`, `sys`, `pathlib`).
   - No external package installations are needed.

2. **Launch Command**:
   ```bash
   python python-ticket-summary/ticket_summary.py <path-to-csv> [--json]
   ```
   Or within the subproject directory:
   ```bash
   cd python-ticket-summary
   python ticket_summary.py tickets.csv
   ```

3. **Readiness**:
   - The CLI executes synchronously and exits with code `0` on successful summary output or code `1` on fatal input failure.
   - Readiness is immediate upon invoking Python with the script path.

4. **Teardown**:
   - Processes terminate naturally upon completion. No lingering background processes exist.

## Doctor

Before running extensive verification runs, execute this read-only health check to ensure the tool runtime and source files are valid:

```bash
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py doctor
```

Manual equivalent steps:
1. Confirm Python version:
   ```bash
   python --version
   ```
   *Requirement*: Python 3.10.0 or higher.
2. Confirm entrypoint file exists and compiles:
   ```bash
   python -m py_compile python-ticket-summary/ticket_summary.py
   ```
   *Requirement*: Exit code `0` with zero syntax errors.
3. Confirm help documentation renders:
   ```bash
   python python-ticket-summary/ticket_summary.py --help
   ```
   *Requirement*: Exit code `0`, usage string on `stdout`.

If any doctor check fails, do not proceed with feature testing until the environment or syntax defect is corrected.

## Drive

Drive the application using the feature map in [features/README.md](./features/README.md).

### 1. Automated Test Drive Harness
Run all feature verifications and capture structured evidence in a single command:
```bash
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py all
```

To drive an individual feature:
```bash
# Category counts and sorting
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature category-counts

# Average resolution time calculations
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature resolution-time

# Row validation and stderr warnings
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature row-validation

# Skipped tickets categorization
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature skipped-tickets

# JSON output mode
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature json-mode

# Fatal input handling
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature fatal-input

# Default dataset verification
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature real-dataset

# Excel data anomalies verification (dates, billing casing * 3, compound categories, extra columns, escalate)
python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature excel-anomalies
```

### 2. Manual CLI Recipes

- **Baseline Run against Sample Dataset**:
  ```bash
  python python-ticket-summary/ticket_summary.py python-ticket-summary/tickets.csv
  ```
  *Observable Result*: Exit code `0`. Prints category counts, overall average resolution time, and skipped tickets section. Warnings for known data anomalies appear on `stderr`.

- **Structured JSON Mode**:
  ```bash
  python python-ticket-summary/ticket_summary.py python-ticket-summary/tickets.csv --json
  ```
  *Observable Result*: Exit code `0`. Valid JSON is emitted to `stdout`. All row warnings stay isolated to `stderr`.

- **Fatal Input Rejection**:
  ```bash
  python python-ticket-summary/ticket_summary.py nonexistent_tickets.csv
  ```
  *Observable Result*: Exit code `1`. Error message on `stderr`: `Error: File 'nonexistent_tickets.csv' does not exist.`

## Evidence

Verification evidence is persistently stored in `artifacts/verify-ticket-summary/`:

- `doctor_evidence.json`: Records Python version, script existence, syntax compile status, and help flag output.
- `run_summary.json`: Detailed execution record for each driven feature, including:
  - Feature identifier
  - Status (`PASS` or `FAIL`)
  - Exit code
  - Captured `stdout` and `stderr` snippets
  - Granular boolean assertions (e.g., `alphabetical_order`, `row_missing_ticket_id_warned`, `stdout_is_valid_json`)

Proof Standards:
- Must execute the real `ticket_summary.py` script via `python` sub-processes, not mocked functions or internal unit tests.
- Capture action, inputs, exit code, `stdout`, and `stderr`.
- Verify side-effects (e.g. clean JSON stream separation).
- Proof artifacts must survive fixture cleanup.

## Cleanup

Cleanup removes temporary synthetic CSV test files created during test runs.

1. Temporary test CSV files are written into an isolated temporary folder (`ticket_verify_*`).
2. After driving the features, the temporary directory is removed recursively.
3. The evidence artifacts directory (`artifacts/verify-ticket-summary/`) is never modified or removed during cleanup.
4. If driving manually, delete any ad-hoc scratch CSV files created in the workspace.

## Helpers

The skill includes the automated verification harness script:
- Path: [scripts/verify_ticket_summary.py](./scripts/verify_ticket_summary.py)
- Invocations:
  - `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py doctor`
  - `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature <name>`
  - `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py all`
