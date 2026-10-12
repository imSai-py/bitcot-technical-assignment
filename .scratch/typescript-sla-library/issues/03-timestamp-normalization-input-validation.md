# 03: Timestamp Normalization and Input Validation

**What to build:** Normalize all date inputs (`Date`, ISO string, epoch number) and enforce robust input validation with descriptive error messages.

**Blocked by:** 02: SLA Breach Detection and Target Overrides

**Status:** ready-for-agent

- [ ] Accept `Date | string | number` for `createdAt`, `resolvedAt`, and `checkTime`
- [ ] Throw descriptive `Error` when any timestamp is an invalid date string or NaN
- [ ] Throw descriptive `Error` when `priority` is not in the recognized target map
- [ ] Throw descriptive `Error` when `resolvedAt` is earlier than `createdAt`
- [ ] All unit tests pass in Vitest
