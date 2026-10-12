# Spec: SLA Breach Report Calculation Fix

Status: ready-for-agent

## Problem Statement

The SLA breach reporting function calculates incorrect duration for tickets that resolve across day boundaries. It uses only the seconds component of the time difference, losing 24 hours for every full day elapsed. Consequently, multi-day tickets that breach SLA are falsely marked as non-breaching, and the reported average resolution hours is incorrectly low.

## Solution

Update the duration calculation to use total elapsed seconds across the full date-time span rather than seconds within a single day. This accurately computes resolution duration for multi-day tickets, correctly flags SLA breaches, and produces accurate average resolution hours.

## User Stories

1. As an operations lead, I want resolution durations for tickets spanning multiple days to include all elapsed days, so that SLA compliance statistics are accurate.
2. As a support manager, I want tickets exceeding their priority SLA threshold over multiple calendar days to appear in the `breached` ticket list, so that overdue tickets receive investigation.
3. As an operations analyst, I want the `average_hours` metric to accurately reflect the true average resolution time across all resolved tickets, so that team reporting is reliable.
4. As an analyst, I want tickets resolved on the same calendar day to continue calculating elapsed hours accurately, so that existing valid calculations do not regress.
5. As an analyst, I want tickets with an empty or missing resolution timestamp to be skipped from counted tickets and duration metrics, so that unresolved tickets do not skew the averages.
6. As an automated test runner, I want to call the public report function with ticket data and priority SLA definitions and receive the exact expected summary payload, so that regression tests verify behavior reliably.
7. As a maintenance engineer, I want the report output to round average resolution hours to two decimal places, so that formatted output remains consistent.

## Implementation Decisions

- **Single High-Level Public Interface**: The public report function accepts a list of ticket records and an SLA mapping table by priority, returning the breached tickets, average resolution hours, and count of processed tickets.
- **Duration Calculation Logic**: Use total elapsed seconds across the full date-time delta divided by 3600 rather than seconds-within-day.
- **Unresolved Ticket Handling**: Tickets without a valid resolution timestamp are bypassed and excluded from both counted totals and breach checks.
- **Precision and Formatting**: The average hours value is rounded to two decimal places when resolved tickets exist; otherwise, it returns zero.
- **Notes Record**: Two descriptive lines documenting the bug explanation and discovery technique are preserved in project documentation.

## Testing Decisions

- **Test Quality Definition**: Tests only exercise the top-level public report function against external inputs and outputs, never private time-parsing helpers.
- **Module Under Test**: The report calculation module.
- **Prior Art**: The sample case provided in the function documentation serves as the baseline regression test. Additional test cases verify same-day resolution, multi-day resolution (exceeding 24 and 48 hours), and tickets with missing resolution timestamps.

## Out of Scope

- Changing the date string format accepted by the parser.
- Adding business hours filtering or excluding weekends and holidays.
- Modifying priority definitions or dynamic SLA configuration schemas.
- Modifying return dictionary keys or payload structure.

## Further Notes

- The expected output for the baseline sample containing tickets A, B, C, and D is:
  `{'breached': ['B', 'C'], 'average_hours': 13.0, 'counted': 3}`
