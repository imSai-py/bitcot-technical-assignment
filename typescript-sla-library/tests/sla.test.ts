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
  // 2026-10-12 is Monday
  it('calculates deadline within the same business day', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-12T10:00:00.000Z',
    };
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-12T14:00:00.000Z');
  });

  it('pauses overnight and resumes at 09:00 next business day', () => {
    const ticket: Ticket = {
      priority: 'high',
      createdAt: '2026-10-12T14:00:00.000Z',
    };
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-13T13:00:00.000Z');
  });

  it('skips weekends for tickets spanning Friday to Monday', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-16T16:00:00.000Z',
    };
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-19T11:00:00.000Z');
  });

  it('advances start time when ticket is created outside business hours on a weekday evening', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-13T20:00:00.000Z',
    };
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-14T13:00:00.000Z');
  });

  it('advances start time when ticket is created outside business hours on a weekday morning', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-14T06:30:00.000Z',
    };
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-14T13:00:00.000Z');
  });

  it('advances start time when ticket is created on a weekend', () => {
    const ticket: Ticket = {
      priority: 'high',
      createdAt: '2026-10-17T14:00:00.000Z',
    };
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-19T17:00:00.000Z');
  });

  it('calculates multi-day business hours deadline (normal: 24h = 2 full days + 6h)', () => {
    const ticket: Ticket = {
      priority: 'normal',
      createdAt: '2026-10-12T09:00:00.000Z',
    };
    const deadline = calculateSlaDeadline(ticket, { businessHours: true });
    expect(deadline.toISOString()).toBe('2026-10-14T15:00:00.000Z');
  });

  it('calculates breach status and active business duration when breached', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-12T10:00:00.000Z',
    };

    const result = checkSlaBreach(ticket, {
      businessHours: true,
      checkTime: '2026-10-12T16:30:00.000Z',
    });
    expect(result.isBreached).toBe(true);
    expect(result.breachDurationMs).toBe(2.5 * 60 * 60 * 1000);

    const nextDayResult = checkSlaBreach(ticket, {
      businessHours: true,
      checkTime: '2026-10-13T10:00:00.000Z',
    });
    expect(nextDayResult.isBreached).toBe(true);
    expect(nextDayResult.breachDurationMs).toBe(5 * 60 * 60 * 1000);
  });
});

