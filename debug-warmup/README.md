# Debug Warm-Up Task

This sub-project resolves the SLA breach reporting defect in `debug_warmup.py`.

## Problem & Root Cause
The original implementation in `debug_warmup.py` accessed `delta.seconds` instead of `delta.total_seconds()`.

In Python's `datetime.timedelta`, `delta.seconds` returns only the remaining seconds within a single day modulo 86400, discarding elapsed calendar days. This lost 24 hours for every full calendar day elapsed, masking SLA breaches and reporting falsely low average resolution times.

## How It Was Found
Tracing ticket `B` across calendar days (created `2026-03-01 08:00:00`, resolved `2026-03-02 10:00:00` — 26 elapsed hours) revealed that the original function returned only 2.0 hours.

## Fix
Updated `_hours_between()` to divide `delta.total_seconds()` by 3600.0, capturing all elapsed calendar days and hours accurately.

## Running Tests
```bash
python -m pytest tests
```
