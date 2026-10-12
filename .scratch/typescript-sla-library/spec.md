# Specification: TypeScript SLA Library

Status: resolved

## Problem Statement

Engineering, customer success, and operations teams manage service requests with strict contractual resolution commitments. Each request has a designated priority that determines its allowed resolution timeframe. When tickets lack automated SLA tracking, teams cannot reliably detect when a ticket breaches its deadline or calculate the duration of the breach. In addition, basic calendar calculations penalize support organizations during nights and weekends when staff are off-duty.

## Solution

A typed, standalone library that calculates SLA deadlines and detects SLA breaches. The library evaluates tickets based on priority and creation timestamp, accounts for ticket resolution timestamps, and reports whether a breach occurred along with the exact breach duration in milliseconds. By default, it operates across continuous 24/7 calendar time, while offering an optional business hours calculation engine that only counts working hours (Monday through Friday, 09:00 to 18:00) and accounts for off-hour submissions and holidays.

## User Stories

1. As an API consumer, I want to evaluate an urgent priority ticket, so that I can track its 4-hour SLA deadline.
2. As an API consumer, I want to evaluate a high priority ticket, so that I can track its 8-hour SLA deadline.
3. As an API consumer, I want to evaluate a normal priority ticket, so that I can track its 24-hour SLA deadline.
4. As an API consumer, I want to evaluate a low priority ticket, so that I can track its 72-hour SLA deadline.
5. As an API consumer, I want to check an open ticket before its deadline has passed, so that I receive `isBreached: false` and a breach duration of 0.
6. As an API consumer, I want to check an open ticket exactly at its deadline, so that the status is not considered breached.
7. As an API consumer, I want to check an open ticket after its deadline has passed, so that I receive `isBreached: true` with the elapsed duration past the deadline in milliseconds.
8. As an API consumer, I want to check a ticket that was resolved before its deadline, so that it is reported as not breached even when the current check time is past the deadline.
9. As an API consumer, I want to check a ticket that was resolved after its deadline, so that it is reported as breached with the breach duration calculated from the deadline to the resolution time.
10. As an API consumer, I want to omit the check time parameter when checking an unresolved ticket, so that the library defaults to checking against the current timestamp.
11. As an API consumer, I want to supply creation and resolution timestamps as standard JavaScript `Date` instances, so that I can pass native date objects directly.
12. As an API consumer, I want to supply timestamps as ISO 8601 formatted strings, so that I do not need to convert JSON string dates manually.
13. As an API consumer, I want to supply timestamps as UNIX epoch millisecond numbers, so that I can work directly with numeric epoch values.
14. As an API consumer, I want to supply custom priority target hours, so that I can customize SLA targets to match non-standard customer contracts.
15. As an API consumer, I want the library to reject invalid date inputs with clear error messages, so that bugs in caller data are caught early.
16. As an API consumer, I want the library to reject unknown priority values with clear error messages, so that invalid tickets do not produce invalid calculations.
17. As an API consumer, I want the library to reject tickets where resolution occurs before creation, so that impossible timelines are flagged immediately.
18. As an API consumer, I want to calculate an explicit deadline timestamp for a ticket, so that I can display the SLA due date on a dashboard without performing a breach check.
19. As an API consumer, I want to enable business hours mode, so that SLA deadlines only consume hours during the defined working schedule (Monday to Friday, 09:00 to 18:00).
20. As an API consumer, I want tickets created outside business hours (such as evening or weekend) to begin their SLA clock at 09:00 on the next business day, so that off-hours creation does not consume SLA time while the team is closed.
21. As an API consumer, I want SLA calculations during business hours mode to pause overnight between 18:00 and 09:00 the following morning, so that overnight hours do not count toward resolution.
22. As an API consumer, I want SLA calculations during business hours mode to skip weekend days (Saturday and Sunday), so that weekend hours do not count toward resolution.
23. As an API consumer, I want to provide a list of holiday dates in business hours mode, so that designated holidays are skipped like weekends.
24. As an API consumer, I want business hours calculations to run in UTC by default, so that calculations are deterministic across distributed servers and test environments.
25. As an API consumer, I want to configure custom business hour timezones or offsets, so that regional operational hours can be tracked accurately.
26. As a TypeScript developer, I want comprehensive exported type definitions, so that my editor and compiler enforce strict typing on ticket inputs and SLA results.

