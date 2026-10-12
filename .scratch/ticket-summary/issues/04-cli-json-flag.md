# 04: CLI `--json` Flag for Structured Output

**What to build:** Adds the `--json` command line argument. When enabled, outputs complete structured JSON to `stdout` containing category counts, resolution metrics, and skipped ticket lists, while preserving warning logs on `stderr`. Includes automated `pytest` tests.

**Blocked by:** 03: Row Validation, Warning Logs, and Skipped Tickets Reporting

**Status:** ready-for-agent

- [ ] CLI supports optional `--json` argument: `python ticket_summary.py <file> --json`
- [ ] Emits valid JSON to `stdout` containing category counts, overall average resolution time, category-level resolution times, and skipped tickets
- [ ] Keeps error and warning logs directed to `stderr` so `stdout` remains clean JSON
- [ ] Automated tests using `pytest` verify JSON structure, keys, values, and CLI integration
