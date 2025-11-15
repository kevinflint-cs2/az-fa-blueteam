---
description: 'Execute fully automated commit, push, PR, and merge workflow for solo developer'
mode: 'agent'
tools: ['run_terminal']
---

# Commit and Merge — Fully Automated Git Workflow

Execute fully automated git workflow to commit changes, push to remote, create pull request with auto-merge, and let CI validation automatically merge to main.

## Mission

Automate the complete process of committing code changes, creating a feature branch, pushing to remote, opening a pull request, and automatically merging after CI/CD validation passes. Designed for solo developer workflow with no manual review gates. Follow conventional commit standards and leverage GitHub automation for zero-touch merge.

## Scope & Preconditions

- **Prerequisites:**
  - All phases 1-7 complete (code, tests, quality, documentation)
  - Git repository initialized with remote configured
  - Feature branch created in Phase 4 (`feat/[feature-name]`)
  - Changes ready for commit
  - GitHub repository configured for auto-merge (see Required GitHub Settings)
- **Authority:** Can execute git commands and create pull requests
- **GitHub Integration:** CI/CD pipeline, auto-merge enabled, branch protection configured
- **Workflow Type:** Solo developer - no manual review or approval gates

## Inputs

- **Feature Name:** Used in branch name and PR title
- **Changes Summary:** Description of what was implemented
- **Conventional Commit Type:** feat, fix, docs, refactor, test, chore
- **Breaking Changes:** Whether changes are breaking (optional)

## Required GitHub Settings

For fully automated workflow, configure your repository:

**Branch Protection Rules (main):**
- ✅ Require status checks to pass before merging
  - `ruff-lint` (or your CI check name)
  - `mypy-typecheck` (or your CI check name)
  - `pytest-unit` (or your CI check name)
  - `pytest-endpoint` (or your CI check name)
  - `detect-secrets` (or your CI check name)
- ✅ Require branches to be up to date before merging
- ✅ Allow auto-merge
- ✅ Automatically delete head branches
- ❌ Do NOT require approvals (solo developer)

**Repository Settings:**
- ✅ Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests
- ✅ Enable auto-merge for pull requests

**Note:** Configure your CI/CD pipeline (GitHub Actions) to run these checks on pull requests.

## Workflow

### Step 1: Verify and Stage Changes

Confirm you're on the feature branch and stage all changes:

```bash
# Verify current branch
git branch --show-current
# Expected: feat/[feature-name]

# Stage all changes
git add -A
```

**What gets staged:**
- New function modules in `functions/`
- Updated `function_app.py`
- New test files in `tests/`
- Documentation in `docs/`
- Updated `README.md`
- Any configuration changes

### Step 2: Commit with Conventional Formatormat

Generate commit message following conventional commits format:

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code change that neither fixes bug nor adds feature
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example Commit Message:**
```
feat(urlscan): add search and result retrieval endpoints

Implemented two new URLScan.io endpoints:
- /api/urlscan/result - Retrieve scan results by UUID
- /api/urlscan/search - Search scans with ElasticSearch syntax

Added comprehensive test coverage (43 unit, 19 endpoint, 7 live tests)
Updated documentation with curl examples and module details
```

**Execute commit:**
```bash
git commit -m "feat(module): brief description

Detailed description of changes...

- Key point 1
- Key point 2
- Key point 3"
```

**If commit fails due to detect-secrets:**

Pre-commit hooks will block commits containing potential secrets. When this occurs:

1. **Review the detected secret:**
   - Location: File path and line number displayed in error
   - Type: Secret type identified (e.g., "Hex High Entropy String", "Secret Keyword")

2. **Identify the secret:**
   - Read the flagged line in the file
   - Determine what was detected (API key, UUID, MongoDB ID, etc.)

3. **Explain why it's a false positive:**
   - Example: "MongoDB ObjectId in example JSON response"
   - Example: "Placeholder API key 'your-key-here' in documentation"
   - Example: "Mock UUID in test fixture"
   - Example: "High entropy hex string in sample data"

4. **Request approval:**
   ```
   Detected Secret Analysis:
   
   File: [file-path]
   Line: [line-number]
   Type: [secret-type]
   Content: [actual string]
   
   Assessment: This is a false positive because [explanation]
   
   Approve adding to baseline? (yes/no)
   ```

5. **After approval, add pragma comment:**
   ```bash
   # Add inline comment to mark as safe
   # Example: "your-key-here"  # pragma: allowlist secret
   
   # Re-stage and commit
   git add -A
   git commit -m "[same commit message]"
   ```

**Never bypass without approval** - Real secrets must never be committed.

### Step 3: Push and Create Auto-Merge PR

Push branch and create pull request with auto-merge enabled:

