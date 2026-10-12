export type Priority = 'urgent' | 'high' | 'normal' | 'low';

export interface Ticket {
  priority: Priority;
  createdAt: Date | string | number;
  resolvedAt?: Date | string | number;
}

export interface SlaResult {
  isBreached: boolean;
  breachDurationMs: number;
  deadline: Date;
}

export interface SlaOptions {
  customTargetsHours?: Partial<Record<Priority, number>>;
  checkTime?: Date | string | number;
  businessHours?: boolean;
}

export const DEFAULT_SLA_TARGET_HOURS: Record<Priority, number> = {
  urgent: 4,
  high: 8,
  normal: 24,
  low: 72,
};

export function calculateSlaDeadline(ticket: Ticket, options?: SlaOptions): Date {
  const targetHours =
    options?.customTargetsHours?.[ticket.priority] ??
    DEFAULT_SLA_TARGET_HOURS[ticket.priority];

  const createdTime = new Date(ticket.createdAt).getTime();
  const targetMs = targetHours * 60 * 60 * 1000;

  return new Date(createdTime + targetMs);
}
