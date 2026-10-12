# 01: Multi-day SLA breach calculation and automated tests

**What to build:** Fix duration calculation for tickets spanning multiple days and provide automated pytest test suite.

**Blocked by:** None (can start immediately).

**Status:** resolved

- [x] Place `debug_warmup.py` into repository
- [x] Fix `_hours_between()` to use `delta.total_seconds() / 3600`
- [x] Add pytest tests in `tests/test_debug_warmup.py` verifying docstring sample and multi-day edge cases
- [x] Verify test suite passes with pytest

## Answer
Replaced `delta.seconds / 3600` with `delta.total_seconds() / 3600` in `_hours_between()` inside `debug_warmup.py`. Verified that all 5 tests pass including the docstring sample producing `{'breached': ['B', 'C'], 'average_hours': 13.0, 'counted': 3}`.
