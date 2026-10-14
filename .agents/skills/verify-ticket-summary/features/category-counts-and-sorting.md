# Category Counts and Sorting

The Category Counts feature tallies tickets grouped by category, trims surrounding whitespace from column headers and values, and outputs an alphabetically sorted summary table.

## Sub-features

- `counts-tally`: Tallies valid tickets per category accurately.
- `counts-sort`: Sorts category names in ascending alphabetical order in the output.
- `counts-whitespace`: Automatically strips leading and trailing whitespace from CSV headers and cells without altering category names.

## How to get to it (user POV)

- Run `python ticket_summary.py <path-to-csv>` from the terminal.
- Run `python python-ticket-summary/ticket_summary.py <path-to-csv>` from the project root.

## Driving it with python ticket_summary.py

Preconditions:
- Python 3.10+ runtime available.
- `python-ticket-summary/ticket_summary.py` exists and passes syntax validation.

- **Standard Alphabetical Tally.** Provide a CSV with categories in random order (`Hardware`, `Billing`, `Access`).
  Run `python python-ticket-summary/ticket_summary.py <csv-file>`.
  Exit code is `0`. `stdout` displays `Tickets by Category:` followed by categories listed alphabetically:
  ```text
  Tickets by Category:
    Access: 1 (Avg Resolution: ...)
    Billing: 2 (Avg Resolution: ...)
    Hardware: 1 (Avg Resolution: ...)
  ```
- **Whitespace Immunity.** Provide a CSV where headers have padding spaces (` ticket_id , created_at , category `) and data cells have padded text (` Billing `).
  Run `python python-ticket-summary/ticket_summary.py <whitespace-csv-file>`.
  Exit code is `0`. The category is correctly recognized as `Billing` and tallied without space-induced key fragmentation.
- **Proof Artifact.** Run `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature category-counts`.
  Exit code is `0`. Inspect `artifacts/verify-ticket-summary/run_summary.json` to verify `category_counts_and_sorting` reports `PASS`.

## Gotchas

- Case sensitivity: Standard category values (`Billing` vs `billing`) will group separately as distinct Python strings; ensure test CSVs intentionally test the casing intended.
- Extra commas or quotes in cell text must be properly quoted in CSV formatting to prevent shifting column indexes.
