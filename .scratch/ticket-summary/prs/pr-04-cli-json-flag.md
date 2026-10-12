# PR 04: CLI `--json` Flag for Structured Output

**Branch:** `feat/04/cli-json-flag` -> `dev`  
**Ticket:** [04-cli-json-flag.md](file:///C:/Users/saila/Documents/BITCOT_TASK/Python-ticket-summary-tool/.scratch/ticket-summary/issues/04-cli-json-flag.md)

## Summary

```diff
 parser.add_argument("file", type=Path)
+parser.add_argument("--json", action="store_true", help="Output summary as structured JSON.")
...
+if output_json:
+    print(format_summary_json(metrics))
+else:
+    print(format_summary_text(metrics))
```

## Evidence

- **Before:**
  ```text
  ticket_summary.py: error: unrecognized arguments: --json
  FAILED tests/test_ticket_summary.py::test_json_output_flag
  FAILED tests/test_ticket_summary.py::test_json_output_with_warnings_keeps_stdout_valid_json
  ```
- **After:**
  ```text
  tests/test_ticket_summary.py::test_json_output_flag PASSED
  tests/test_ticket_summary.py::test_json_output_with_warnings_keeps_stdout_valid_json PASSED
  11 passed in 1.89s
  ```

## Merge Danger

**Door:** two-way  
Optional CLI flag additions can be altered or removed cleanly.

**Blast Radius:** low  
Default text output remains completely unaffected; only callers with `--json` receive JSON payloads.