## Implementation Decisions

- **Single Module Architecture**: The library consists of a single focused module exposing pure functions without external runtime dependencies or side effects.
- **Data Models**:
  - `Priority`: Union type representing `'urgent' | 'high' | 'normal' | 'low'`.
  - `Ticket`: Input shape containing `priority`, `createdAt` (`Date | string | number`), and optional `resolvedAt` (`Date | string | number`).
  - `SlaResult`: Output shape containing `isBreached` (`boolean`), `breachDurationMs` (`number`), and `deadline` (`Date`).
  - `SlaOptions`: Optional configuration object accepting custom priority durations, business hours settings, and check time override.
- **Default SLA Target Schedule**:
  - Urgent: 4 hours (14,400,000 ms)
  - High: 8 hours (28,800,000 ms)
  - Normal: 24 hours (86,400,000 ms)
  - Low: 72 hours (259,200,000 ms)
- **Breach Measurement Rule**:
  - If `resolvedAt` is defined, the reference time is `resolvedAt`.
  - If `resolvedAt` is undefined, the reference time is `checkTime` (defaults to current time).
  - A ticket is breached if reference time > `deadline`.
  - When breached, `breachDurationMs = referenceTime - deadline`. When not breached, `breachDurationMs = 0`.
- **Validation**:
  - Throws descriptive runtime errors if `createdAt`, `resolvedAt`, or `checkTime` evaluates to `NaN`.
  - Throws if `priority` is not in the recognized target map.
  - Throws if `resolvedAt < createdAt`.
- **Business Hours Engine**:
  - Business day spans 09:00 to 18:00 (9 working hours / 32,400,000 ms per working day).
  - Active business days: Monday through Friday, excluding supplied holiday dates.
  - Off-hours creation: start clock advances to 09:00 on the subsequent business day.
  - Deadline calculation iteratively consumes working hours across valid business windows until target duration is satisfied.
  - Default timezone is UTC for cross-environment reproducibility, with optional IANA timezone or hour offset support.

## Testing Decisions

- **Definition of Good Tests**: Tests must verify public behavioral contracts only (inputs and outputs), never testing internal helper functions or implementation details. Tests must be fast, fully deterministic, and independent of external state or wall-clock timing (using explicit check times or mock timers).
- **Target Module**: All tests execute against the public functions (`checkSlaBreach`, `calculateSlaDeadline`).
- **Test Scenarios**:
  - Priority target calculations for all 4 priorities under calendar hours.
  - Boundary conditions: check before deadline, exactly at deadline, after deadline.
  - Resolution handling: resolved on time, resolved late, unresolved checked late.
  - Timestamp format handling: ISO string, epoch number, Date object.
  - Error conditions: invalid date strings, unsupported priority strings, negative intervals.
  - Business hours scenarios: intraday tickets, overnight rollovers, weekend spanning, holiday exclusion, off-hours ticket creation.
- **Prior Art**: Modern TypeScript test suites running under Vitest using clear behavior-driven assertions.

## Out of Scope

- Database persistence, ORM integration, or external storage.
- HTTP API endpoints, microservice routing, or web controllers.
- Automated fetching of dynamic national or regional bank holidays via external network APIs (holidays must be provided explicitly as an array).
- Multi-shift working hours (e.g. rotating shifts, split shifts, or intra-day lunch break exclusions).
- Live scheduling, cron jobs, or active background notification listeners.

## Further Notes

- The library is designed as a zero-runtime-dependency package for minimal footprint and maximum compatibility.
- All time duration outputs are normalized to milliseconds to maintain precision and ease of conversion.
