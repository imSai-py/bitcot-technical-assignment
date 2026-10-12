Status: ready-for-agent

# Specification: Ticket Summary Tool

## Problem Statement

Support managers, engineers, and administrators regularly export ticket data to CSV files. They need to understand ticket distribution across categories and calculate average resolution times. Currently, there is no fast, reliable command-line tool to parse this CSV data, compute accurate resolution metrics, handle data anomalies, and report unresolved or skipped tickets without requiring third-party library installations.

## Solution

A standalone Python command-line utility (`ticket_summary.py`) built exclusively with the Python standard library. The tool accepts a CSV file path, validates ticket rows, computes ticket counts per category and average resolution times (both overall and per category), reports malformed rows to `stderr`, and prints structured results to `stdout`. It provides human-readable text by default and optional structured JSON output.

## User Stories

1. As a support lead, I want to execute `python ticket_summary.py tickets.csv`, so that I can immediately generate ticket summaries without installing external dependencies.
2. As a support lead, I want to see the total number of tickets in each category, so that I can evaluate workload distribution across departments.
3. As a support lead, I want category counts sorted alphabetically, so that I can quickly locate specific categories in the summary table.
4. As an operations manager, I want to see the overall average resolution time across all resolved tickets, so that I can track team efficiency.
5. As an operations manager, I want to see average resolution times broken down per category, so that I can detect bottlenecks in specific functional areas.
6. As a user, I want resolution durations formatted as days, hours, and minutes with total decimal hours in parentheses (for example: `1 day, 4 hours, 30 minutes (28.50 hours)`), so that durations are easy to read and compare.
7. As an automation engineer, I want an optional `--json` command-line flag, so that I can pipe structured output to downstream automated systems.
8. As a user, I want leading and trailing whitespace automatically removed from CSV headers and cells, so that formatting inconsistencies do not break parsing.
9. As a user, I want the tool to support standard ISO-8601 timestamp formats (both `YYYY-MM-DD HH:MM:SS` and `YYYY-MM-DDTHH:MM:SS` with optional timezone offsets), so that exports from diverse ticketing platforms work seamlessly.
10. As a data analyst, I want tickets with missing `resolved_at` or non-resolved statuses excluded from resolution time calculations, so that open tickets do not distort resolution averages.
11. As a data analyst, I want a dedicated section listing the `ticket_id` of all tickets skipped from resolution time calculations, so that I have complete visibility into open or unresolved items.
12. As a data analyst, I want tickets with invalid negative resolution durations (`resolved_at < created_at`) excluded from resolution time calculations and reported as skipped, so that corrupted timestamps do not skew metrics.
13. As a user, I want the tool to display `N/A (No resolved tickets)` when no tickets in the dataset or category are resolved, so that the program does not crash with a division-by-zero error.
14. As a user, I want malformed rows to generate clear warning messages on `stderr` referencing the specific `ticket_id`, so that I can trace data issues back to source records.
15. As a user, I want malformed rows lacking a `ticket_id` to generate warning messages on `stderr` referencing the row number (for example: `Row 12`), so that I can identify broken rows in the source CSV.
16. As a user, I want the tool to continue processing all valid rows when individual rows are malformed, so that partial data anomalies do not abort the entire report.
17. As a script runner, I want the tool to exit with code `1` and print an error message to `stderr` if the specified file does not exist or is unreadable, so that pipeline failures are captured.
18. As a script runner, I want the tool to exit with code `1` and print an error message to `stderr` if the file is empty or missing required headers, so that invalid input files are caught immediately.
19. As a developer, I want a complete `pytest` test suite validating normal paths, edge cases, and CLI behaviors, so that changes can be safely made in the future.

## Implementation Decisions

- **Runtime Architecture**: Built using only the Python standard library (`csv`, `datetime`, `argparse`, `sys`, `pathlib`). No external runtime packages (such as `pandas`) are required.
- **CLI Interface**: 
  - Entry point: `ticket_summary.py`
  - Positional argument: `file` (path to the input CSV file)
  - Optional flag: `--json` (emits JSON output to `stdout`)
  - Standard streams: Clean summary/JSON on `stdout`; error and row warnings on `stderr`.
  - Exit codes: `0` on successful summary generation; `1` on missing/unreadable file or fatal CSV header error.
- **CSV Parsing and Schema**:
  - Required columns: `ticket_id`, `created_at`, `resolved_at`, `category`, `priority`, `status`.
  - Headers and cell values are stripped of leading/trailing whitespace.
  - Rows missing required columns or containing invalid `created_at` timestamps are flagged on `stderr` and omitted from metrics.
- **Timestamp Parsing**:
  - Flexible ISO-8601 parsing supporting space-separated and `T`-separated date-time strings, as well as UTC and timezone offset specifiers (`Z`, `+HH:MM`, `-HH:MM`).
  - Timestamps are normalized to ensure consistent duration arithmetic.
- **Metric Computation**:
  - `ticket_count`: Count of valid tickets per category.
  - `resolution_time`: Calculated as `resolved_at - created_at` strictly when `resolved_at` is populated and `resolved_at >= created_at`.
  - Overall average resolution time: Total resolution duration of all valid resolved tickets divided by the count of valid resolved tickets.
  - Category average resolution time: Total resolution duration of resolved tickets in that category divided by the count of resolved tickets in that category.
  - Display format: Formatted as `X days, Y hours, Z minutes (Total.HH hours)`.
- **Skipped Tickets Tracking**:
  - Unresolved tickets and tickets with invalid resolution order are tracked by `ticket_id` and reason, then output in a dedicated section on `stdout` (or in the JSON payload).

## Testing Decisions

- **Single High-Level Seam**:
  - All automated tests exercise the tool through the CLI / top-level application interface (`ticket_summary.py` and its main entrypoint function).
  - Tests verify external behavior only: input files/arguments mapped to `stdout`, `stderr`, and exit codes.
  - No internal private methods or implementation details are directly coupled in tests.
- **Test Framework**:
  - Automated tests are written using `pytest`.
- **Test Matrix**:
  1. Clean CSV with mixed categories and resolved tickets (validates correct category counts and average resolution time).
  2. Category-level average resolution calculation and alphabetical sorting.
  3. Exclusion and reporting of unresolved tickets (missing `resolved_at` or open statuses) by `ticket_id`.
  4. Exclusion and reporting of tickets where `resolved_at < created_at`.
  5. Dataset with zero resolved tickets (verifies `N/A (No resolved tickets)` output without crash).
  6. Malformed CSV rows (verifies warnings on `stderr` with `ticket_id` or row number, while valid rows are still calculated).
  7. CSV with extraneous whitespace in headers and cell values.
  8. Non-existent file path and unreadable file handling (verifies exit code `1` and `stderr` output).
  9. Empty CSV file and missing headers (verifies exit code `1` and `stderr` output).
  10. `--json` flag output validation (verifies valid JSON structure and correct data fields).

## Out of Scope

- Writing to or modifying the input CSV file.
- Direct synchronization with ticketing APIs (such as Jira, GitHub Issues, or Zendesk).
- Graphical User Interface (GUI) or web server endpoints.
- Integration of third-party analytical frameworks (`pandas`, `numpy`).

## Further Notes

- The test suite will use temporary files (`tmp_path` fixture in `pytest`) to construct test CSV inputs cleanly without leaving leftover files.
