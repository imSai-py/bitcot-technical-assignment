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

function parseAndValidateDate(value: Date | string | number, fieldName: string): Date {
  const date = value instanceof Date ? new Date(value.getTime()) : new Date(value);
  if (isNaN(date.getTime())) {
    throw new Error(`Invalid ${fieldName} date provided: ${String(value)}`);
  }
  return date;
}

function resolveTargetHours(priority: Priority, options?: SlaOptions): number {
  const targetHours =
    options?.customTargetsHours?.[priority] ?? DEFAULT_SLA_TARGET_HOURS[priority];

  if (
    targetHours === undefined ||
    typeof targetHours !== 'number' ||
    isNaN(targetHours) ||
    targetHours <= 0
  ) {
    throw new Error(`Unsupported priority: ${String(priority)}`);
  }

  return targetHours;
}

export function calculateSlaDeadline(ticket: Ticket, options?: SlaOptions): Date {
  const targetHours = resolveTargetHours(ticket.priority, options);
  const createdDate = parseAndValidateDate(ticket.createdAt, 'createdAt');
  const targetMs = targetHours * 60 * 60 * 1000;

  return new Date(createdDate.getTime() + targetMs);
}

export function checkSlaBreach(ticket: Ticket, options?: SlaOptions): SlaResult {
  const createdDate = parseAndValidateDate(ticket.createdAt, 'createdAt');
  const deadline = calculateSlaDeadline(ticket, options);
  const deadlineMs = deadline.getTime();

  let resolvedDate: Date | undefined;
  if (ticket.resolvedAt !== undefined) {
    resolvedDate = parseAndValidateDate(ticket.resolvedAt, 'resolvedAt');
    if (resolvedDate.getTime() < createdDate.getTime()) {
      throw new Error(
        `resolvedAt cannot be earlier than createdAt (${resolvedDate.toISOString()} < ${createdDate.toISOString()})`
      );
    }
  }

  const checkTime =
    options?.checkTime !== undefined
      ? parseAndValidateDate(options.checkTime, 'checkTime')
      : new Date();

  const referenceTime = resolvedDate ?? checkTime;
  const referenceMs = referenceTime.getTime();
  const isBreached = referenceMs > deadlineMs;
  const breachDurationMs = isBreached ? referenceMs - deadlineMs : 0;

  return {
    isBreached,
    breachDurationMs,
    deadline,
  };
}
