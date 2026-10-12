# PR 02: Average Resolution Time Calculation and Duration Formatting

**Branch:** `feat/02/average-resolution-time` -> `dev`  
**Ticket:** [02-average-resolution-time.md](file:///C:/Users/saila/Documents/BITCOT_TASK/Python-ticket-summary-tool/.scratch/ticket-summary/issues/02-average-resolution-time.md)

## Summary

```text
compute_metrics(rows)
  parse_iso_timestamp(created_at) -> UTC datetime
  parse_iso_timestamp(resolved_at) -> UTC datetime
  if resolved_dt >= created_dt
    duration = resolved_dt - created_dt
    accumulate overall and per-category durations
format_duration(seconds)
  split into days, hours, minutes
  output "X days, Y hours, Z minutes (Total.HH hours)"
```

## Evidence

- **Before:**
  ```text
  AssertionError: assert 'Average Resolution Time' in stdout
  FAILED tests/test_ticket_summary.py::test_overall_and_category_average_resolution_time
  FAILED tests/test_ticket_summary.py::test_zero_resolved_tickets_displays_na
  FAILED tests/test_ticket_summary.py::test_iso_timestamp_variants_and_timezones
  ```
- **After:**
  ```text
  tests/test_ticket_summary.py::test_overall_and_category_average_resolution_time PASSED
  tests/test_ticket_summary.py::test_zero_resolved_tickets_displays_na PASSED
  tests/test_ticket_summary.py::test_iso_timestamp_variants_and_timezones PASSED
  7 passed in 1.02s
  ```

## Merge Danger

**Door:** two-way  
Calculation changes can be safely reverted or modified without persistent side effects.

**Blast Radius:** low  
Additive duration formatting within output presentation.
