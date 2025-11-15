---
description: 'Execute linting and type checking with iterative fix workflow'
mode: 'agent'
tools: ['run_terminal']
---

# Linting & Type Checking — Code Quality Validation

Execute automated code quality checks using Ruff (linting/formatting) and MyPy (type checking) with iterative fix workflow. Process issues one at a time to avoid infinite loops.

## Mission

Validate Python code quality through automated linting and type checking tools. Provide clear explanations of issues and guide user through fix approval workflow until all checks pass.

## Scope & Preconditions

- **Linting Tool:** Ruff (combines linting + formatting)
- **Type Checker:** MyPy with strict configuration (`mypy.ini`)
- **Target Files:** All Python files in repository (`**/*.py`)
- **Authority:** May run checks and collect results; cannot modify code without approval
- **Environment:** Virtual environment activated (`.venv/bin/activate`)

## Inputs

- **Check Type:** Linting, formatting, type checking, or all
- **Fix Mode:** Auto-fix safe issues vs. manual targeted edits
- **Unsafe Fixes:** Whether to apply unsafe auto-fixes (requires approval)

## Workflow

### Phase A — Linting with Ruff

Execute Ruff checks in proper sequence to ensure code quality and consistent formatting.

#### Step 1: Auto-fix Safe Issues

```bash
ruff check . --fix
```

**What it does:**
- Fixes safe linting issues automatically
- Removes unused imports
- Fixes incorrect quote styles
- Corrects whitespace issues

**Expected outcome:**
- Most common issues resolved
- Files modified in place
- Summary of changes applied

#### Step 2: Format Code

```bash
ruff format .
```

**What it does:**
- Applies consistent code formatting
- Adjusts line length (max 79 characters)
- Fixes indentation
- Organizes imports

**Expected outcome:**
- All Python files formatted consistently
- Files modified in place

#### Step 3: Final Lint Check

```bash
ruff check .
```

**What it does:**
- Validates all linting rules
- Reports remaining issues
- Exits with code 0 if clean, non-zero if issues remain

**Expected outcome:**
- No issues: Ready to proceed
- Issues remain: Report and request approval for fixes

#### Optional: Unsafe Auto-fixes

**Only with explicit approval:**

```bash
ruff check . --fix --unsafe-fixes
```

**What it does:**
- Applies fixes that may change code behavior
- Removes unused variables
- Simplifies boolean expressions
- Refactors code patterns

**Risk:** May alter logic; requires manual review after application.

### Phase B — Type Checking with MyPy

Execute MyPy type checking with one-issue-at-a-time resolution to prevent infinite loops.

#### Step 1: Run Type Checker

```bash
mypy . --config-file mypy.ini --check-untyped-defs
```

**What it does:**
- Validates type hints across all files
- Checks for type inconsistencies
- Verifies return types match declarations
- Ensures proper use of `Optional`, `Union`, etc.

**Expected outcome:**
- List of type errors with file locations and descriptions
- Exit code 0 if clean, non-zero if errors exist

#### Step 2: Process First Error Only

**Critical:** Only address the first error in the list to avoid looping.

1. **Read the error message:**
   ```
   functions/module.py:42: error: Argument 1 to "process" has incompatible type "str | None"; expected "str"
   ```

2. **Explain in plain language:**
   ```
   Issue: The function expects a string, but we're passing a value that could be None.
   
   Why it matters: This could cause runtime errors if None is passed.
   
   How to fix: Either ensure the value is never None before passing, or update
   the function signature to accept Optional[str].
   ```

3. **Request approval:**
   ```
   Proposed fix:
   Add None check before calling process():
   
   if value is not None:
       process(value)
   
   Approve this fix? (yes/no/skip)
   ```

#### Step 3: Apply Approved Fix

After approval:
1. Implement the minimal fix required
2. Re-run `mypy` from scratch
3. Move to the next first error in the new output

#### Step 4: Handle Persistent Errors

If the same error appears 3+ times after attempted fixes:
1. Mark as "unresolvable"
2. Automatically skip
3. Continue with next error
4. Report unresolvable issues in final summary

#### Step 5: Iterate Until Clean

Continue Steps 1-4 until:
- No errors remain, OR
- All errors are marked as unresolvable/skipped

### Reporting Format

#### Ruff Status Report

```
=== Ruff Linting Results ===

Status: PASS / FAIL

Issues Found: X
Files Modified: Y

Top Issues:
1. F401 - Unused import 'os' (5 occurrences)
2. E501 - Line too long (3 occurrences)
3. W292 - No newline at end of file (2 occurrences)

Actions:
✅ Auto-fixed: X issues
⏭️  Requires manual fix: Y issues

Next Step: [Run ruff format / Apply manual fixes / Proceed to MyPy]
```

#### MyPy Status Report

```
=== MyPy Type Checking Results ===

Status: PASS / FAIL

Errors Found: X
Files Affected: Y

Processing First Error:
File: functions/module.py
Line: 42
Error: Argument 1 to "process" has incompatible type "str | None"; expected "str"

Explanation:
[Plain language explanation]

Proposed Fix:
[Specific code change]

Approve fix? (yes/no/skip)
```

#### Final Summary

