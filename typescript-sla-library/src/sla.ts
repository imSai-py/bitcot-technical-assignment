export type Priority = 'urgent' | 'high' | 'normal' | 'low';

export const VALID_PRIORITIES: readonly Priority[] = ['urgent', 'high', 'normal', 'low'] as const;

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
  holidays?: (Date | string | number)[];
  timezone?: string;
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

const BUSINESS_START_HOUR = 9;
const BUSINESS_END_HOUR = 18;

function parseAndValidateDate(value: Date | string | number, fieldName: string): Date {
  const date = value instanceof Date ? new Date(value.getTime()) : new Date(value);
  if (isNaN(date.getTime())) {
    throw new Error(`Invalid ${fieldName} date provided: ${String(value)}`);
  }
  return date;
}

function resolveTargetHours(priority: Priority, options?: SlaOptions): number {
  if (!VALID_PRIORITIES.includes(priority)) {
    throw new Error(`Unsupported priority: ${String(priority)}`);
  }

  const targetHours =
    options?.customTargetsHours?.[priority] ?? DEFAULT_SLA_TARGET_HOURS[priority];

  if (
    targetHours === undefined ||
    typeof targetHours !== 'number' ||
    isNaN(targetHours) ||
    targetHours <= 0
  ) {
    throw new Error(`Invalid target hours for priority '${String(priority)}': ${String(targetHours)}`);
  }

  return targetHours;
}

interface ResolvedBusinessHoursConfig {
  holidayStrings: Set<string>;
  timezoneOffsetMs: number;
}

function toDateString(d: Date): string {
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, '0');
  const day = String(d.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function getEndOfBusinessDay(d: Date): Date {
  const endOfDay = new Date(d.getTime());
  endOfDay.setUTCHours(BUSINESS_END_HOUR, 0, 0, 0);
  return endOfDay;
}

function getIanaTimezoneOffsetHours(timeZone: string, refDate: Date = new Date()): number {
  try {
    const formatter = new Intl.DateTimeFormat('en-US', {
      timeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
    const parts = formatter.formatToParts(refDate);
    const getPart = (type: string) => Number(parts.find(p => p.type === type)?.value);
    const year = getPart('year');
    const month = getPart('month');
    const day = getPart('day');
    const rawHour = getPart('hour');
    const hour = rawHour === 24 ? 0 : rawHour;
    const minute = getPart('minute');
    const second = getPart('second');

    const localUtcMs = Date.UTC(year, month - 1, day, hour, minute, second);
    const actualUtcMs = Date.UTC(
      refDate.getUTCFullYear(),
      refDate.getUTCMonth(),
      refDate.getUTCDate(),
      refDate.getUTCHours(),
      refDate.getUTCMinutes(),
      refDate.getUTCSeconds()
    );

    return (localUtcMs - actualUtcMs) / (3600 * 1000);
  } catch {
    throw new Error(`Invalid timezone specified: ${timeZone}`);
  }
}

function resolveBusinessHoursConfig(
  option?: boolean | BusinessHoursConfig
): ResolvedBusinessHoursConfig | null {
  if (!option) {
    return null;
  }

  const rawConfig: BusinessHoursConfig = typeof option === 'object' ? option : {};

  let timezoneOffsetHours = 0;
  if (rawConfig.timezone !== undefined) {
    timezoneOffsetHours = getIanaTimezoneOffsetHours(rawConfig.timezone);
  } else if (rawConfig.timezoneOffsetHours !== undefined) {
    if (
      !Number.isFinite(rawConfig.timezoneOffsetHours) ||
      Math.abs(rawConfig.timezoneOffsetHours) > 14
    ) {
      throw new Error(
        `Invalid timezoneOffsetHours: ${String(rawConfig.timezoneOffsetHours)}. Must be a finite number between -14 and 14.`
      );
    }
    timezoneOffsetHours = rawConfig.timezoneOffsetHours;
  }

  const timezoneOffsetMs = timezoneOffsetHours * 60 * 60 * 1000;

  const holidayStrings = new Set<string>();
  if (rawConfig.holidays && Array.isArray(rawConfig.holidays)) {
    for (const rawHoliday of rawConfig.holidays) {
      if (typeof rawHoliday === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(rawHoliday.trim())) {
        holidayStrings.add(rawHoliday.trim());
      } else {
        const holidayDate = parseAndValidateDate(rawHoliday, 'holiday');
        holidayStrings.add(toDateString(holidayDate));
      }
    }
  }

  return {
    holidayStrings,
    timezoneOffsetMs,
  };
}

function advanceToNextBusinessWindow(
  date: Date,
  config: ResolvedBusinessHoursConfig
): Date {
  const currentDate = new Date(date.getTime());

  while (true) {
    const dayOfWeek = currentDate.getUTCDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const isHoliday = config.holidayStrings.has(toDateString(currentDate));

    if (isWeekend || isHoliday) {
      currentDate.setUTCDate(currentDate.getUTCDate() + 1);
      currentDate.setUTCHours(0, 0, 0, 0);
      continue;
    }

    const hour = currentDate.getUTCHours();
    const min = currentDate.getUTCMinutes();
    const sec = currentDate.getUTCSeconds();
    const ms = currentDate.getUTCMilliseconds();
    const timeInHours = hour + min / 60 + sec / 3600 + ms / 3600000;

    if (timeInHours < BUSINESS_START_HOUR) {
      currentDate.setUTCHours(BUSINESS_START_HOUR, 0, 0, 0);
      return currentDate;
    } else if (timeInHours >= BUSINESS_END_HOUR) {
      currentDate.setUTCDate(currentDate.getUTCDate() + 1);
      currentDate.setUTCHours(0, 0, 0, 0);
      continue;
    } else {
      return currentDate;
    }
  }
}

function addBusinessDuration(
  start: Date,
  durationMs: number,
  config: ResolvedBusinessHoursConfig
): Date {
  const localStart = new Date(start.getTime() + config.timezoneOffsetMs);
  let currentDate = advanceToNextBusinessWindow(localStart, config);
  let remainingMs = durationMs;

  while (remainingMs > 0) {
    const endOfDay = getEndOfBusinessDay(currentDate);
    const availableMsInDay = endOfDay.getTime() - currentDate.getTime();

    if (remainingMs <= availableMsInDay) {
      const localResult = new Date(currentDate.getTime() + remainingMs);
      return new Date(localResult.getTime() - config.timezoneOffsetMs);
    } else {
      remainingMs -= availableMsInDay;
      currentDate = advanceToNextBusinessWindow(endOfDay, config);
    }
  }

  return new Date(currentDate.getTime() - config.timezoneOffsetMs);
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

  let currentDate = advanceToNextBusinessWindow(localFrom, config);
  if (currentDate.getTime() >= localTo.getTime()) {
    return 0;
  }

  let totalMs = 0;

  while (currentDate.getTime() < localTo.getTime()) {
    const endOfDay = getEndOfBusinessDay(currentDate);

    if (localTo.getTime() <= endOfDay.getTime()) {
      totalMs += localTo.getTime() - currentDate.getTime();
      break;
    } else {
      totalMs += endOfDay.getTime() - currentDate.getTime();
      currentDate = advanceToNextBusinessWindow(endOfDay, config);
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
