# 01: Project Scaffolding and Core SLA Deadline Calculation

**What to build:** Initialize the TypeScript package with Vitest and implement the foundational SLA deadline calculation for standard priority levels (`urgent`: 4h, `high`: 8h, `normal`: 24h, `low`: 72h) using calendar time.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] Project initialized with `package.json` (`"type": "module"`), `tsconfig.json`, and `vitest.config.ts`
- [x] Export `calculateSlaDeadline(ticket, options?)` function
- [x] Export `Priority`, `Ticket`, and `SlaResult` TypeScript types
- [x] Calculate correct deadline for `urgent` (4 hours from creation)
- [x] Calculate correct deadline for `high` (8 hours from creation)
- [x] Calculate correct deadline for `normal` (24 hours from creation)
- [x] Calculate correct deadline for `low` (72 hours from creation)
- [x] All unit tests pass in Vitest
