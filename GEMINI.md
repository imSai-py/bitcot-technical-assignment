# Agent Instructions & Workflow

## 1. Communication Protocol
- Standard : use ASD-STE 100 language for all communication
- **Style**: Concise, direct GitHub-flavored markdown. Always use clickable links for files and symbols with `file://` scheme.

## 2. Git & Branching Strategy
- **Core Branches**:
  - `master`: Production release branch.
  - `staging`: Staging and pre-production validation branch.
  - `dev`: Active development integration branch.
- **Task Branching**:
  - Always branch from `dev`.
  - Branch naming format: `[ticket-type]/[ticket-number]/[ticket-short-name]` (e.g., `feat/T-101/user-auth`, `fix/T-204/session-timeout`).
- **Pre-Commit Synchronization**:
  - Pull latest upstream changes from `dev` (or `master` if explicitly required by ticket instructions) before staging and committing changes.

## 3. Development & Verification Standards (Python)
- **Toolchain**: Use `pytest` for tests, and `ruff` / `black` for linting and code formatting.
- **Verification Gate**: Run automated tests and lint checks locally before committing. Show verification evidence (command output) prior to claiming task completion.
- **Code Integrity**: Preserve existing docstrings, type annotations, and comments unless explicitly instructed otherwise.

## 4. Pull Request (PR) & Ticket Lifecycle
- **PR Structure Template**: Every PR body must follow this exact template structure:
  ```markdown
  ## Summary

  <Visual diagram, call tree, diff-sketch, or shallow file tree>

  ## Verified end to end

  - <Concrete end-to-end verification workflows, execution scenarios, edge-case validations>

  ## Verification

  - `<command>` — passed (<evidence / test counts>)

  ## Engineering practices applied

  - <Key design principles, typed boundaries, isolated state, synthetic fixtures, standard library constraints>

  ## Review

  - **Standards:** <StandardsReview findings and conventions adherence>
  - **Spec:** <SpecReview findings and functional requirements coverage>

  ## Follow-ups

  - <Upcoming tickets, follow-up items, or out-of-scope enhancements>

  ## Merge Danger

  **Door:** <one-way or two-way with rollback rationale>
  **Blast Radius:** <isolated / narrow / medium / broad with scope assessment>

  <!-- This is an auto-generated comment: release notes by coderabbit.ai -->

  ## Summary by CodeRabbit

  * **New Features**
    * <bullet points of new capabilities>
  * **Bug Fixes**
    * <bullet points of bug fixes, if applicable>

  <!-- end of auto-generated comment: release notes by coderabbit.ai -->
  ```
- **PR Completion Gate**: Upon opening or completing a PR:
  1. Provide the clickable link to the PR.
  2. Ask: *"Would you like to proceed with the next ticket?"*

5. **Environment Variable Security:** Whenever creating or updating an `.env.example` file, README, or other documentation containing environment variable examples, use mock/placeholder values only. Never copy or expose actual credentials, API keys, tokens, passwords, or secrets from the `.env` file. Ensure all example values are clearly fake and safe to share.