# TypeScript SLA Library

A strongly typed TypeScript library for calculating service level agreement (SLA) deadlines and detecting SLA breaches.

## Features
- **Configurable Priorities**: Default targets for `urgent` (4h), `high` (8h), `normal` (24h), and `low` (72h), with custom overrides.
- **Breach Detection**: Determines breach status (`isBreached`) and exact elapsed breach duration in milliseconds (`breachDurationMs`).
- **Input Flexibility**: Accepts JavaScript `Date` instances, ISO-8601 strings, and numeric timestamps.
- **Business Hours Engine**: Optional schedule calculations (Monday to Friday, 09:00 - 18:00) with off-hours submission adjustments and holiday exclusions.

## Scripts & Commands
```bash
# Run unit and integration tests
npm test

# Build distribution bundle
npm run build

# Run interactive demo
npx tsx scripts/demo.ts
```

## Docker Usage
```bash
docker build -t typescript-sla .
docker run --rm typescript-sla
```
