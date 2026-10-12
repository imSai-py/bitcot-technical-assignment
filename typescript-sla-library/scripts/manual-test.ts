import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import {
  checkSlaBreach,
  calculateSlaDeadline,
  Priority,
  Ticket,
  SlaOptions,
  VALID_PRIORITIES,
} from '../src/index.js';

async function main() {
  const rl = readline.createInterface({ input, output });

  console.log('='.repeat(60));
  console.log('     INTERACTIVE MANUAL TESTING - TYPESCRIPT SLA LIBRARY    ');
  console.log('='.repeat(60));
  console.log('Press Ctrl+C at any prompt to exit.\n');

  try {
    while (true) {
      console.log('--- Enter Ticket Details ---');
      const priorityInput = (
        await rl.question('1. Priority (urgent / high / normal / low) [default: urgent]: ')
      ).trim().toLowerCase() || 'urgent';

      if (!VALID_PRIORITIES.includes(priorityInput as Priority)) {
        console.log(`[Error] Invalid priority: "${priorityInput}". Allowed: ${VALID_PRIORITIES.join(', ')}\n`);
        continue;
      }
      const priority = priorityInput as Priority;

      const defaultCreated = new Date().toISOString();
      const createdInput = (
        await rl.question(`2. Created At (ISO string or press Enter for now [${defaultCreated}]): `)
      ).trim() || defaultCreated;

      const resolvedInput = (
        await rl.question('3. Resolved At (ISO string or press Enter if unresolved): ')
      ).trim();

      const defaultCheck = new Date().toISOString();
      const checkInput = (
        await rl.question(`4. Check Time (ISO string or press Enter for now [${defaultCheck}]): `)
      ).trim() || defaultCheck;

      const bhInput = (
        await rl.question('5. Enable Business Hours (09:00 - 18:00 Mon-Fri)? (y/N): ')
      ).trim().toLowerCase();
      const useBusinessHours = bhInput === 'y' || bhInput === 'yes';

      let holidays: string[] | undefined = undefined;
      let timezone: string | undefined = undefined;

      if (useBusinessHours) {
        const holInput = (
          await rl.question('   Holidays comma-separated (e.g. 2026-10-13, 2026-12-25 or Enter for none): ')
        ).trim();
        if (holInput) {
          holidays = holInput.split(',').map((h) => h.trim()).filter(Boolean);
        }

        const tzInput = (
          await rl.question('   IANA Timezone (e.g. UTC, America/New_York or Enter for UTC): ')
        ).trim();
        if (tzInput) {
          timezone = tzInput;
        }
      }

      const ticket: Ticket = {
        priority,
        createdAt: createdInput,
        resolvedAt: resolvedInput || undefined,
      };

      const options: SlaOptions = {
        checkTime: checkInput,
        businessHours: useBusinessHours
          ? {
              holidays,
              timezone: timezone || undefined,
            }
          : false,
      };

      try {
        const deadline = calculateSlaDeadline(ticket, options);
        const result = checkSlaBreach(ticket, options);

        console.log('\n--- Calculation Result ---');
        console.log(`Ticket Priority:   ${ticket.priority}`);
        console.log(`Created At:        ${new Date(ticket.createdAt).toISOString()}`);
        if (ticket.resolvedAt) {
          console.log(`Resolved At:       ${new Date(ticket.resolvedAt).toISOString()}`);
        }
        console.log(`Evaluated At:      ${new Date(options.checkTime!).toISOString()}`);
        console.log(`Business Hours:    ${useBusinessHours ? 'ENABLED (09:00-18:00)' : 'DISABLED (24/7 calendar)'}`);
        if (timezone) console.log(`Timezone:          ${timezone}`);
        if (holidays?.length) console.log(`Holidays:          ${holidays.join(', ')}`);
        console.log(`SLA Deadline:      ${deadline.toISOString()}`);
        console.log(`Breached?:         ${result.isBreached ? '>> YES (BREACHED) <<' : '>> NO (WITHIN SLA) <<'}`);
        console.log(`Breach Duration:   ${result.breachDurationMs / (3600 * 1000)} hours (${result.breachDurationMs.toLocaleString()} ms)`);
        console.log('--------------------------\n');
      } catch (err: unknown) {
        console.error(`\n[Execution Error] ${(err as Error).message}\n`);
      }

      const again = (await rl.question('Test another ticket? (Y/n): ')).trim().toLowerCase();
      if (again === 'n' || again === 'no') {
        break;
      }
      console.log('\n');
    }
  } finally {
    rl.close();
  }

  console.log('\nTesting session ended.');
}

main().catch(console.error);
