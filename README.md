# Bitcot Technical Assignment: Unified Monorepo

This repository contains the consolidated solutions for all three technical assignment components:

1. **`debug-warmup/`**: Python SLA breach duration bugfix and investigation notes.
2. **`python-ticket-summary/`**: Standalone Python CLI ticket summary tool and test suite.
3. **`typescript-sla-library/`**: Typed TypeScript SLA deadline and breach calculation engine with business hours support.

All original pre-merge directories have been preserved in `_backup/` for reference and verification.

---

## Directory Structure

```text
bitcot-technical-assignment/
├── _backup/                           # Preserved original folders before deduplication
│   ├── Debug warm-up/
│   ├── Python-ticket-summary-tool/
│   └── TypeScript-SLA-library/
├── debug-warmup/                      # Part 1: Debug Warm-Up
│   ├── debug_warmup.py
│   ├── pytest.ini
│   ├── README.md
│   └── tests/
│       └── test_debug_warmup.py
├── python-ticket-summary/             # Part 2: Python Ticket Summary CLI
│   ├── ticket_summary.py
│   ├── tickets.csv
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│       └── test_ticket_summary.py
├── typescript-sla-library/            # Part 3: TypeScript SLA Library
│   ├── src/
│   │   ├── index.ts
│   │   └── sla.ts
│   ├── tests/
│   │   └── sla.test.ts
│   ├── scripts/
│   │   ├── demo.ts
│   │   └── manual-test.ts
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   └── README.md
├── docs/                              # Shared documentation
│   └── agents/
│       ├── domain.md
│       ├── issue-tracker.md
│       └── triage-labels.md
├── .scratch/                          # Unified specifications and issues
│   ├── debug-warmup/
│   ├── ticket-summary/
│   └── typescript-sla-library/
├── .agents/                           # Agent definitions and skills
├── AGENTS.md
├── GEMINI.md
├── TASK.md                            # Comprehensive task specifications & notes
└── README.md                          # Repository guide (this file)
```

---

## Running the Tests

### 1. Debug Warm-Up
```bash
cd debug-warmup
python -m pytest tests
```
Runs 6 unit tests confirming the multi-day resolution duration calculation fix.

### 2. Python Ticket Summary Tool
```bash
cd python-ticket-summary
python -m pytest tests
```
Runs 11 integration tests covering CLI invocation, edge cases, whitespace handling, and JSON output.

To run the CLI tool directly:
```bash
cd python-ticket-summary
python ticket_summary.py tickets.csv
python ticket_summary.py tickets.csv --json
```

### 3. TypeScript SLA Library
```bash
cd typescript-sla-library
npm test
```
Runs 34 Vitest tests covering priority targets, breach detection, custom overrides, and the business hours calculation engine.

To run the demonstration script:
```bash
cd typescript-sla-library
npx tsx scripts/demo.ts
```

---

## Docker Support

- **Python Ticket Summary**:
  ```bash
  cd python-ticket-summary
  docker build -t ticket-summary .
  docker run --rm ticket-summary --help
  ```

- **TypeScript SLA Library**:
  ```bash
  cd typescript-sla-library
  docker build -t typescript-sla .
  docker run --rm typescript-sla
  ```
