# 04: Business Hours Calculation Engine

**What to build:** Implement optional business hours calculation (Monday to Friday, 09:00 to 18:00 UTC) with off-hours start advancement, overnight pauses, and weekend skipping.

**Blocked by:** 02: SLA Breach Detection and Target Overrides

**Status:** resolved

- [x] Enable business hours mode via options (`businessHours: true` or config object)
- [x] For ticket created inside business hours: calculate deadline by counting only 09:00 - 18:00 window (9 hours/day)
- [x] For ticket created outside business hours (evenings or weekends): advance start to 09:00 on the next business day
- [x] Accurately pause overnight (18:00 to 09:00 next day)
- [x] Accurately skip weekends (Saturday and Sunday)
- [x] Measure breach status and breach duration correctly in business hours mode
- [x] All unit tests pass in Vitest
