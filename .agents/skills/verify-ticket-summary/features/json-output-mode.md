# JSON Output Mode

JSON Output Mode emits complete machine-readable metrics to `stdout` when invoked with the `--json` flag while preserving clean stream separation for warnings on `stderr`.

## Sub-features

- `json-flag`: Enables structured JSON formatting via the `--json` CLI option.
- `json-stream-separation`: Directs warnings and non-fatal diagnostics exclusively to `stderr` so `stdout` can be piped directly into `jq` or JSON decoders.
- `json-schema-integrity`: Produces top-level keys `category_counts`, `overall_average_resolution_time`, `categories`, and `skipped_tickets`.
- `json-category-detail`: Provides nested objects for each category with `count` and formatted `average_resolution_time`.

## How to get to it (user POV)

- Run `python ticket_summary.py <path-to-csv> --json` from the terminal.
- Pipe output into downstream consumers: `python ticket_summary.py <path-to-csv> --json | jq .`.

## Driving it with python ticket_summary.py

Preconditions:
- Python 3.10+ runtime available.
- Test CSV contains a mix of resolved tickets, unresolved tickets, and at least one malformed row.

- **Drive JSON Invocation.**
  Run `python python-ticket-summary/ticket_summary.py <csv-file> --json`.
  Exit code is `0`.
- **Verify Stderr Isolation.**
  Malformed row warnings appear on `stderr`: `Warning: Row 2: Missing ticket_id.`
  No warning text appears on `stdout`.
- **Verify Valid JSON on Stdout.**
  `stdout` must parse successfully with `json.loads(stdout)`.
  The parsed dictionary has:
  ```json
  {
    "category_counts": {
      "Billing": 1
    },
    "overall_average_resolution_time": "0 days, 2 hours, 0 minutes (2.00 hours)",
    "categories": {
      "Billing": {
        "count": 1,
        "average_resolution_time": "0 days, 2 hours, 0 minutes (2.00 hours)"
      },
      "Hardware": {
        "count": 1,
        "average_resolution_time": "N/A (No resolved tickets)"
      }
    },
    "skipped_tickets": {
      "Unresolved / Missing resolution date": ["T-2"]
    }
  }
  ```
- **Proof Artifact.** Run `python .cursor/skills/verify-ticket-summary/scripts/verify_ticket_summary.py drive --feature json-mode`.
  Exit code is `0`. Check `artifacts/verify-ticket-summary/run_summary.json` to verify `json_output_mode` reports `PASS`.

## Gotchas

- Any `print()` calls in the application code without `file=sys.stderr` will invalidate the JSON payload on `stdout`.
- Ensure duration values in the JSON match the human-readable string format required by the specification rather than raw seconds.
