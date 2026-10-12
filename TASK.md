# Technical Assignment: Consolidated Task Specifications & Notes

This document consolidates all task requirements, specifications, and investigation notes across the three assignment components.

---

## Part 1: Debug Warm-Up Task

### Problem Statement
The function in `debug-warmup/debug_warmup.py` originally produced an incorrect duration calculation when evaluating tickets whose resolution spanned multiple calendar days.

### Notes & Investigation
1. **What was wrong**:
   `_hours_between()` accessed `delta.seconds` instead of `delta.total_seconds()`. In Python's `datetime.timedelta`, `delta.seconds` returns only the seconds remainder modulo 1 day (0 to 86399), discarding full days (`delta.days * 86400`). This caused the function to lose 24 hours for every full calendar day elapsed, incorrectly under-reporting resolution times and missing SLA breaches for multi-day tickets.
2. **How I found it**:
   Traced ticket `B` across calendar days (created `2026-03-01 08:00:00`, resolved `2026-03-02 10:00:00` — 26 elapsed hours) and observed that the original function returned only 2.0 hours.

### Verification
Run tests in `debug-warmup/`:
```bash
cd debug-warmup
python -m pytest tests
```
Output: 6 passing unit tests covering same-day, multi-day (>24h and >48h), and unhandled timestamp cases.

---

## Part 2: Python Ticket Summary CLI Tool

### Requirements
Build a standalone command-line tool (`python-ticket-summary/ticket_summary.py`) using only the Python standard library:
```bash
python ticket_summary.py tickets.csv
```
The tool reads the CSV file and outputs:
- The number of tickets in each category (sorted alphabetically).
- The average resolution time (both overall and per category), formatted as `X days, Y hours, Z minutes (Total.HH hours)`.
- A list of skipped/unresolved tickets.
- Optional JSON output when invoked with `--json`.
- Warning diagnostics to `stderr` for malformed rows while continuing to process valid records.

### CSV Columns
- `ticket_id`: Unique identifier (e.g. `TICK-101`)
- `created_at`: Creation timestamp (ISO-8601)
- `resolved_at`: Resolution timestamp (ISO-8601, optional/empty if open)
- `category`: Ticket category (e.g. `Billing`, `Hardware`, `Software`)
- `priority`: Priority level (`Urgent`, `High`, `Normal`, `Low`)
- `status`: Ticket status (`Open`, `In Progress`, `Resolved`, `Closed`)

### Verification
Run tests in `python-ticket-summary/`:
```bash
cd python-ticket-summary
python -m pytest tests
```
Output: 11 passing integration tests validating CLI arguments, parsing, edge cases, whitespace handling, and JSON output.

---

## Part 3: TypeScript SLA Library

### Requirements
Build a fully typed, standalone TypeScript library (`typescript-sla-library/`) that calculates SLA deadlines and detects SLA breaches.

### Key Capabilities
- **Priority Target Hours**:
  - `urgent`: 4 hours
  - `high`: 8 hours
  - `normal`: 24 hours
  - `low`: 72 hours
  - Supports custom overrides per priority.
- **Breach Detection**:
  - Identifies whether a ticket breached its deadline (`isBreached: boolean`).
  - Reports the exact breach duration in milliseconds (`breachDurationMs: number`).
- **Flexible Timestamps**:
  - Accepts native JavaScript `Date` instances, ISO-8601 strings, and numeric UNIX epoch timestamps.
- **Business Hours Calculation Engine**:
  - Optional mode restricting calculation to Monday through Friday, 09:00 to 18:00.
  - Pauses overnight and across weekends.
  - Accounts for off-hour submissions and optional holiday exclusions.

### Verification
Run tests in `typescript-sla-library/`:
```bash
cd typescript-sla-library
npm test
```
Output: 34 passing tests across unit and scenario suites.
