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
  // Urgent: deadline is 14:00:00.000Z (4 hours)
  const ticket: Ticket = {
    priority: 'urgent',
    createdAt: baseDate,
  };

  it('returns not breached when checked before deadline', () => {
    const checkTime = new Date('2026-10-12T13:00:00.000Z'); // 3 hours in
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
    const checkTime = new Date('2026-10-12T15:30:00.000Z'); // 1.5 hours past deadline
    const result = checkSlaBreach(ticket, { checkTime });

    expect(result.isBreached).toBe(true);
    expect(result.breachDurationMs).toBe(1.5 * 60 * 60 * 1000); // 5400000 ms
    expect(result.deadline.toISOString()).toBe('2026-10-12T14:00:00.000Z');
  });

  it('returns not breached for ticket resolved before deadline even if check time is late', () => {
    const resolvedTicket: Ticket = {
      ...ticket,
      resolvedAt: new Date('2026-10-12T13:30:00.000Z'),
    };
    const checkTime = new Date('2026-10-12T18:00:00.000Z'); // Checked way after deadline
    const result = checkSlaBreach(resolvedTicket, { checkTime });

    expect(result.isBreached).toBe(false);
    expect(result.breachDurationMs).toBe(0);
  });

  it('returns breached for ticket resolved after deadline with duration measured to resolvedAt', () => {
    const resolvedTicket: Ticket = {
      ...ticket,
      resolvedAt: new Date('2026-10-12T15:00:00.000Z'), // 1 hour past deadline
    };
    const checkTime = new Date('2026-10-12T20:00:00.000Z'); // 6 hours past deadline
    const result = checkSlaBreach(resolvedTicket, { checkTime });

    expect(result.isBreached).toBe(true);
    expect(result.breachDurationMs).toBe(1 * 60 * 60 * 1000); // Measured to resolvedAt, not checkTime
  });

  describe('Default checkTime behavior', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('defaults checkTime to current time (Date.now) when omitted', () => {
      vi.setSystemTime(new Date('2026-10-12T16:00:00.000Z')); // 2 hours past deadline
      const result = checkSlaBreach(ticket);

      expect(result.isBreached).toBe(true);
      expect(result.breachDurationMs).toBe(2 * 60 * 60 * 1000);
    });
  });

  it('supports custom priority targets via options', () => {
    const options: SlaOptions = {
      customTargetsHours: {
        urgent: 2, // Override urgent to 2 hours
      },
      checkTime: new Date('2026-10-12T12:30:00.000Z'), // 2.5 hours in
    };
    const result = checkSlaBreach(ticket, options);

    expect(result.deadline.toISOString()).toBe('2026-10-12T12:00:00.000Z');
    expect(result.isBreached).toBe(true);
    expect(result.breachDurationMs).toBe(0.5 * 60 * 60 * 1000); // 30 minutes breached
  });
});
