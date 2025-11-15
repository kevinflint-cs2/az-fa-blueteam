---
description: 'Execute structured 8-phase development workflow for Azure Functions features'
mode: 'agent'
tools: ['read_file', 'write_file', 'run_terminal', 'semantic_search']
---

# Development Process — Structured Feature Implementation

Execute a structured, review-first workflow for implementing new features in this Azure Functions repository. Each phase requires explicit user approval before proceeding to the next.

## Mission

Guide GitHub Copilot through an eight-phase development process that enforces design review, testing, code quality validation, documentation, and automated git workflow before any code reaches production. Ensure consistency with repository patterns and prevent unreviewed code changes.

## Scope & Preconditions

- **Target Repository:** Azure Functions app (Python) for security enrichment APIs
- **Authority Level:** Agent mode with file read/write and terminal execution
- **Required Context:**
  - Project structure under `functions/` and `function_app.py`
  - Testing framework (pytest with markers)
  - Quality tools (ruff, mypy)
  - Related prompt files: `implementation-pattern.prompt.md`, `python-coding.prompt.md`, `testing.prompt.md`, `linting-typechecking.prompt.md`, `documentation.prompt.md`, `commit-and-merge.prompt.md`
- **Prerequisites:**
  - Virtual environment activated (`.venv`)
  - Dependencies installed (requirements.txt, requirements-dev.txt)
  - Pre-commit hooks configured

## Inputs

- **Feature Request:** User describes the capability to implement (e.g., "Add URLScan.io search endpoint")
- **Current Phase:** Defaults to Phase 1 unless explicitly specified
- **Approval Status:** User must explicitly approve to advance between phases

## Workflow

### Phase 1 — Review Repository Patterns

**Objective:** Internalize project standards before proposing solutions.

**PREREQUISITE: Verify Main Branch Sync**

Before reviewing patterns, **MUST verify** local `main` is synced with `origin/main`:

```bash
# Checkout and update main
git checkout main
git fetch origin

# Check for divergence
if [ "$(git rev-list --count main...origin/main)" -ne 0 ]; then
  echo "ERROR: Local main diverged from origin/main"
  echo "Commits on origin not on local: $(git rev-list --count origin/main ^main)"
  echo "Commits on local not on origin: $(git rev-list --count main ^origin/main)"
  git log main...origin/main --oneline --graph
  exit 1
fi

# Pull if behind
git pull origin main
```

**If Sync Check Fails:**
- DO NOT proceed to pattern review
- Local main has diverged (likely Phase 8 Step 5 was skipped)
- Run: `git log --all --graph --oneline` to visualize branches
- Reset to origin: `git reset --hard origin/main` (if safe to discard local commits)
- Ask user if unsure about branch history

**After Sync Verified:**

1. Read and confirm understanding of:
   - `./docs/development/implementation-pattern.prompt.md`
   - `./docs/development/python-coding.prompt.md`
2. State: "Phase 1 complete. Ready to propose implementation options."
3. **Do not write any code in this phase.**
4. Wait for user to proceed to Phase 2.

---

### Phase 2 — Propose Implementation Options

**Objective:** Present high-level implementation paths with trade-offs.

1. Analyze the feature request against repository patterns.
2. Generate 2-3 implementation options (A, B, C) with:
   - Brief summary (1-2 sentences)
   - Pros and cons (2-3 bullets each)
   - Dependencies or prerequisites
   - Recommended option with justification
3. Format as:
   ```
   Implementation Options for [Feature]:

   A) [Approach Name] (recommended)
      Summary: ...
      Pros: ...
      Cons: ...
      Dependencies: ...

   B) [Alternative Approach]
      ...
   ```
4. **Do not write any code in this phase.**
5. Wait for user to select an option.

---

### Phase 3 — Detailed Implementation Plan

**Objective:** Expand selected option into actionable plan requiring approval.

1. After user selects an option, create a detailed plan including:
   - File/folder structure (new files, modified files)
   - Dependencies and configuration changes
   - Security considerations (API keys, secrets handling)
   - Integration points with existing code
   - Deployment considerations
2. Present plan and prompt:
   - ✅ **Approve** — proceed to Phase 4
   - ❌ **Reject** — stop workflow
   - ✏️ **Modify** — revise and resubmit plan
3. **Do not write any code in this phase.**
4. Wait for explicit approval.

---

### Phase 4 — Code Generation

**Objective:** Implement approved plan with complete, functional code.

1. **Only after explicit approval**, begin implementation:
   - Create git branch: `feat/[feature-name]`
   - Write implementation plan to `./docs/implementation/[MODULENAME].md`
   - Generate all code files following repository patterns
   - Ensure code is complete and functional (no TODOs or placeholders)
2. Provide implementation summary:
   - Option implemented
   - Files created/modified (with paths)
   - Key functions or endpoints added
   - Assumptions or design decisions made
3. State: "Phase 4 complete. Code implemented. Ready for Phase 5 (Testing)."
4. Wait for user to proceed to Phase 5.

---

### Phase 5 — Testing