```bash
# Push feature branch
git push -u origin feat/[feature-name]

# Create PR with auto-merge enabled
gh pr create \
  --title "feat(module): Brief description" \
  --body "## Description

[Detailed description of changes]

## Changes
- Item 1
- Item 2
- Item 3

## Testing
- All tests passing (X/X)
- Linting and type checking clean
- Documentation updated

## Validation
All Phases 1-7 complete. Ready for automated merge." \
  --base main \
  --head feat/[feature-name] \
  --auto-merge
```

**Expected output:**
- PR created successfully
- Auto-merge enabled
- CI checks triggered automatically
- Message: "Pull request will automatically merge when all requirements are met"

### Step 4: Automated CI Validation and Merge

GitHub automatically executes the following workflow:

**CI Checks Triggered:**
- ✅ Linting (Ruff)
- ✅ Type checking (MyPy)
- ✅ Unit tests
- ✅ Endpoint tests
- ✅ Security scans (detect-secrets)

**Auto-Merge Conditions:**
- ✅ All CI checks pass
- ✅ Security scans pass
- ✅ Branch is up to date with main
- ✅ Branch protection rules satisfied

**GitHub Automatically:**
1. Runs all status checks
2. Waits for all checks to pass
3. Performs "Squash and Merge" into `main`
4. Closes the PR
5. Deletes the feature branch

**Expected Timeline:**
- CI checks complete: 2-5 minutes
- Auto-merge executes: Immediately after checks pass
- Total time: ~3-6 minutes from PR creation to merge

**If CI Checks Fail:**

*Note: This should be rare since Phases 5-6 validated everything locally.*

1. Review CI failure in GitHub Actions logs
2. Fix issue locally
3. Re-run affected phase:
   - Tests: `pytest -vv`
   - Linting: `ruff check . --fix && ruff format .`
   - Type checking: `mypy .`
4. Commit fix:
   ```bash
   git add -A
   git commit -m "fix: resolve CI failure - [brief description]"
   git push
   ```
5. CI automatically re-runs and auto-merges when passing

### Step 5: Sync Local Environment (MANDATORY)

After auto-merge completes (monitor PR page for completion), **you MUST execute these commands** to complete Phase 8:

```bash
# Switch to main branch
git checkout main

# Pull latest changes (includes your squashed commit)
git pull origin main

# VERIFICATION REQUIRED: Confirm local matches remote
git fetch origin
if ! git diff main origin/main --exit-code >/dev/null 2>&1; then
  echo "ERROR: Local main diverged from origin/main"
  echo "Run: git log main...origin/main --oneline"
  exit 1
fi

# Verify merge
git log --oneline -5

# Clean up local feature branch
git branch -d feat/[feature-name]
```

**Critical Requirements:**
- ✅ Verification command MUST pass (no diff between main and origin/main)
- ✅ Your commit appears in `main` history
- ✅ Feature branch deleted on GitHub
- ✅ Local environment synced with remote

**If Verification Fails:**
- DO NOT continue with Phase 1 of next feature
- Run: `git log --all --graph --oneline` to see branch history
- If local has commits not on origin: Branch divergence occurred
- Reset to origin: `git reset --hard origin/main` (saves work, resets branch)
- Contact user if unsure how branches diverged

**Phase 8 is INCOMPLETE until this step executes successfully.**

## Conventional Commit Examples

### New Feature
```bash
git commit -m "feat(abuseipdb): add IP reputation check endpoint

Implemented /api/abuseipdb/check endpoint with:
- IP address validation
- API integration with rate limiting
- Comprehensive error handling
- Full test coverage (28 tests)"
```

### Bug Fix
```bash
git commit -m "fix(whois): handle empty domain responses

Fixed crash when WHOIS server returns empty response.
Added validation and default values."
```

### Documentation
```bash
git commit -m "docs(urlscan): add curl examples and module documentation

Created comprehensive documentation:
- docs/modules/urlscan.md
- docs/examples/urlscan-curl.md
- Updated README.md with new endpoints"
```

### Refactoring
```bash
git commit -m "refactor(dns): extract retry logic to shared utility

Moved exponential backoff retry logic to shared module
for reuse across all API clients."
```

### Testing
```bash
git commit -m "test(alienvault): add endpoint integration tests

Added 15 new endpoint tests covering:
- Success scenarios
- Error handling
- Edge cases"
```

### Breaking Change
```bash
git commit -m "feat(api)!: change response format to match RFC standard

BREAKING CHANGE: API responses now use 'data' instead of 'result' key.

Migration: Update client code to expect:
{ 'status': 'ok', 'data': {...} }
instead of:
{ 'status': 'ok', 'result': {...} }"
```

## Pull Request Template

**Title Format:**
```
<type>(<scope>): <brief description>
```

