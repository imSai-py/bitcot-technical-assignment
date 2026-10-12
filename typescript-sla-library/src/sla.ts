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

export interface BusinessHoursConfig {
  startHour?: number;
  endHour?: number;
  holidays?: (Date | string | number)[];
  timezoneOffsetHours?: number;
}

export interface SlaOptions {
  customTargetsHours?: Partial<Record<Priority, number>>;
  checkTime?: Date | string | number;
  businessHours?: boolean | BusinessHoursConfig;
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

interface ResolvedBusinessHoursConfig {
  startHour: number;
  endHour: number;
  holidayStrings: Set<string>;
  timezoneOffsetMs: number;
}

function toDateString(d: Date): string {
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, '0');
  const day = String(d.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function resolveBusinessHoursConfig(
  option?: boolean | BusinessHoursConfig
): ResolvedBusinessHoursConfig | null {
  if (!option) {
    return null;
  }

  const rawConfig: BusinessHoursConfig = typeof option === 'object' ? option : {};
  const startHour = rawConfig.startHour ?? 9;
  const endHour = rawConfig.endHour ?? 18;
  const timezoneOffsetHours = rawConfig.timezoneOffsetHours ?? 0;
  const timezoneOffsetMs = timezoneOffsetHours * 60 * 60 * 1000;

  const holidayStrings = new Set<string>();
  if (rawConfig.holidays && Array.isArray(rawConfig.holidays)) {
    for (const h of rawConfig.holidays) {
      const hDate = parseAndValidateDate(h, 'holiday');
      // Adjust holiday date to local timezone perspective
      const localHDate = new Date(hDate.getTime() + timezoneOffsetMs);
      holidayStrings.add(toDateString(localHDate));
    }
  }

  return {
    startHour,
    endHour,
    holidayStrings,
    timezoneOffsetMs,
  };
}

function advanceToNextBusinessWindow(
  d: Date,
  config: ResolvedBusinessHoursConfig
): Date {
  const curr = new Date(d.getTime());

  while (true) {
    const dayOfWeek = curr.getUTCDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const isHoliday = config.holidayStrings.has(toDateString(curr));

    if (isWeekend || isHoliday) {
      curr.setUTCDate(curr.getUTCDate() + 1);
      curr.setUTCHours(0, 0, 0, 0);
      continue;
    }

    const hour = curr.getUTCHours();
    const min = curr.getUTCMinutes();
    const sec = curr.getUTCSeconds();
    const ms = curr.getUTCMilliseconds();
    const timeInHours = hour + min / 60 + sec / 3600 + ms / 3600000;

    if (timeInHours < config.startHour) {
      curr.setUTCHours(config.startHour, 0, 0, 0);
      return curr;
    } else if (timeInHours >= config.endHour) {
      curr.setUTCDate(curr.getUTCDate() + 1);
      curr.setUTCHours(0, 0, 0, 0);
      continue;
    } else {
      return curr;
    }
  }
}

function addBusinessDuration(
  start: Date,
  durationMs: number,
  config: ResolvedBusinessHoursConfig
): Date {
  // Convert UTC to local perspective
  const localStart = new Date(start.getTime() + config.timezoneOffsetMs);
  let curr = advanceToNextBusinessWindow(localStart, config);
  let remainingMs = durationMs;

  while (remainingMs > 0) {
    const endOfDay = new Date(curr.getTime());
    endOfDay.setUTCHours(config.endHour, 0, 0, 0);

    const availableMsInDay = endOfDay.getTime() - curr.getTime();

    if (remainingMs <= availableMsInDay) {
      const localResult = new Date(curr.getTime() + remainingMs);
      return new Date(localResult.getTime() - config.timezoneOffsetMs);
    } else {
      remainingMs -= availableMsInDay;
      curr = advanceToNextBusinessWindow(endOfDay, config);
    }
  }

  return new Date(curr.getTime() - config.timezoneOffsetMs);
}

function calculateBusinessDurationMs(
  from: Date,
  to: Date,
  config: ResolvedBusinessHoursConfig
): number {
  if (to.getTime() <= from.getTime()) {
    return 0;
  }

  const localFrom = new Date(from.getTime() + config.timezoneOffsetMs);
  const localTo = new Date(to.getTime() + config.timezoneOffsetMs);

  let curr = advanceToNextBusinessWindow(localFrom, config);
  if (curr.getTime() >= localTo.getTime()) {
    return 0;
  }

  let totalMs = 0;

  while (curr.getTime() < localTo.getTime()) {
    const endOfDay = new Date(curr.getTime());
    endOfDay.setUTCHours(config.endHour, 0, 0, 0);

    if (localTo.getTime() <= endOfDay.getTime()) {
      totalMs += localTo.getTime() - curr.getTime();
      break;
    } else {
      totalMs += endOfDay.getTime() - curr.getTime();
      curr = advanceToNextBusinessWindow(endOfDay, config);
    }
  }

  return totalMs;
}

export function calculateSlaDeadline(ticket: Ticket, options?: SlaOptions): Date {
  const targetHours = resolveTargetHours(ticket.priority, options);
  const createdDate = parseAndValidateDate(ticket.createdAt, 'createdAt');
  const targetMs = targetHours * 60 * 60 * 1000;

  const bhConfig = resolveBusinessHoursConfig(options?.businessHours);
  if (bhConfig) {
    return addBusinessDuration(createdDate, targetMs, bhConfig);
  }

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

  const bhConfig = resolveBusinessHoursConfig(options?.businessHours);
  let breachDurationMs = 0;
  if (isBreached) {
    if (bhConfig) {
      breachDurationMs = calculateBusinessDurationMs(deadline, referenceTime, bhConfig);
    } else {
      breachDurationMs = referenceMs - deadlineMs;
    }
  }

  return {
    isBreached,
    breachDurationMs,
    deadline,
  };
}
