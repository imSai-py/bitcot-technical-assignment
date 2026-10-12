import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  calculateSlaDeadline,
  checkSlaBreach,
  Priority,
  Ticket,
  SlaOptions,
} from '../src/sla.js';

describe('Ticket 01: Core SLA Deadline Calculation', () => {
  const baseDate = new Date('2026-10-12T10:00:00.000Z');

  it('calculates deadline for urgent priority (4 hours)', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: baseDate,
    };
    const deadline = calculateSlaDeadline(ticket);
    expect(deadline.toISOString()).toBe('2026-10-12T14:00:00.000Z');
  });

  it('calculates deadline for high priority (8 hours)', () => {
    const ticket: Ticket = {
      priority: 'high',
      createdAt: baseDate,
    };
    const deadline = calculateSlaDeadline(ticket);
    expect(deadline.toISOString()).toBe('2026-10-12T18:00:00.000Z');
  });

  it('calculates deadline for normal priority (24 hours)', () => {
    const ticket: Ticket = {
      priority: 'normal',
      createdAt: baseDate,
    };
    const deadline = calculateSlaDeadline(ticket);
    expect(deadline.toISOString()).toBe('2026-10-13T10:00:00.000Z');
  });

  it('calculates deadline for low priority (72 hours)', () => {
    const ticket: Ticket = {
      priority: 'low',
      createdAt: baseDate,
    };
    const deadline = calculateSlaDeadline(ticket);
    expect(deadline.toISOString()).toBe('2026-10-15T10:00:00.000Z');
  });
});

describe('Ticket 02: SLA Breach Detection and Target Overrides', () => {
  const baseDate = new Date('2026-10-12T10:00:00.000Z');
  const ticket: Ticket = {
    priority: 'urgent',
    createdAt: baseDate,
  };

  it('returns not breached when checked before deadline', () => {
    const checkTime = new Date('2026-10-12T13:00:00.000Z');
    const result = checkSlaBreach(ticket, { checkTime });

    expect(result.isBreached).toBe(false);
    expect(result.breachDurationMs).toBe(0);
    expect(result.deadline.toISOString()).toBe('2026-10-12T14:00:00.000Z');
  });

  it('returns not breached when checked exactly at deadline', () => {
    const checkTime = new Date('2026-10-12T14:00:00.000Z');
    const result = checkSlaBreach(ticket, { checkTime });

    expect(result.isBreached).toBe(false);
    expect(result.breachDurationMs).toBe(0);
    expect(result.deadline.toISOString()).toBe('2026-10-12T14:00:00.000Z');
  });

  it('returns breached with correct duration when checked after deadline', () => {
    const checkTime = new Date('2026-10-12T15:30:00.000Z');
    const result = checkSlaBreach(ticket, { checkTime });

    expect(result.isBreached).toBe(true);
    expect(result.breachDurationMs).toBe(1.5 * 60 * 60 * 1000);
    expect(result.deadline.toISOString()).toBe('2026-10-12T14:00:00.000Z');
  });

  it('returns not breached for ticket resolved before deadline even if check time is late', () => {
    const resolvedTicket: Ticket = {
      ...ticket,
      resolvedAt: new Date('2026-10-12T13:30:00.000Z'),
    };
    const checkTime = new Date('2026-10-12T18:00:00.000Z');
    const result = checkSlaBreach(resolvedTicket, { checkTime });

    expect(result.isBreached).toBe(false);
    expect(result.breachDurationMs).toBe(0);
  });

  it('returns breached for ticket resolved after deadline with duration measured to resolvedAt', () => {
    const resolvedTicket: Ticket = {
      ...ticket,
      resolvedAt: new Date('2026-10-12T15:00:00.000Z'),
    };
    const checkTime = new Date('2026-10-12T20:00:00.000Z');
    const result = checkSlaBreach(resolvedTicket, { checkTime });

    expect(result.isBreached).toBe(true);
    expect(result.breachDurationMs).toBe(1 * 60 * 60 * 1000);
  });

  describe('Default checkTime behavior', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('defaults checkTime to current time (Date.now) when omitted', () => {
      vi.setSystemTime(new Date('2026-10-12T16:00:00.000Z'));
      const result = checkSlaBreach(ticket);

      expect(result.isBreached).toBe(true);
      expect(result.breachDurationMs).toBe(2 * 60 * 60 * 1000);
    });
  });

  it('supports custom priority targets via options', () => {
    const options: SlaOptions = {
      customTargetsHours: {
        urgent: 2,
      },
      checkTime: new Date('2026-10-12T12:30:00.000Z'),
    };
    const result = checkSlaBreach(ticket, options);

    expect(result.deadline.toISOString()).toBe('2026-10-12T12:00:00.000Z');
    expect(result.isBreached).toBe(true);
    expect(result.breachDurationMs).toBe(0.5 * 60 * 60 * 1000);
  });
});