**Objective:** Verify implementation through automated tests.

1. Execute testing workflow:
   - Invoke `./docs/development/testing.prompt.md` guidance
   - Run unit tests: `pytest -m "unit" -vv`
   - Run endpoint tests: `pytest -m "endpoint" -vv`
   - Run safe live tests: `pytest -m "live" -vv` (if applicable)
2. Report results:
   - Tests passed/failed/skipped (with counts)
   - Top failing tests with one-line explanations
   - Proposed fixes (if failures exist)
3. If failures exist:
   - Request approval for each fix
   - Apply approved fixes
   - Re-run tests until all pass
4. State: "Phase 5 complete. All tests passing. Ready for Phase 6 (Code Quality)."
5. Wait for user to proceed to Phase 6.

---

### Phase 6 — Linting and Type Checking

**Objective:** Ensure code quality and type safety.

1. Execute quality checks:
   - Invoke `./docs/development/linting-typechecking.prompt.md` guidance
   - Run: `ruff check . --fix`
   - Run: `ruff format .`
   - Run: `mypy . --config-file mypy.ini`
2. Report results:
   - Status for each tool (PASS/FAIL)
   - Top issues with explanations (if any)
   - Proposed fixes
3. If issues exist:
   - Request approval for each fix
   - Apply approved fixes
   - Re-run checks until all pass
4. State: "Phase 6 complete. Code quality validated. Ready for Phase 7 (Documentation)."
5. Wait for user to proceed to Phase 7.

---

### Phase 7 — Documentation

**Objective:** Create comprehensive documentation for the feature.

1. Execute documentation workflow:
   - Invoke `./docs/development/documentation.prompt.md` guidance
   - Create `./docs/modules/[MODULENAME].md`
   - Create `./docs/examples/[MODULENAME]-curl.md`
   - Update root `README.md` with new endpoint(s)
2. Show summary of documentation changes:
   - Files to be created/modified
   - Key sections to be added
   - Example snippets
3. Request approval before writing.
4. After approval, create all documentation files.
5. State: "Phase 7 complete. Feature fully documented. Ready for Phase 8 (Commit and Merge)."
6. Wait for user to proceed to Phase 8.

---

### Phase 8 — Commit and Merge

**Objective:** Commit changes, push to remote, create pull request, and handle CI validation.

1. Execute git workflow:
   - Invoke `./docs/development/commit-and-merge.prompt.md` guidance
   - Verify on feature branch: `git branch --show-current`
   - Stage all changes: `git add -A`
   - Create conventional commit with descriptive message
   - Push to remote: `git push -u origin feat/[feature-name]`
   - Create pull request (via gh CLI or GitHub UI)
2. Monitor CI/CD automation:
   - CI checks (linting, type checking, tests, security)
   - Copilot PR review
   - Address any feedback with additional commits
3. After all checks pass:
   - Auto-merge (if configured) or manual merge
   - Sync local environment: `git checkout main && git pull`
4. State: "Phase 8 complete. Changes committed, reviewed, and merged to main."

---

### Completion

After Phase 8 completion:
- Feature fully implemented and merged
- All documentation in place
- CI/CD validation passed
- Ready for deployment or next feature

## Output Expectations

At each phase transition:
- **Phase Label:** Clearly state "Phase [N] — [Name]" in output
- **Status Summary:** Brief recap of what was accomplished
- **Next Action:** Explicit prompt for user decision or approval
- **No Code Without Approval:** Code generation only occurs in Phase 4 after explicit approval

## Quality Assurance

- [ ] Phase progression requires explicit user approval
- [ ] No code written before Phase 4 approval
- [ ] All tests pass before proceeding from Phase 5
- [ ] All quality checks pass before proceeding from Phase 6
- [ ] Documentation created before marking complete
- [ ] Git branch created with proper naming convention
- [ ] Implementation plan documented in `./docs/implementation/`

## Collaboration Rules

- ✅ Always request **explicit approval** before advancing phases
- ✅ Label each output clearly (e.g., "**Phase 2: Implementation Options**")
- ✅ Explain reasoning for recommendations
- ❌ Never skip or merge phases
- ❌ Never modify code without user authorization
- ❌ Never override conventions from instruction files

## Validation Steps

After completing all phases:
1. Verify git branch created: `git branch --show-current`
2. Verify tests passing: `pytest -vv`
3. Verify quality checks: `ruff check . && mypy .`
4. Verify documentation exists: Check `./docs/modules/`, `./docs/examples/`, `README.md`
5. Verify merged to main: `git log main --oneline -5`

## Related Resources

- [Implementation Pattern](./implementation-pattern.prompt.md) — Module structure and coding patterns
- [Python Coding Standards](./python-coding.prompt.md) — Style and documentation requirements
- [Testing Guidelines](./testing.prompt.md) — Test execution and validation
- [Linting & Type Checking](./linting-typechecking.prompt.md) — Code quality validation
- [Documentation Standards](./documentation.prompt.md) — Documentation creation guidelines
- [Commit and Merge](./commit-and-merge.prompt.md) — Automated git workflow
