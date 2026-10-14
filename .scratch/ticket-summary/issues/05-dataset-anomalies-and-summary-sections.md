# 05: Dataset Anomalies, Category Normalization, and Summary Sections

**What to build:** Adds robust handling for real-world Excel ticket anomalies including case-insensitive category normalization (merging Billing, billing, BILLING while preserving compound categories), dedicated escalated tickets section, note extraction from headers and extra columns, and a dedicated resolved tickets section listing all resolved ticket IDs independent of duration arithmetic.

**Blocked by:** 04: CLI `--json` Flag for Structured Output

**Status:** resolved

- [x] Case-insensitive category normalization merging casing variants into canonical category names
- [x] Escalated tickets section tracking explicit escalated statuses (`escalated`, `escalatd`)
- [x] Extraction of ticket notes from both explicit header columns and extra trailing columns
- [x] Dedicated resolved tickets section tracking all tickets with resolved terminal status
- [x] Comprehensive automated unit and integration tests passing across all test suites
