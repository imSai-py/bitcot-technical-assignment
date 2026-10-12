import {
  calculateSlaDeadline,
  checkSlaBreach,
  Ticket,
  SlaOptions,
} from '../src/index.js';

function formatDuration(ms: number): string {
  if (ms === 0) return '0 hours';
  const hours = ms / (3600 * 1000);
  return `${hours.toFixed(2)} hours (${ms.toLocaleString()} ms)`;
}

console.log('='.repeat(70));
console.log('       TYPESCRIPT SLA LIBRARY - DEMONSTRATION & MANUAL TEST       ');
console.log('='.repeat(70));

// Scenario 1: Standard Calendar Hours (Urgent Ticket)
console.log('\n--- Scenario 1: Urgent Ticket (Calendar Time, Open) ---');
const scenario1Ticket: Ticket = {
  priority: 'urgent',
  createdAt: '2026-10-12T10:00:00.000Z', // Monday 10:00 UTC
};
const scenario1CheckTime = '2026-10-12T15:30:00.000Z'; // Monday 15:30 UTC
const scenario1Result = checkSlaBreach(scenario1Ticket, {
  checkTime: scenario1CheckTime,
});

console.log(`Priority:       ${scenario1Ticket.priority} (Default: 4 hours)`);
console.log(`Created At:     ${scenario1Ticket.createdAt}`);
console.log(`Check Time:     ${scenario1CheckTime}`);
console.log(`SLA Deadline:   ${scenario1Result.deadline.toISOString()}`);
console.log(`Breached?:      ${scenario1Result.isBreached ? 'YES (BREACHED)' : 'NO'}`);
console.log(`Breach Time:    ${formatDuration(scenario1Result.breachDurationMs)}`);

// Scenario 2: Ticket Resolved Before Deadline
console.log('\n--- Scenario 2: High Ticket (Resolved In Time) ---');
const scenario2Ticket: Ticket = {
  priority: 'high',
  createdAt: '2026-10-12T09:00:00.000Z',
  resolvedAt: '2026-10-12T15:00:00.000Z', // Resolved after 6 hours (SLA is 8h)
};
const scenario2CheckTime = '2026-10-12T20:00:00.000Z'; // Checked after 11 hours
const scenario2Result = checkSlaBreach(scenario2Ticket, {
  checkTime: scenario2CheckTime,
});

console.log(`Priority:       ${scenario2Ticket.priority} (Default: 8 hours)`);
console.log(`Created At:     ${scenario2Ticket.createdAt}`);
console.log(`Resolved At:    ${scenario2Ticket.resolvedAt}`);
console.log(`Check Time:     ${scenario2CheckTime}`);
console.log(`SLA Deadline:   ${scenario2Result.deadline.toISOString()}`);
console.log(`Breached?:      ${scenario2Result.isBreached ? 'YES' : 'NO (PASSED)'}`);
console.log(`Breach Time:    ${formatDuration(scenario2Result.breachDurationMs)}`);

// Scenario 3: Business Hours with Weekend Rollover
console.log('\n--- Scenario 3: Business Hours Mode (Friday to Monday Rollover) ---');
const scenario3Ticket: Ticket = {
  priority: 'urgent', // 4 hours
  createdAt: '2026-10-16T16:00:00.000Z', // Friday 16:00 UTC (2 business hours before 18:00 close)
};
const scenario3Options: SlaOptions = {
  businessHours: true, // Monday-Friday, 09:00 to 18:00 UTC
  checkTime: '2026-10-19T10:30:00.000Z', // Monday 10:30 UTC
};
const scenario3Result = checkSlaBreach(scenario3Ticket, scenario3Options);

console.log(`Priority:       ${scenario3Ticket.priority} (4 hours)`);
console.log(`Created At:     ${scenario3Ticket.createdAt} (Friday 16:00 UTC)`);
console.log(`SLA Deadline:   ${scenario3Result.deadline.toISOString()} (Monday 11:00 UTC - skips weekend)`);
console.log(`Check Time:     ${scenario3Options.checkTime}`);
console.log(`Breached?:      ${scenario3Result.isBreached ? 'YES' : 'NO (WITHIN SLA)'}`);
console.log(`Breach Time:    ${formatDuration(scenario3Result.breachDurationMs)}`);

// Scenario 4: Off-Hours Ticket Creation (Saturday)
console.log('\n--- Scenario 4: Ticket Created on Weekend Outside Business Hours ---');
const scenario4Ticket: Ticket = {
  priority: 'high', // 8 hours
  createdAt: '2026-10-17T14:00:00.000Z', // Saturday 14:00 UTC
};
const scenario4Deadline = calculateSlaDeadline(scenario4Ticket, { businessHours: true });
console.log(`Created At:     ${scenario4Ticket.createdAt} (Saturday - Closed)`);
console.log(`SLA Starts:     2026-10-19T09:00:00.000Z (Monday 09:00 UTC)`);
console.log(`SLA Deadline:   ${scenario4Deadline.toISOString()} (Monday 17:00 UTC)`);

// Scenario 5: Business Hours with Custom Holiday Exclusion
console.log('\n--- Scenario 5: Business Hours with Holiday Exclusion ---');
const scenario5Ticket: Ticket = {
  priority: 'high', // 8 hours
  createdAt: '2026-10-12T14:00:00.000Z', // Monday 14:00 UTC
};
const scenario5Result = checkSlaBreach(scenario5Ticket, {
  businessHours: {
    holidays: ['2026-10-13'], // Tuesday 2026-10-13 is a holiday
  },
  checkTime: '2026-10-14T11:00:00.000Z', // Wednesday 11:00 UTC
});
console.log(`Created At:     ${scenario5Ticket.createdAt} (Monday 14:00 UTC)`);
console.log(`Holiday:        2026-10-13 (Tuesday)`);
console.log(`SLA Deadline:   ${scenario5Result.deadline.toISOString()} (Wednesday 13:00 UTC - Tuesday skipped)`);
console.log(`Check Time:     Wednesday 11:00 UTC`);
console.log(`Breached?:      ${scenario5Result.isBreached ? 'YES' : 'NO (WITHIN SLA)'}`);

console.log('\n' + '='.repeat(70) + '\n');
