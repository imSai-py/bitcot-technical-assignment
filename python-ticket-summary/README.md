# Python Ticket Summary CLI Tool

A standalone command-line utility built exclusively with Python standard library packages to summarize ticket datasets from CSV exports.

## Features
- **Category Ticket Counts**: Alphabetically sorted counts of tickets by category.
- **Average Resolution Time**: Computes overall average resolution time and breakdowns per category in `X days, Y hours, Z minutes (Total.HH hours)` format.
- **Skipped Ticket Tracking**: Visibility into tickets bypassed due to missing resolution timestamps or negative elapsed times.
- **Robust Error Handling**: Warns about malformed rows on `stderr` while completing calculations on valid rows.
- **JSON Output**: Supports `--json` flag for machine-readable output.

## Usage
```bash
# Standard summary
python ticket_summary.py tickets.csv

# JSON output
python ticket_summary.py tickets.csv --json
```

## Running Tests
```bash
python -m pytest tests
```

## Docker Usage
```bash
docker build -t ticket-summary .
docker run --rm ticket-summary --help
```