describe('Ticket 03: Timestamp Normalization and Input Validation', () => {
  it('accepts ISO 8601 strings, epoch timestamps, and Date instances', () => {
    const isoTicket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-12T10:00:00.000Z',
      resolvedAt: '2026-10-12T13:00:00.000Z',
    };
    const resultIso = checkSlaBreach(isoTicket, {
      checkTime: '2026-10-12T15:00:00.000Z',
    });
    expect(resultIso.isBreached).toBe(false);

    const epochTicket: Ticket = {
      priority: 'high',
      createdAt: 1791804000000,
    };
    const resultEpoch = checkSlaBreach(epochTicket, {
      checkTime: 1791804000000 + 10 * 3600 * 1000,
    });
    expect(resultEpoch.isBreached).toBe(true);
  });

  it('throws descriptive error on invalid createdAt timestamp', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: 'not-a-valid-date',
    };
    expect(() => calculateSlaDeadline(ticket)).toThrow(/Invalid createdAt date/i);
    expect(() => checkSlaBreach(ticket)).toThrow(/Invalid createdAt date/i);
  });

  it('throws descriptive error on invalid resolvedAt timestamp', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: new Date('2026-10-12T10:00:00Z'),
      resolvedAt: 'invalid-resolved-date',
    };
    expect(() => checkSlaBreach(ticket)).toThrow(/Invalid resolvedAt date/i);
  });

  it('throws descriptive error on invalid checkTime', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: new Date('2026-10-12T10:00:00Z'),
    };
    expect(() =>
      checkSlaBreach(ticket, { checkTime: 'not-a-date' })
    ).toThrow(/Invalid checkTime/i);
  });

  it('throws descriptive error on unknown priority', () => {
    const ticket = {
      priority: 'critical' as unknown as Priority,
      createdAt: new Date('2026-10-12T10:00:00Z'),
    };
    expect(() => calculateSlaDeadline(ticket)).toThrow(/Unsupported priority: critical/i);
  });

  it('throws descriptive error when resolvedAt is earlier than createdAt', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: new Date('2026-10-12T10:00:00Z'),
      resolvedAt: new Date('2026-10-12T09:00:00Z'),
    };
    expect(() => checkSlaBreach(ticket)).toThrow(/resolvedAt cannot be earlier than createdAt/i);
  });
});

