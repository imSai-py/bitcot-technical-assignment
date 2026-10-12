# 03: Row Validation, Warning Logs, and Skipped Tickets Reporting

**What to build:** Validates row data and timestamp chronology. Logs warnings to `stderr` with `ticket_id` (or `Row <number>`) for malformed rows while continuing to process valid rows. Outputs a dedicated summary section on `stdout` listing all skipped tickets by `ticket_id` grouped by reason (unresolved tickets or negative durations). Includes automated `pytest` tests.

**Blocked by:** 02: Average Resolution Time Calculation and Duration Formatting

**Status:** resolved

- [x] Flags malformed rows (missing required fields or invalid `created_at`) on `stderr` with `ticket_id` (or row number if `ticket_id` is missing)
- [x] Continues processing remaining valid rows when individual rows are malformed
- [x] Excludes unresolved tickets (missing `resolved_at`) and negative duration tickets (`resolved_at < created_at`) from resolution time calculations
- [x] Displays a dedicated "Skipped Tickets" section on `stdout` listing skipped ticket IDs grouped by reason
- [x] Automated tests using `pytest` verify stderr warnings, continued processing of valid rows, and stdout skipped ticket reporting
