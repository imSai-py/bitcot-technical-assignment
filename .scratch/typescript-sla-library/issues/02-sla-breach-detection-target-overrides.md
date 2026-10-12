# 02: SLA Breach Detection and Target Overrides

**What to build:** Implement `checkSlaBreach` to evaluate whether an open or resolved ticket breached its deadline, compute the exact breach duration in milliseconds, and allow custom priority hour overrides.

**Blocked by:** 01: Project Scaffolding and Core SLA Deadline Calculation

**Status:** ready-for-agent

- [ ] Export `checkSlaBreach(ticket, options?)` returning `SlaResult` (`isBreached`, `breachDurationMs`, `deadline`)
- [ ] For open ticket checked before deadline: return `isBreached: false` and `breachDurationMs: 0`
- [ ] For open ticket checked exactly at deadline: return `isBreached: false` and `breachDurationMs: 0`
- [ ] For open ticket checked after deadline: return `isBreached: true` with duration in ms
- [ ] For ticket resolved before deadline: return `isBreached: false` and `breachDurationMs: 0` even if checked late
- [ ] For ticket resolved after deadline: return `isBreached: true` with duration measured to resolution time
- [ ] When `checkTime` is omitted, default to current timestamp (`new Date()`)
- [ ] Support custom priority hour overrides passed in options
- [ ] All unit tests pass in Vitest