```
=== Code Quality Status ===

Ruff Lint: ✅ PASS / ❌ FAIL (X issues)
Ruff Format: ✅ PASS / ❌ FAIL
MyPy: ✅ PASS / ❌ FAIL (X errors)

Fixed:
- X linting issues auto-fixed
- Y type errors resolved

Skipped:
- Z unresolvable type errors

Remaining Issues:
[List if any]

Next Step: [Proceed to Phase 7 / Address remaining issues]
```

## Resolution Loop Workflow

### For Linting Issues

1. Run `ruff check . --fix`
2. Run `ruff format .`
3. Run `ruff check .` (final validation)
4. If issues remain:
   - Show summary (counts + top rules/files)
   - Suggest fix approach
   - Ask: "Apply targeted edits?" or "Use unsafe fixes?"
5. If approved, apply fixes and re-run from step 3
6. Repeat until clean

### For Type Errors

1. Run `mypy . --config-file mypy.ini`
2. Read full error list
3. Process **only the first error**:
   - Explain what it means
   - Explain how to fix it
   - Request approval
4. If approved:
   - Apply fix
   - Re-run MyPy from step 1
   - Process new first error
5. If skipped:
   - Mark as skipped
   - Re-run MyPy from step 1
   - Process new first error
6. If same error seen 3+ times:
   - Mark as "unresolvable"
   - Automatically skip
   - Continue with next error
7. Repeat until no errors or all skipped/unresolvable

## Common Type Issues and Fixes

### Issue: Optional Type Mismatch

```python
# Error: Argument has incompatible type "str | None"; expected "str"

# Fix Option 1: Add None check
if value is not None:
    process(value)

# Fix Option 2: Update function signature
def process(value: str | None) -> dict:
    if value is None:
        return {"status": "error"}
    # ... rest of function
```

### Issue: Missing Return Type

```python
# Error: Function is missing a return type annotation

# Fix: Add explicit return type
def calculate(x: int, y: int) -> int:
    return x + y
```

### Issue: Inconsistent Return Types

```python
# Error: Incompatible return value type (got "None", expected "dict")

# Fix: Ensure all code paths return correct type
def get_data(key: str) -> dict:
    if not key:
        return {}  # Not None
    return {"key": key}
```

### Issue: Missing Type Hints

```python
# Error: Call to untyped function

# Fix: Add type hints to function
def helper(value):  # Before
    return value * 2

def helper(value: int) -> int:  # After
    return value * 2
```

### Issue: Any Type Usage

```python
# Error: Returning Any from function declared to return "dict"

# Fix: Use specific types instead of Any
from typing import Dict, Any

def parse(data: Any) -> Dict[str, Any]:  # Before
    return data

def parse(data: dict) -> Dict[str, str]:  # After (more specific)
    return {k: str(v) for k, v in data.items()}
```

## Configuration Files

### Ruff Configuration (ruff.toml)

Expected configuration in repository root:

```toml
[lint]
select = ["E", "F", "W", "I"]  # Error, pyflakes, warning, import
ignore = []

[format]
line-length = 79
indent-style = "space"
quote-style = "double"
```

### MyPy Configuration (mypy.ini)

Expected configuration in repository root:

```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
check_untyped_defs = True
```

## Quality Assurance Checklist

- [ ] Virtual environment activated
- [ ] Ruff auto-fixes applied: `ruff check . --fix`
- [ ] Code formatted: `ruff format .`
- [ ] No remaining lint issues: `ruff check .` exits 0
- [ ] Type errors addressed one at a time
- [ ] MyPy passes: `mypy .` exits 0
- [ ] No unsafe fixes applied without approval
- [ ] All persistent errors marked as unresolvable
- [ ] Final summary provided with clear status

## Approval Prompts

### For Unsafe Ruff Fixes

```
The following unsafe auto-fixes are available:
- Remove unused variables (may affect debugging)
- Simplify boolean expressions (may alter logic)
- Refactor comprehensions (may change behavior)

These changes modify code behavior and should be reviewed carefully.

Apply unsafe auto-fixes? (yes/no)
```

### For Type Error Fixes

```
MyPy Error #1:
File: functions/module.py, Line: 42
Issue: [Plain explanation]

Proposed Fix:
[Specific change with code snippet]

This fix will [expected outcome].

Options:
- yes: Apply fix and re-run MyPy
- no: Stop type checking
- skip: Mark as unresolvable and continue with next error

Your choice?
```

## Validation Steps

After all checks pass:

1. **Verify Ruff:** `ruff check . && ruff format --check .`
2. **Verify MyPy:** `mypy . --config-file mypy.ini`
3. **Check for warnings:** Review output for deprecation notices
4. **Confirm clean state:** No errors, all files formatted consistently
5. **Start function app:** `func start` (run in background)
6. **Run full test suite:** `pytest -vv` to verify code changes didn't break functionality
7. **Stop function app:** After tests complete

State: "Phase 6 complete. Code quality validated and tests passing. Ready for Phase 7 (Documentation)."

## Related Resources

- [Development Process](./development-process.prompt.md) — Seven-phase workflow
- [Python Coding Standards](./python-coding.prompt.md) — Style guidelines
- [Ruff Documentation](https://docs.astral.sh/ruff/) — Official Ruff guide
- [MyPy Documentation](https://mypy.readthedocs.io/) — Official MyPy guide
