---

### 🧠 Refined Prompt — *“Single-Error Resolver Loop”*

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