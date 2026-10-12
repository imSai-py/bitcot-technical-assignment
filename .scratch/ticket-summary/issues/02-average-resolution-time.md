# 02: Average Resolution Time Calculation and Duration Formatting

**What to build:** Calculates resolution durations (`resolved_at - created_at`) from ISO-8601 timestamps. Computes overall average resolution time and category-level average resolution time. Formats durations in days, hours, and minutes with total decimal hours in parentheses. Displays `"N/A (No resolved tickets)"` when zero tickets are resolved. Includes automated `pytest` tests.

**Blocked by:** 01: Baseline CLI Runner and Category Count Summary

**Status:** resolved

- [x] Parses standard ISO-8601 timestamps (`YYYY-MM-DD HH:MM:SS`, `YYYY-MM-DDTHH:MM:SS`, and timezone offsets) for `created_at` and `resolved_at`
- [x] Calculates `resolved_at - created_at` for resolved tickets where `resolved_at >= created_at`
- [x] Computes overall average resolution time across all resolved tickets
- [x] Computes average resolution time for each category
- [x] Formats durations as `X days, Y hours, Z minutes (Total.HH hours)`
- [x] Displays `"N/A (No resolved tickets)"` when no tickets in the dataset or category are resolved
- [x] Automated tests using `pytest` verify duration arithmetic, duration formatting, and zero resolved tickets
