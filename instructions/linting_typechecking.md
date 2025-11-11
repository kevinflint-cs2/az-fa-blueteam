# Linting & Type Checking (Phase 5)

**AI is allowed to run these commands.**
---

## Linting (Ruff)

### Tools

* **Ruff** for lint + format
* Use repo-pinned versions/config in `pyproject.toml` if present.

### Order of operations

```bash
ruff check . --fix
ruff format .
ruff check .
```

> Optional (only if approved): `ruff check . --fix --unsafe-fixes`

### Resolution loop

1. Run the commands.
2. If there are issues, show a **short summary** (counts + top rules/files) and **suggest fixes**.
3. Ask: “Apply Fix mode?” or “Targeted edits?”
4. If approved, apply fixes and **re-run** until clean.

### Reporting (keep it brief)

* Status for: Ruff lint, Ruff format, mypy (PASS/FAIL).
* Top 3–5 issues with one-line suggestions.
* Next step prompt (Fix mode / targeted edits / stop).

---

## Type Checking (mypy)

**Goal:** Fix one `mypy` issue at a time with simple explanations, avoiding infinite loops.

---

**Instructions for the AI:**

1. Run

   ```bash
   mypy . --config-file mypy.ini --check-untyped-defs
   ```

   to gather type errors.

2. Read the list of `mypy` errors.

3. **Process only the first error** in the list.

4. For that first error:

   * Explain **what the issue means** in plain language.
   * Explain **how to fix it** simply (no code, just reasoning).

5. Ask whether to:

   * ✅ **Approve fix** — implement the change, rerun `mypy`, and repeat from step 1.
   * 🚫 **Skip** — ignore this specific error (treat it as resolved for now), rerun `mypy`, and continue with the next issue.

6. If the same error reappears after multiple fix attempts, **mark it as “unresolvable” and skip it** automatically to avoid looping.

7. Continue until all errors are resolved or skipped.

8. Output a final summary showing:

   * Errors fixed
   * Errors skipped
   * Any recurring (“unresolvable”) issues

---

**Key rules:**

* Never show or modify code unless the user explicitly approves.
* Never reattempt a fix on an error already marked as skipped or unresolvable.
* Keep explanations brief and beginner-friendly.
* Always restart from a clean `mypy` run after each approved fix.

---