# Excel Data Anomalies and Cross-Verification

Excel Data Anomalies addresses common data corruption and formatting inconsistencies exported from spreadsheet tools (e.g., non-ISO slash dates, impossible calendar days, casing divergence, compound comma categories, extra columns, and typo statuses).

## Sub-features

- `anomaly-date-slash-formats`: Detects and warns about Excel/UK slash date strings (`DD/MM/YYYY HH:MM`) which do not conform to ISO-8601 (`YYYY-MM-DD HH:MM:SS`), logging `Warning: <ticket_id>: Invalid or missing created_at.` and safely skipping the row.
- `anomaly-date-impossible-bounds`: Detects invalid calendar dates (such as February 30th: `2026-02-30 10:00`), logging `Warning: <ticket_id>: Invalid or missing created_at.` and preventing datetime constructor crashes.
- `anomaly-date-inverted-chronology`: Detects tickets with resolution earlier than creation (`resolved_at < created_at`), logs `Warning: <ticket_id>: Resolved date earlier than created date.`, and classifies under `Resolved before created`.
- `anomaly-casing-split`: Identifies distinct case variants (`Billing`, `billing`, and `BILLING`), tallies them separately, and maintains case accuracy in the category output.
- `anomaly-compound-comma-category`: Preserves properly quoted category names containing commas (`"Billing, refunds"`), preventing CSV column shifting.
- `anomaly-extra-columns`: Tolerates rows containing more than the six standard headers (e.g., extra trailing notes such as `note: sent by phone`), aligning core columns without crashing.
- `anomaly-non-standard-status`: Accurately handles non-standard statuses (e.g., `escalatd` or `escalate`), excluding them from resolved duration averages and tracking them under skipped tickets.

## How to get to it (user POV)

- Run `python ticket_summary.py <path-to-csv>` on raw exports.
- Run `python ticket_summary.py tickets.csv` on the repository default dataset.
- Run the automated anomaly check: `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature excel-anomalies`.

## Driving it with python ticket_summary.py

Preconditions:
- Python 3.10+ runtime available.
- Entrypoint exists at `python-ticket-summary/ticket_summary.py`.

- **Drive Slash Dates & Invalid Dates.**
  Provide a CSV containing:
  - T-D1: `02/03/2026 10:02` (Slash format).
  - T-D2: `2026-02-30 10:00` (February 30th).
  Run `python python-ticket-summary/ticket_summary.py <csv-file>`.
  Exit code is `0`.
  `stderr` contains:
  ```text
  Warning: T-D1: Invalid or missing created_at.
  Warning: T-D2: Invalid or missing created_at.
  ```
  Neither invalid row is tallied in category counts or resolution times.

- **Drive Category Casing Variants (Billing * 3).**
  Provide a CSV containing `Billing`, `billing`, and `BILLING`.
  Run `python python-ticket-summary/ticket_summary.py <csv-file>`.
  Exit code is `0`.
  `stdout` displays distinct entries:
  ```text
  Tickets by Category:
    BILLING: 1 (Avg Resolution: ...)
    Billing: 2 (Avg Resolution: ...)
    billing: 1 (Avg Resolution: ...)
  ```

- **Drive Compound Category with Comma.**
  Provide a row containing `"Billing, refunds"`.
  Run `python python-ticket-summary/ticket_summary.py <csv-file>`.
  Exit code is `0`.
  `stdout` contains:
  ```text
    Billing, refunds: 1 (Avg Resolution: N/A (No resolved tickets))
  ```

- **Drive Extra Column and Escalate Status.**
  Provide a row with an extra 7th column (`note: sent by phone`) and a row with status `escalatd`.
  Run `python python-ticket-summary/ticket_summary.py <csv-file>`.
  Exit code is `0`.
  The extra column is ignored without raising an index error. Ticket with status `escalatd` is placed under `Skipped Tickets (Resolution Time)`.

- **Verify Real Repository Dataset (`tickets.csv`).**
  Run `python python-ticket-summary/ticket_summary.py python-ticket-summary/tickets.csv`.
  Exit code is `0`.
  `stderr` shows:
  ```text
  Warning: TCK-1183: Invalid or missing created_at.
  Warning: TCK-1007: Missing category.
  Warning: TCK-1021: Invalid or missing created_at.
  Warning: TCK-1162: Invalid or missing created_at.
  Warning: TCK-1025: Invalid or missing created_at.
  Warning: TCK-1056: Invalid or missing created_at.
  Warning: TCK-1137: Resolved date earlier than created date.
  ```
  `stdout` confirms:
  - `Billing: 38`, `BILLING: 1`, `billing: 1`
  - `Billing, refunds: 1`
  - Skipped items include `TCK-1009` (`escalatd`), `TCK-1137` (`Resolved before created`), and `TCK-2999` (extra column row).

## Gotchas

- Excel date formatting: Excel exports often use local machine locale (e.g. `DD/MM/YYYY` or `MM/DD/YYYY`). Since the tool enforces strict ISO-8601 parsing, slash dates are rejected with warnings.
- Leading whitespace before quotes: In CSV, `' "Billing, refunds"'` is treated as unquoted by `csv.reader`. Quoted fields must immediately follow the delimiter (`,,"Billing, refunds",`).
- Extra columns: Never use strict column length equality assertions without padding or slice truncation; real datasets frequently include ad-hoc note columns.
