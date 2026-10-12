# 02: Root cause analysis and task notes documentation

**What to build:** Record defect analysis and discovery methodology in task notes and verify linting.

**Blocked by:** 01: Multi-day SLA breach calculation and automated tests

**Status:** resolved

- [x] Append two lines of root cause notes to `Task.md.txt`
- [x] Format and lint code with `black` and `ruff`

## Answer
Documented what was wrong (`delta.seconds` ignoring day boundaries) and how it was discovered (tracing ticket B duration across days returning 2.0 instead of 26.0 hours) in `task.md.txt`. Verified all files with `black` formatting and `pytest`.
