# Skipped Tickets Tracking

Skipped Tickets Tracking identifies tickets that cannot be factored into resolution duration metrics, groups them by reason, and presents them in a dedicated section on `stdout`.

## Sub-features

- `skip-missing-date`: Tracks tickets with empty `resolved_at` (open or in progress) under `Unresolved / Missing resolution date`.
- `skip-non-resolved-status`: Tracks tickets with a resolution date but whose status is neither `resolved` nor `closed` under `Unresolved / Non-resolved status`.
- `skip-inverted-chronology`: Identifies tickets where `resolved_at < created_at`, logs `Warning: <ticket_id>: Resolved date earlier than created date.` to `stderr`, and groups under `Resolved before created`.
- `skip-invalid-resolved-date`: Identifies unparseable `resolved_at` strings, logs `Warning: <ticket_id>: Invalid resolved_at timestamp.` to `stderr`, and groups under `Invalid resolution date`.
- `skip-category-integrity`: Confirms skipped tickets still count towards category volume if their row was otherwise structurally valid.

## How to get to it (user POV)

- Run `python ticket_summary.py <path-to-csv>` from the terminal.
- Locate the `Skipped Tickets (Resolution Time):` section at the bottom of the stdout summary.

## Driving it with python ticket_summary.py

Preconditions:
- Test CSV contains tickets covering each of the skipped reasons:
  - T-100: Valid resolved ticket (2 hours).
  - T-101: `resolved_at` is empty, status `open`.
  - T-102: `resolved_at` is earlier than `created_at` (e.g. created Jan 2, resolved Jan 1).
  - T-103: `resolved_at` is `corrupted-date`.
  - T-104: `resolved_at` is valid, but status is `in_progress`.

- **Drive Execution.**
  Run `python python-ticket-summary/ticket_summary.py <skipped-csv-file>`.
  Exit code is `0`.
- **Verify stderr Warnings.**
  `stderr` contains:
  ```text
  Warning: T-102: Resolved date earlier than created date.
  Warning: T-103: Invalid resolved_at timestamp.
  ```
- **Verify stdout Skipped Section.**
  `stdout` contains:
  ```text
  Skipped Tickets (Resolution Time):
    Unresolved / Missing resolution date: T-101
    Unresolved / Non-resolved status: T-104
    Resolved before created: T-102
    Invalid resolution date: T-103
  ```
- **Verify Category Count Retention.**
  All 5 valid rows are counted in their category tally: `DevOps: 5`.
- **Verify Duration Isolation.**
  Only T-100 is used in resolution averages: `0 days, 2 hours, 0 minutes (2.00 hours)`.
- **Proof Artifact.** Run `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature skipped-tickets`.
  Exit code is `0`. Inspect `artifacts/verify-ticket-summary/run_summary.json` to verify `skipped_tickets_tracking` reports `PASS`.

## Gotchas

- Case sensitivity on status: Only `resolved` and `closed` (case-insensitive) are accepted as resolved states. Any other status (`open`, `in_progress`, `escalated`) must be treated as non-resolved.
- Chronology checks: A negative duration (`resolved_at < created_at`) must never be added to duration calculations or it will artificially lower the average.
