# 05: Holiday Exclusion and Timezone Configuration for Business Hours

**What to build:** Extend the business hours engine to support custom holiday date exclusions and configurable timezones or UTC offsets.

**Blocked by:** 04: Business Hours Calculation Engine

**Status:** ready-for-agent

- [ ] Support `holidays?: (Date | string | number)[]` in business hours config
- [ ] Skip designated holidays like weekends during SLA calculations
- [ ] Support custom timezone or UTC offset in business hours config
- [ ] All unit tests pass in Vitest
