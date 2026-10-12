import { describe, it, expect } from 'vitest';
import { calculateSlaDeadline, Priority, Ticket } from '../src/sla.js';

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
