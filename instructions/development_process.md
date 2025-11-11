# Development Process Guide for GitHub Copilot Collaboration

This guide defines the structured workflow for GitHub Copilot (and any AI assistant) when collaborating on code within this repository.
It enforces a **structured, review-first process** where all design, implementation, testing, and documentation steps require explicit user approval.

---

## Phase 1 — AI Setup

**Purpose:** Ensure the AI is aware of the project’s standards, conventions, and implementation patterns before proposing any solutions.

### Requirements

* The AI must **not write any code** in this phase.
* The AI must first read and internalize:

  * `./instructions/implementation_pattern.md`
  * `./instructions/python_instructions.md`

* Confirm that you have read the md files

---

## Phase 2 — Propose Implementation Options

**Purpose:** Present high-level implementation paths before coding begins.

### Requirements

* **Do not write code** in this phase.
* Provide concise **options (A, B, C)** with:

  * Summary, pros/cons, dependencies
* Based on Phase 1 patterns, identify and explain the **recommended** option.

### Example

```
Implementation Options for <Feature/Module>:

A) Use Azure Function with Blob Cache (recommended)
   - Matches existing BlueTeam enrichment pattern
B) Use Logic App orchestration
   - Low-code, limited flexibility
C) Use Containerized Queue Worker
   - Higher performance, more setup complexity
```

---

## Phase 3 — Selection & Approval

After presenting options:

1. The **user selects** an option.
2. The AI provides a **detailed implementation plan** for that option.

### Requirements

* **No code yet.**
* Include: file/folder structure, dependencies, configuration, security, observability, deployment, and integrations.
* Prompt for:

  * ✅ **Approve** — proceed to Phase 4
  * ❌ **Reject** — stop
  * ✏️ **Modify** — revise and resubmit

---

## Phase 4 — Code Generation (After Approval)

Once an implementation plan is explicitly **approved**:

* The AI may now **generate code**, following the plan exactly.
* Code must be written in **complete, functional files**.
* Provide a **summary** describing:

  * What was implemented
  * Which option it corresponds to
  * Key files created/modified
  * Any assumptions made

### Example Summary

> Implemented Option A — built Python Azure Function `CheckUrl` with Blob cache.
> Added `cache_loader.py` and `gsb_client.py`, plus telemetry to Log Analytics.

---

## Phase 5 — Testing

**Purpose:** Verify that the implementation works correctly through unit and safe live-endpoint tests.

### Requirements

* The AI must **read and follow** all testing guidance in
  **`./instructions/testing.md`**.
* Run only safe tests — **never create or execute destructive tests**.
* Summarize test results, failures, and proposed fixes.
* Do not modify code unless explicitly approved.
* Re-run tests after each approved fix until all pass.

---

## Phase 6 — Linting and Type Checking

**Purpose:** Validate code quality and consistency before documentation or merging.

### Requirements

* The AI must **read and follow** all guidance in
  **`./instructions/linting_typechecking.md`**.
* Apply only the tools and rules defined there.
* Report issues and suggest fixes, but do not change code without approval.

---

## Phase 7 — Documentation

**Purpose:** Ensure all implemented features are fully and clearly documented.

### Requirements

* The AI must **read and follow** all standards in
  **`./instructions/documentation.md`**.
* Documentation should include:

  * Purpose and design rationale
  * Usage examples and configuration
  * Integration and security notes
* Do not generate docs without referencing that file.

---

## Collaboration Rules

* ✅ Always request **explicit approval** before advancing phases.
* ✅ Label each output clearly (e.g., “**Phase 2: Implementation Options**”).
* ✅ Explain reasoning for recommendations.
* ❌ Never skip or merge phases.
* ❌ Never modify code without user authorization.
* ❌ Never override conventions from the instruction files.

---