**Body Template:**
```markdown
## Description

[Clear description of what was implemented and why]

## Changes

- Added X functionality
- Updated Y component
- Fixed Z issue

## Implementation Details

- **Module:** `functions/module_name.py`
- **Endpoints:** `/api/module/action`
- **Tests:** X unit, Y endpoint, Z live

## Testing

- ✅ All tests passing (X/X)
- ✅ Linting clean (ruff)
- ✅ Type checking clean (mypy)
- ✅ Pre-commit hooks pass

## Documentation

- ✅ Module documentation created
- ✅ Curl examples added
- ✅ README updated

## Breaking Changes

[List any breaking changes, or "None"]

## Related Issues

Closes #[issue-number]
Relates to #[issue-number]
```

## CI/CD Pipeline Expectations

### Required Checks (Must Pass)

1. **Linting:**
   ```bash
   ruff check .
   ruff format --check .
   ```

2. **Type Checking:**
   ```bash
   mypy . --config-file mypy.ini
   ```

3. **Unit Tests:**
   ```bash
   pytest -m "mock" -vv
   ```

4. **Endpoint Tests:**
   ```bash
   pytest -m "endpoint" -vv
   ```

5. **Security Scan:**
   ```bash
   detect-secrets scan
   ```

### Optional Checks

1. **Live Tests:** (may require credentials)
   ```bash
   pytest -m "live" -vv
   ```

2. **Coverage Report:**
   ```bash
   pytest --cov=functions --cov-report=term-missing
   ```

## Quality Assurance Checklist

Before pushing:

- [ ] Phases 1-7 completed and validated
- [ ] Feature branch created with proper naming (`feat/[name]`)
- [ ] All files staged (`git add -A`)
- [ ] Conventional commit message formatted correctly
- [ ] Commit message body includes detailed description
- [ ] All tests passing locally (`pytest -vv`)
- [ ] Linting and type checking clean (`ruff check . && mypy .`)
- [ ] Documentation complete and accurate
- [ ] No secrets or credentials in code

After PR creation:

- [ ] PR created with `--auto-merge` flag enabled
- [ ] CI checks triggered automatically
- [ ] PR description complete with all sections
- [ ] Monitoring CI progress (should complete in 3-6 minutes)
- [ ] Auto-merge will trigger when all checks pass

## Troubleshooting

### Issue: Push Rejected (Behind Remote)

**Solution:**
```bash
# Fetch and rebase
git fetch origin
git rebase origin/main

# Resolve conflicts if any
# Then force push (only if you're the only one on the branch)
git push --force-with-lease
```

### Issue: Merge Conflicts

**Solution:**
```bash
# Update main locally
git checkout main
git pull

# Rebase feature branch
git checkout feat/[feature-name]
git rebase main

# Resolve conflicts in editor
# After resolving:
git add -A
git rebase --continue
git push --force-with-lease
```

### Issue: CI Checks Failing

**Solution:**
1. Review CI logs in GitHub Actions tab
2. Identify which check failed (lint/type/test)
3. Re-run that phase locally:
   - Linting: `ruff check . --fix && ruff format .`
   - Type checking: `mypy . --config-file mypy.ini`
   - Tests: `pytest -vv`
4. Fix the issue
5. Commit and push:
   ```bash
   git add -A
   git commit -m "fix: resolve [check-name] failure"
   git push
   ```
6. CI automatically re-runs and auto-merges when passing

**Note:** CI failures should be rare since Phase 5 (Testing) and Phase 6 (Quality) validate locally.

### Issue: Auto-Merge Not Triggering

**Verify GitHub Settings:**
```bash
# Check if auto-merge is enabled on PR
gh pr view --json autoMergeRequest

# Enable auto-merge if not set
gh pr merge --auto --squash
```

**Common causes:**
- Branch protection rules not configured (see Required GitHub Settings)
- Required status checks not defined in branch protection
- PR not marked for auto-merge (missing `--auto-merge` flag)
- Checks still running (wait for completion)

## Validation Steps

After auto-merge completes:

1. **Verify merge on GitHub:**
   ```bash
   gh pr view [PR-number]
   # Status should show: "Merged"
   ```
   - PR shows as merged (purple badge)
   - Squashed commit appears in main branch
   - Feature branch automatically deleted

2. **Verify local sync:**
   ```bash
   git checkout main
   git pull origin main
   git log --oneline -5
   # Your commit should appear in history
   ```

3. **Verify deployment (if auto-deploy configured):**
   - Check GitHub Actions deployment workflow
   - Verify function app running
   - Test deployed endpoints

**Success Indicators:**
- ✅ PR merged automatically without manual intervention
- ✅ All CI checks passed
- ✅ Feature branch deleted
- ✅ Local main branch synced
- ✅ Changes deployed (if configured)

State: "Phase 8 complete. Changes automatically committed, validated by CI, and merged to main."

## Related Resources

- [Development Process](./development-process.prompt.md) — Eight-phase workflow
- [Conventional Commits](https://www.conventionalcommits.org/) — Commit message standard
- [GitHub CLI Documentation](https://cli.github.com/manual/) — gh command reference
- [GitHub Actions](https://docs.github.com/en/actions) — CI/CD documentation
- [GitHub Auto-Merge](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request) — Auto-merge configuration
