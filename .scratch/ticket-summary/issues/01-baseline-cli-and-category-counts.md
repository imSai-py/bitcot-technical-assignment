# 01: Baseline CLI Runner and Category Count Summary

**What to build:** A runnable command line tool (`python ticket_summary.py tickets.csv`). It reads the input CSV, trims whitespace from headers and values, computes ticket totals for each category, prints an alphabetically sorted category table on `stdout`, exits with code `1` on missing or unreadable files, and includes automated `pytest` tests.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] CLI accepts a CSV file path as a positional argument: `python ticket_summary.py <file>`
- [x] Strips leading and trailing whitespace from CSV headers and cells
- [x] Groups tickets by category and counts them
- [x] Outputs an alphabetically sorted category summary to `stdout`
- [x] Exits with code `1` and prints an error message to `stderr` if the file does not exist, cannot be read, or is empty
- [x] Automated tests using `pytest` verify valid summary generation, alphabetical sorting, whitespace handling, and missing file error behavior
