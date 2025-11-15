---
description: 'Generate comprehensive documentation for modules, examples, and README updates'
mode: 'agent'
tools: ['read_file', 'write_file']
---

# Documentation — Module, Examples, and README Generation

Create clear, concise, GitHub Flavored Markdown documentation for implemented features including module documentation, practical examples, and README updates.

## Mission

Produce professional, task-focused documentation that enables users to understand, configure, and use new endpoints effectively. Follow GitHub documentation standards with minimal decoration and maximum utility.

## Scope & Preconditions

- **Documentation Areas:**
  - Module documentation (`./docs/modules/[MODULENAME].md`)
  - Example documentation (`./docs/examples/[MODULENAME]-curl.md`)
  - Root README updates (`./README.md`)
- **Format:** GitHub Flavored Markdown (GFM) exclusively
- **Style:** Clear, direct, professional (Microsoft/Azure documentation tone)
- **Authority:** May create/update documentation files after approval
- **Prerequisites:** Testing and linting phases complete

## Inputs

- **Module Name:** Identifier for the implemented feature
- **Endpoint Details:** Routes, methods, parameters, responses
- **Configuration:** Required environment variables and setup
- **Examples:** Sample requests and responses
- **Integration Notes:** How feature fits into existing system

## Documentation Structure

### A) Module Documentation

**File:** `./docs/modules/[MODULENAME].md`

**Purpose:** Explain what the module does, how it integrates, and how to configure it.

**Required Sections:**

1. **Title and Purpose**
   - Module name (H1)
   - Single-sentence purpose statement
   - Brief description (2-3 sentences)

2. **Overview**
   - Capabilities provided
   - External service integration details
   - Key features

3. **Configuration**
   - Required environment variables
   - Setup instructions
   - Authentication details

4. **Usage**
   - Function signatures (if library usage)
   - Integration points
   - Expected inputs/outputs

5. **Architecture Notes** (optional)
   - Design decisions
   - Dependencies
   - Performance considerations

6. **Troubleshooting** (optional)
   - Common issues
   - Error messages and resolutions
   - Known limitations

**Template:**