describe('Ticket 05: Holiday Exclusion and Timezone Configuration', () => {
  it('skips designated holidays during deadline calculation', () => {
    // 2026-10-12 is Monday.
    // 2026-10-13 is Tuesday (designated as holiday).
    const ticket: Ticket = {
      priority: 'high', // 8 hours
      createdAt: '2026-10-12T14:00:00.000Z', // Monday 14:00 UTC
    };

    // Monday 14:00 to 18:00 = 4 hours.
    // Tuesday 2026-10-13 is a holiday -> skipped entirely.
    // Remaining 4 hours resumes Wednesday 2026-10-14 at 09:00 UTC -> deadline 13:00 UTC Wednesday.
    const deadline = calculateSlaDeadline(ticket, {
      businessHours: {
        holidays: ['2026-10-13'],
      },
    });

    expect(deadline.toISOString()).toBe('2026-10-14T13:00:00.000Z');
  });

  it('advances start time when ticket is created on a holiday', () => {
    // 2026-10-13 is Tuesday (holiday).
    const ticket: Ticket = {
      priority: 'urgent', // 4 hours
      createdAt: '2026-10-13T11:00:00.000Z', // Tuesday 11:00 UTC (holiday)
    };

    // Advances to Wednesday 2026-10-14 09:00 UTC.
    // 09:00 + 4 hours = Wednesday 13:00 UTC.
    const deadline = calculateSlaDeadline(ticket, {
      businessHours: {
        holidays: ['2026-10-13'],
      },
    });

    expect(deadline.toISOString()).toBe('2026-10-14T13:00:00.000Z');
  });

  it('skips holiday when calculating active breach duration', () => {
    // Ticket deadline is Monday 2026-10-12 18:00 UTC.
    // Tuesday 2026-10-13 is a holiday.
    // Checked Wednesday 2026-10-14 11:00 UTC.
    // Business duration past deadline:
    // Mon 18:00 to Wed 09:00 (Tuesday was holiday) = 0 hours.
    // Wed 09:00 to 11:00 = 2 business hours.
    const ticket: Ticket = {
      priority: 'urgent', // 4 hours
      createdAt: '2026-10-12T14:00:00.000Z', // deadline: 18:00 UTC Monday
    };

    const result = checkSlaBreach(ticket, {
      businessHours: {
        holidays: [new Date('2026-10-13T00:00:00.000Z')],
      },
      checkTime: '2026-10-14T11:00:00.000Z',
    });

    expect(result.isBreached).toBe(true);
    expect(result.breachDurationMs).toBe(2 * 60 * 60 * 1000);
  });

  it('supports custom timezone offset (+2 hours)', () => {
    // Offset +2 hours:
    // Local business hours: 09:00 - 18:00 local = 07:00 - 16:00 UTC.
    // Created Monday 2026-10-12 at 14:00 UTC (16:00 local).
    // Today has 2 business hours left (until 16:00 UTC / 18:00 local).
    // High priority (8 hours):
    // 2 hours consumed Monday.
    // 6 hours remaining resumes Tuesday 07:00 UTC (09:00 local).
    // 07:00 + 6 hours = 13:00 UTC (15:00 local).
    const ticket: Ticket = {
      priority: 'high', // 8 hours
      createdAt: '2026-10-12T14:00:00.000Z',
    };

    const deadline = calculateSlaDeadline(ticket, {
      businessHours: {
        timezoneOffsetHours: 2,
      },
    });

    expect(deadline.toISOString()).toBe('2026-10-13T13:00:00.000Z');
  });

  it('supports negative timezone offset (-5 hours, e.g. EST)', () => {
    // Offset -5 hours:
    // Local business hours: 09:00 - 18:00 local = 14:00 - 23:00 UTC.
    // Created Monday 2026-10-12 at 15:00 UTC (10:00 local).
    // Urgent priority (4 hours):
    // 10:00 local + 4 hours = 14:00 local (19:00 UTC).
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-12T15:00:00.000Z',
    };

    const deadline = calculateSlaDeadline(ticket, {
      businessHours: {
        timezoneOffsetHours: -5,
      },
    });

    expect(deadline.toISOString()).toBe('2026-10-12T19:00:00.000Z');
  });

  it('throws error on invalid timezoneOffsetHours out of range', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-12T15:00:00.000Z',
    };

    expect(() =>
      calculateSlaDeadline(ticket, {
        businessHours: {
          timezoneOffsetHours: 25,
        },
      })
    ).toThrow(/Invalid timezoneOffsetHours/i);
  });

  it('supports IANA timezone strings', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-12T10:00:00.000Z',
    };

    const deadlineUtc = calculateSlaDeadline(ticket, {
      businessHours: {
        timezone: 'UTC',
      },
    });
    expect(deadlineUtc.toISOString()).toBe('2026-10-12T14:00:00.000Z');
  });

  it('throws error on invalid IANA timezone string', () => {
    const ticket: Ticket = {
      priority: 'urgent',
      createdAt: '2026-10-12T10:00:00.000Z',
    };

    expect(() =>
      calculateSlaDeadline(ticket, {
        businessHours: {
          timezone: 'Invalid/City_Name',
        },
      })
    ).toThrow(/Invalid timezone specified/i);
  });

  it('rejects unknown priority even when passed in customTargetsHours', () => {
    const ticket = {
      priority: 'critical' as unknown as Priority,
      createdAt: '2026-10-12T10:00:00.000Z',
    };

    expect(() =>
      calculateSlaDeadline(ticket, {
        customTargetsHours: {
          critical: 2,
        } as unknown as Partial<Record<Priority, number>>,
      })
    ).toThrow(/Unsupported priority: critical/i);
  });
});
