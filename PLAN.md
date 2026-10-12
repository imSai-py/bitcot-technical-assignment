# Implementation Plan

## Python Ticket Summary Tool
- Build a standard-library command-line tool to parse CSV ticket datasets and compute key metrics.
- Calculate category distribution counts, skipped records, and formatted average resolution times.
- Provide structured JSON output support and write warning logs to standard error for malformed rows.
- Package the application in Docker and verify parsing and edge cases with pytest automated tests.

## TypeScript SLA Library
- Build a TypeScript library to compute resolution deadlines and identify SLA breaches.
- Implement business hours logic with configurable operating schedules and timezones.
- Exclude company holidays and weekends from elapsed resolution calculations.
- Validate ISO timestamps and verify calculations with Vitest unit tests.

## Debug Warm-up
- Identify duration calculation errors that occur when tickets span multiple days.
- Update the calculation algorithm to use total_seconds() instead of single-day seconds.
- Validate ticket duration calculations across day boundaries and negative time values.
- Verify the fix against edge cases using automated pytest test cases.