```markdown
# [Module Name]

Brief purpose statement explaining what this module does.

## Overview

[2-3 sentences describing capabilities and integration]

### Features

- Feature 1 description
- Feature 2 description
- Feature 3 description

## Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `API_KEY` | Yes | Authentication key | `abc123...` |
| `TIMEOUT` | No | Request timeout (seconds) | `30` |

### Setup

```bash
# Add API key using Azure Functions CLI
func settings add MODULE_API_KEY "your-key-here"
```

## Usage

### Function Signature

```python
def handle_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle request with specified parameters.
    
    Args:
        payload: Dict containing request parameters
        
    Returns:
        Dict with status and result/error
    """
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | string | Yes | Input value to process |
| `option` | boolean | No | Optional flag |

### Response Format

**Success:**
```json
{
  "status": "ok",
  "result": {
    "data": "...",
    "metadata": {}
  }
}
```

**Error:**
```json
{
  "status": "error",
  "error": {
    "msg": "Error description"
  }
}
```

## Integration

This module is called from the `/api/module/endpoint` HTTP endpoint defined in `function_app.py`.

## Error Handling

| Error Type | HTTP Status | Description |
|------------|-------------|-------------|
| Missing parameter | 400 | Required parameter not provided |
| Invalid format | 400 | Parameter format validation failed |
| API error | 502 | External service returned error |
| Internal error | 500 | Unexpected error occurred |

## Troubleshooting

### Issue: API Key Not Configured

**Symptom:** Error "API_KEY not configured"

**Solution:**
```bash
func settings add MODULE_API_KEY "your-key"
```

## Related Documentation

- [API Examples](../examples/module-curl.md)
- [Implementation Pattern](../development/implementation-pattern.prompt.md)
```

### B) Example Documentation

**File:** `./docs/examples/[MODULENAME]-curl.md`

**Purpose:** Provide copy-paste curl examples for common use cases.

**Required Sections:**

1. **Title**
2. **Prerequisites**
3. **Basic Example**
4. **Common Use Cases** (multiple examples)
5. **Error Examples**

**Template:**

```markdown
# [Module Name] — curl Examples

Practical examples for calling the `[module]` endpoint using curl.

## Prerequisites

- Azure Function app running locally or deployed
- API key configured (if required)
- curl installed

```bash
# Start function app locally
func start

# Base URL
export BASE_URL="http://localhost:7071"
# Or for deployed:
# export BASE_URL="https://your-app.azurewebsites.net"
```

## Basic Example

### Simple Query

```bash
curl -X GET "${BASE_URL}/api/module/check?value=example.com"
```

**Response:**
```json
{
  "status": "ok",
  "result": {
    "data": "processed result",
    "score": 95
  }
}
```

## Common Use Cases

### Use Case 1: [Scenario Description]

```bash
curl -X POST "${BASE_URL}/api/module/action" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "input",
    "options": {
      "flag": true
    }
  }'
```

**Response:**
```json
{
  "status": "ok",
  "result": {
    "processed": true,
    "details": {}
  }
}
```

### Use Case 2: [Another Scenario]

```bash
curl -X GET "${BASE_URL}/api/module/search?query=term&limit=10"
```

**Response:**
```json
{
  "status": "ok",
  "result": {
    "items": [],
    "total": 0
  }
}
```

## Error Examples

### Missing Required Parameter

```bash
curl -X GET "${BASE_URL}/api/module/check"
```

**Response (400):**
```json
{
  "status": "error",
  "error": {
    "msg": "missing 'value' parameter"
  }
}
```

### Invalid Input Format

```bash
curl -X GET "${BASE_URL}/api/module/check?value=invalid-format"
```

**Response (400):**
```json
{
  "status": "error",
  "error": {
    "msg": "Invalid input format"
  }
}
```

### External API Error

```bash
curl -X GET "${BASE_URL}/api/module/check?value=example.com"
```

**Response (502):**
```json
{
  "status": "error",
  "error": {
    "msg": "API error: Service unavailable"
  }
}
```

## Advanced Usage

### With Authentication Header

```bash
curl -X GET "${BASE_URL}/api/module/check?value=example.com" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

### With Timeout

```bash
curl -X GET "${BASE_URL}/api/module/check?value=example.com" \
  --max-time 30
```

### Pretty-printed JSON Output

```bash
curl -X GET "${BASE_URL}/api/module/check?value=example.com" | jq '.'
```

## Notes

> [!TIP]
> Use `jq` for pretty-printing JSON responses: `curl ... | jq '.'`

> [!IMPORTANT]
> Always validate input data before sending to avoid 400 errors.

> [!WARNING]
> Rate limits may apply to external API calls. Check provider documentation.

## Related Documentation

- [Module Documentation](../modules/module.md)
- [Implementation Details](../implementation/module.md)
```

### C) README Updates

**File:** `./README.md`

**Purpose:** Update root README with new endpoint information.

**Sections to Update:**

1. **Project Description** (if adding first endpoint)
2. **Endpoints Table** (add new row)
3. **Quick Start** (if configuration changes)
4. **Configuration** (add new env vars)

**Endpoints Table Format:**

```markdown
## Endpoints

| Endpoint | Method | Description | Documentation |
|----------|--------|-------------|---------------|
| `/api/module/check` | GET | Check value against service | [Module Docs](./docs/modules/module.md) |
| `/api/module/search` | GET | Search for records | [Module Docs](./docs/modules/module.md) |
```

**Configuration Section:**

```markdown
## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MODULE_API_KEY` | API key for module service | `abc123...` |

### Local Development Setup

```bash
# Add environment variables
func settings add MODULE_API_KEY "your-key-here"

# Start function app
func start
```
```

## Writing Guidelines

### Tone and Style

**Direct and Imperative:**
- ✅ "Configure the API key using func settings"
- ❌ "You might want to configure the API key"

**Short Sentences:**
- ✅ "This endpoint validates IP addresses. It returns reputation scores."
- ❌ "This endpoint is designed to validate IP addresses and will return reputation scores based on various threat intelligence sources."

**Plain English:**
- ✅ "The API returns an error if the key is missing"
- ❌ "The API will instantiate an error condition in the event that the authentication credential is not present in the request context"

**Avoid Jargon:**
- ✅ "API call failed"
- ❌ "HTTP request experienced a non-recoverable fault condition"

### Formatting Standards

**GitHub Admonitions:**

```markdown
> [!NOTE]
> Additional information users should notice.

> [!TIP]
> Helpful advice for better usage.

> [!IMPORTANT]
> Critical information users must understand.

> [!WARNING]
> Urgent information requiring attention.

> [!CAUTION]
> Negative potential consequences of an action.
```

**Code Blocks:**

```markdown
# Always specify language
```bash
curl -X GET "http://localhost:7071/api/endpoint"
```

```python
def example():
    pass
```

```json
{
  "key": "value"
}
```
```

**Tables:**

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value A  | Value B  | Value C  |
```

**Internal Links:**

```markdown
- Relative links: [Documentation](./docs/module.md)
- Anchor links: [Configuration](#configuration)
```

## Approval Workflow

### Step 1: Present Summary

Before creating documentation, show summary:

```
Documentation Plan for [Module Name]:

Files to Create:
1. ./docs/modules/module.md
   - Purpose and overview
   - Configuration (2 env vars)
   - Usage with 3 examples
   - Error handling table

2. ./docs/examples/module-curl.md
   - 5 curl examples
   - 3 error scenarios
   - Advanced usage patterns

3. ./README.md (updates)
   - Add endpoint to table
   - Add env var to configuration
   - Update quick start

Key Sections:
- Module capabilities and integration
- Complete API examples
- Error handling reference

Approve documentation generation? (yes/no)
```

### Step 2: Request Approval

Wait for explicit approval before generating files.

### Step 3: Generate Documentation

After approval, create all three documentation files with complete content.

### Step 4: Confirm Completion

```
Documentation Complete:

Created:
✅ ./docs/modules/module.md (234 lines)
✅ ./docs/examples/module-curl.md (156 lines)
✅ ./README.md (updated)

Summary:
- Module documentation with full configuration
- 5 practical curl examples
- README updated with new endpoint

Next Step: Ready for commit (Phase 7 complete)
```

## Quality Assurance Checklist

- [ ] Module documentation includes all required sections
- [ ] Examples are copy-paste ready and tested
- [ ] README updated with endpoint information
- [ ] All code blocks specify language
- [ ] Tables properly formatted
- [ ] Internal links use relative paths
- [ ] No excessive emojis (max 1 in README header)
- [ ] Tone is direct and professional
- [ ] No grammatical errors or typos
- [ ] Configuration clearly documented
- [ ] Error scenarios covered

## Common Patterns

### API Key Configuration

```markdown
### Configuration

```bash
# Add API key using Azure Functions CLI (recommended)
func settings add MODULE_API_KEY "your-api-key-here"  # pragma: allowlist secret

# Or set environment variable
export MODULE_API_KEY="your-api-key-here"  # pragma: allowlist secret
```
```

### Endpoint Table Entry

```markdown
| `/api/module/action` | GET/POST | Description of action | [Docs](./docs/modules/module.md) | [Examples](./docs/examples/module-curl.md) |
```

### Success Response Example

```markdown
**Response (200):**
```json
{
  "status": "ok",
  "result": {
    "data": "value",
    "metadata": {
      "timestamp": "2024-01-01T00:00:00Z"
    }
  }
}
```
```

### Error Response Example

```markdown
**Response (400 Bad Request):**
```json
{
  "status": "error",
  "error": {
    "msg": "missing 'value' parameter"
  }
}
```
```

## Validation Steps

After generating documentation:

1. **Verify files created:**
   ```bash
   ls -l docs/modules/[module].md
   ls -l docs/examples/[module]-curl.md
   git diff README.md
   ```

2. **Check formatting:**
   - Markdown renders correctly in GitHub preview
   - Code blocks have language specified
   - Tables align properly
   - Links resolve correctly

3. **Test examples:**
   - Copy curl commands and verify they work
   - Check response formats match actual API
   - Ensure error examples are accurate

4. **Review content:**
   - No spelling errors
   - Clear and concise language
   - Professional tone throughout
   - All required sections present

## Related Resources

- [Development Process](./development-process.prompt.md) — Seven-phase workflow
- [Implementation Pattern](./implementation-pattern.prompt.md) — Module structure
- [GitHub Flavored Markdown](https://github.github.com/gfm/) — Official GFM spec
- [GitHub Admonitions](https://github.com/orgs/community/discussions/16925) — Alert syntax
