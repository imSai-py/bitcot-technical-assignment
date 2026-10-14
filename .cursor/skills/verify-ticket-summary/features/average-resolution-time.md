# Average Resolution Time

Average Resolution Time calculates the elapsed resolution duration (`resolved_at - created_at`) for resolved tickets across all categories and broken down per category, formatted in human-readable and decimal formats.

## Sub-features

- `res-overall`: Computes overall arithmetic mean of resolution durations across all resolved tickets.
- `res-category`: Computes arithmetic mean of resolution durations for each specific category.
- `res-formatting`: Formats durations as `X days, Y hours, Z minutes (Total.HH hours)` with correct pluralization (`day`/`days`, `hour`/`hours`, `minute`/`minutes`).
- `res-iso-flexibility`: Parses ISO-8601 timestamps in space-separated (`YYYY-MM-DD HH:MM:SS`), `T`-separated (`YYYY-MM-DDTHH:MM:SS`), UTC (`Z`), or offset forms.
- `res-zero-resolved`: Displays `N/A (No resolved tickets)` instead of dividing by zero when no tickets are resolved.

## How to get to it (user POV)

- Run `python ticket_summary.py <path-to-csv>` from the terminal.
- View the `Average Resolution Time:` line and the per-category `(Avg Resolution: ...)` entries in the stdout summary.

## Driving it with python ticket_summary.py

Preconditions:
- CSV file has valid headers and rows with parseable `created_at` and `resolved_at` timestamps.
- Resolved tickets have status `resolved` or `closed` and `resolved_at >= created_at`.

- **Calculate Overall & Category Averages.**
  Given:
  - T-1: Billing, duration 2.0 hours (2026-01-01 10:00 to 12:00)
  - T-2: Billing, duration 6.0 hours (2026-01-01 10:00 to 16:00) -> Billing mean = 4.0 hours
  - T-3: Hardware, duration 24.0 hours (2026-01-01 10:00 to 2026-01-02 10:00) -> Hardware mean = 24.0 hours
  Total elapsed = 32.0 hours / 3 tickets = 10.6667 hours (0 days, 10 hours, 40 minutes).
  Run `python python-ticket-summary/ticket_summary.py <csv-file>`.
  Exit code is `0`.
  `stdout` contains:
  ```text
  Average Resolution Time: 0 days, 10 hours, 40 minutes (10.67 hours)
  ...
    Billing: 2 (Avg Resolution: 0 days, 4 hours, 0 minutes (4.00 hours))
    Hardware: 1 (Avg Resolution: 1 day, 0 hours, 0 minutes (24.00 hours))
  ```
- **Zero-Resolved Dataset Handling.**
  Provide a CSV containing only tickets with status `open` or `in_progress` and empty `resolved_at`.
  Run `python python-ticket-summary/ticket_summary.py <unresolved-csv-file>`.
  Exit code is `0`.
  `stdout` displays:
  ```text
  Average Resolution Time: N/A (No resolved tickets)
  ```
- **Proof Artifact.** Run `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature resolution-time`.
  Exit code is `0`. Inspect `artifacts/verify-ticket-summary/run_summary.json` to confirm `average_resolution_time` passed all checks.

## Gotchas

- Timezone offsets: If one timestamp has UTC `Z` and another has local offset `+05:30`, they are normalized to UTC datetime before subtracting; ensure duration subtraction respects timezone differences.
- Multi-day calculations: Always verify duration calculation preserves full calendar days (`(resolved_dt - created_dt).total_seconds()`).
