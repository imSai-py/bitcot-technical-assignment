# Row Validation and Warnings

Row Validation inspects each CSV record for schema conformance and logs diagnostic warnings to `stderr` for malformed records while allowing all valid records to complete processing.

## Sub-features

- `val-missing-ticket-id`: Flags rows lacking a `ticket_id` with `Warning: Row <row_idx>: Missing ticket_id.` on `stderr`.
- `val-missing-required-fields`: Flags rows lacking `category`, `priority`, or `status` with `Warning: <ticket_id>: Missing <field>.` on `stderr`.
- `val-invalid-created-at`: Flags unparseable or missing `created_at` timestamps with `Warning: <ticket_id>: Invalid or missing created_at.` on `stderr`.
- `val-resilience`: Guarantees processing continues for valid records despite malformed rows.
- `val-fatal-rejection`: Aborts with exit code `1` and error message on `stderr` when file is missing, is a directory, is empty, or lacks required headers.

## How to get to it (user POV)

- Run `python ticket_summary.py <path-to-csv>` from the terminal.
- Observe diagnostic warnings printed to the terminal's standard error stream (`stderr`).

## Driving it with python ticket_summary.py

Preconditions:
- Test CSV contains a mixture of malformed rows and valid rows.

- **Missing ticket_id Detection.**
  Row 2 in CSV contains empty `ticket_id` field: `,2026-01-01 10:00:00,2026-01-01 11:00:00,Billing,low,resolved`.
  Run `python python-ticket-summary/ticket_summary.py <csv-file>`.
  `stderr` contains `Warning: Row 2: Missing ticket_id.`
- **Missing Required Attributes.**
  Ticket `T-98` is missing `category`, `T-97` is missing `priority`, and `T-96` is missing `status`.
  Run `python python-ticket-summary/ticket_summary.py <csv-file>`.
  `stderr` contains:
  ```text
  Warning: T-98: Missing category.
  Warning: T-97: Missing priority.
  Warning: T-96: Missing status.
  ```
- **Invalid Timestamp.**
  Ticket `T-99` contains invalid string `corrupted-date` in `created_at`.
  Run `python python-ticket-summary/ticket_summary.py <csv-file>`.
  `stderr` contains:
  ```text
  Warning: T-99: Invalid or missing created_at.
  ```
- **Continuous Processing of Valid Rows.**
  Ensure valid row `T-1` in category `Billing` is included in the output summary on `stdout`.
  `stdout` contains `Billing: 1`. Exit code is `0`.
- **Proof Artifact.** Run `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature row-validation`.
  Exit code is `0`. Check `artifacts/verify-ticket-summary/run_summary.json` to verify `row_validation_and_warnings` reports `PASS`.

## Gotchas

- Standard streams separation: Row warnings MUST go strictly to `stderr`. Never let warnings pollute `stdout`, which breaks JSON piping.
- Row indices: Row numbering is 1-indexed based on CSV line numbers (Header = Row 1; First data row = Row 2).