describe('Ticket 04: Business Hours Calculation Engine', () => {
  // 2026-10-12 is a Monday
  it('calculates deadline within the same business day', () => {
    const ticket: Ticket = {
      priority: 'urgent', // 4 hours
      createdAt: '2026-10-12T10:00:00.000Z', // Monday 10:00 UTC
    };
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    // 10:00 + 4 hours = 14:00 (within 09:00-18:00 window)
    expect(deadline.toISOString()).toBe('2026-10-12T14:00:00.000Z');
  });

  it('pauses overnight and resumes at 09:00 next business day', () => {
    const ticket: Ticket = {
      priority: 'high', // 8 hours
      createdAt: '2026-10-12T14:00:00.000Z', // Monday 14:00 UTC
    };
    // Monday 14:00 to 18:00 = 4 hours consumed.
    // 4 hours remaining resumes Tuesday 09:00 UTC -> deadline 13:00 UTC Tuesday.
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-13T13:00:00.000Z');
  });

  it('skips weekends for tickets spanning Friday to Monday', () => {
    // 2026-10-16 is a Friday
    const ticket: Ticket = {
      priority: 'urgent', // 4 hours
      createdAt: '2026-10-16T16:00:00.000Z', // Friday 16:00 UTC
    };
    // Friday 16:00 to 18:00 = 2 hours consumed.
    // 2 hours remaining skips Sat 10-17 and Sun 10-18 -> resumes Monday 2026-10-19 09:00 UTC.
    // Monday 09:00 + 2 hours = Monday 11:00 UTC.
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-19T11:00:00.000Z');
  });

  it('advances start time when ticket is created outside business hours on a weekday evening', () => {
    const ticket: Ticket = {
      priority: 'urgent', // 4 hours
      createdAt: '2026-10-13T20:00:00.000Z', // Tuesday 20:00 UTC
    };
    // Starts Wednesday 2026-10-14 at 09:00 UTC.
    // 09:00 + 4 hours = Wednesday 13:00 UTC.
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-14T13:00:00.000Z');
  });

  it('advances start time when ticket is created outside business hours on a weekday morning', () => {
    const ticket: Ticket = {
      priority: 'urgent', // 4 hours
      createdAt: '2026-10-14T06:30:00.000Z', // Wednesday 06:30 UTC
    };
    // Starts Wednesday 2026-10-14 at 09:00 UTC.
    // 09:00 + 4 hours = Wednesday 13:00 UTC.
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-14T13:00:00.000Z');
  });

  it('advances start time when ticket is created on a weekend', () => {
    // 2026-10-17 is a Saturday
    const ticket: Ticket = {
      priority: 'high', // 8 hours
      createdAt: '2026-10-17T14:00:00.000Z', // Saturday 14:00 UTC
    };
    // Starts Monday 2026-10-19 at 09:00 UTC.
    // 09:00 + 8 hours = Monday 17:00 UTC.
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-19T17:00:00.000Z');
  });

  it('calculates multi-day business hours deadline (normal: 24h = 2 full days + 6h)', () => {
    const ticket: Ticket = {
      priority: 'normal', // 24 hours
      createdAt: '2026-10-12T09:00:00.000Z', // Monday 09:00 UTC
    };
    // Day 1 (Mon): 9 hours (15h remaining)
    // Day 2 (Tue): 9 hours (6h remaining)
    // Day 3 (Wed): 09:00 + 6h = 15:00 UTC
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-14T15:00:00.000Z');
  });

  it('calculates breach status and active business duration when breached', () => {
    const ticket: Ticket = {
      priority: 'urgent', // 4 hours
      createdAt: '2026-10-12T10:00:00.000Z', // Monday 10:00 UTC, deadline 14:00 UTC
    };

    // Checked Monday at 16:30 UTC (2.5 business hours past 14:00 deadline)
    const result = checkSlaBreach(ticket, {
      businessHours: true,
      checkTime: '2026-10-12T16:30:00.000Z',
    });
    expect(result.isBreached).toBe(true);
    expect(result.breachDurationMs).toBe(2.5 * 60 * 60 * 1000);

    // Checked next day Tuesday at 10:00 UTC:
    // From Mon 14:00 deadline to Mon 18:00 = 4 business hours
    // Overnight pause (18:00 to 09:00) = 0 business hours
    // Tuesday 09:00 to 10:00 = 1 business hour
    // Total breach duration = 5 business hours = 18,000,000 ms
    const nextDayResult = checkSlaBreach(ticket, {
      businessHours: true,
      checkTime: '2026-10-13T10:00:00.000Z',
    });
    expect(nextDayResult.isBreached).toBe(true);
    expect(nextDayResult.breachDurationMs).toBe(5 * 60 * 60 * 1000);
  });
});
