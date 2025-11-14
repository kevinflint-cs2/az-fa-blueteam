# Development Process Entry Point for GitHub Copilot

> **Purpose:**
> This file defines the entire multi-phase workflow for GitHub Copilot collaboration.
> Each phase has its own detailed instructions in the `/instructions` directory.
> Copilot must read the file for the current phase **before continuing** and must **not skip or merge phases**.

---

## Phase 1 — Get Python Instructions

**Goal:** Load the project’s Python coding conventions.

* **Read:** [`./docs/instructions/python_instructions.md`](./docs/instructions/python_instructions.md)
* **Do not write code.**
* Summarize the key conventions and confirm readiness to continue.

---

## Phase 2 — Get Implementation Pattern

**Goal:** Load the architectural and implementation patterns used across the project.

* **Read:** [`./docs/instructions/implementation_pattern.md`](./docs/instructions/implementation_pattern.md)
* **Do not write code.**
* Summarize how the patterns will be applied to future phases.
* Ask the user for approval to proceed to Phase 3.

---

## Phase 3 — Propose Implementation Options

**Goal:** Present high-level implementation paths.

* Provide Options A/B/C with pros, cons, dependencies, and one recommended approach.
* Wait for user selection before continuing.

---

## Phase 4 — Selection & Approval

**Goal:** Create a detailed implementation plan for the chosen option.

* Do **not** write code yet.
* Write the implementation plan to:
  `./docs/implementation/[MODULENAME].md`
* Wait for explicit **Approve / Reject / Modify** feedback.

---

## Phase 5 — Code Generation (After Approval)

**Goal:** Implement the approved plan.

* Write full, functional files only after approval.
* Provide a short summary of what was implemented and any assumptions.

---

## Phase 6 — Testing

**Goal:** Verify the implementation using pytest (unit + safe live tests).

* **Read:** [`./docs/instructions/testing.md`](./docs/instructions/testing.md)
* Run tests, summarize results, and propose fixes.
* Do **not** modify code unless explicitly approved.
* **Never** create or run destructive tests.

---

## Phase 7 — Linting and Type Checking

**Goal:** Ensure code quality and consistency.

* **Read:** [`./docs/instructions/linting_typechecking.md`](./docs/instructions/linting_typechecking.md)
* Run Ruff and mypy as described.
* Fix issues only with approval.
* Re-run until clean.

---

## Phase 8 — Documentation

**Goal:** Generate and update project documentation.

* **Read:** [`./docs/instructions/documentation.md`](./docs/instructions/documentation.md)
* Create or update:

  * `./docs/modules/[MODULENAME].md` — module-specific doc
  * `./README.md` — endpoint-focused quick-start guide
* Use GitHub Flavored Markdown and GitHub admonitions.
* Keep it concise; no emojis.

---

## Collaboration Rules

* Always state the **current phase** in responses.
* Always **read the phase’s instruction file** before acting.
* Ask for **explicit approval** before writing or modifying code.
* Never skip, merge, or reorder phases.
* Reference relative file paths exactly as listed.
* When provideing next steps or options always present as a choice of A, B, C, etc...

---