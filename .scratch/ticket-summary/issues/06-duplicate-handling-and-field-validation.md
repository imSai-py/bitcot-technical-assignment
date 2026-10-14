# 06: Duplicate Ticket Handling and ID Placeholder Validation

**What to build:** Deduplicate rows with duplicate ticket IDs using a seen-IDs set so duplicates are logged to stderr and not counted twice. Validate ticket IDs to reject invalid placeholder values such as `N/A`.

**Blocked by:** 05: Dataset Anomalies, Category Normalization, and Summary Sections

**Status:** resolved

- [x] Maintain `seen_ticket_ids` set in `read_and_validate_csv` to detect and skip duplicate ticket IDs
- [x] Emit stderr warning for duplicate ticket IDs: `Warning: <ticket_id>: Duplicate ticket ID (skipped).`
- [x] Validate `ticket_id` against empty and placeholder values (`N/A`, `NA`, `NULL`, `NONE`)
- [x] Add automated unit tests in `test_code_review_fixes.py` covering duplicate rejection and `N/A` validation
- [x] All test suites pass under the unified verification gate
