# Debugging Guide for Jira Webhook Validation Errors

## Overview
This guide explains how to debug 422 Unprocessable Entity errors when receiving Jira webhooks.

## New Debugging Features

### 1. Custom Validation Error Handler
When a webhook payload fails validation (422 error), the application now logs:
- Request method and URL path
- Query parameters
- Request headers
- **Raw request body** (the actual JSON payload received)
- **Detailed validation errors** (which fields are missing/invalid)

### 2. Debug Logging in Webhook Endpoint
When a webhook is successfully validated, the application logs:
- Client IP address
- Query parameters
- Request headers
- The validated payload structure

## How to Enable Debug Logging

### Option 1: Environment Variable
Set the `LOG_LEVEL` environment variable to `DEBUG`:

```bash
export LOG_LEVEL=DEBUG
```

Or add to your `.env` file:
```
LOG_LEVEL=DEBUG
```

### Option 2: Docker Compose
Update `docker-compose.yml`:

```yaml
services:
  webhook-api:
    environment:
      - LOG_LEVEL=DEBUG
```

### Option 3: Temporary (Current Session)
```bash
LOG_LEVEL=DEBUG python -m uvicorn app.main:app --reload
```

## Understanding the Logs

### For 422 Validation Errors

When you see a 422 error, the logs will now show:

```
ERROR - Validation error for POST /webhook/jira
ERROR - Query params: {'triggeredByUser': '557058:9116cb26-9a2b-417f-9b5a-d271fc166d6d'}
ERROR - Headers: {'host': 'your-server.com', 'content-type': 'application/json', ...}
ERROR - Raw body: {"timestamp": 1713782400000, "webhookEvent": "jira:issue_created", ...}
ERROR - Validation errors: [
    {
        'type': 'missing',
        'loc': ('body', 'issue', 'fields', 'priority'),
        'msg': 'Field required',
        'input': {...}
    }
]
```

**Key Information:**
- **Raw body**: Shows the exact JSON received from Jira
- **Validation errors**: Shows which fields are missing or have wrong types
  - `loc`: The path to the problematic field (e.g., `('body', 'issue', 'fields', 'priority')`)
  - `type`: Error type (`missing`, `type_error`, etc.)
  - `msg`: Human-readable error message

### For Successful Requests (DEBUG mode)

```
DEBUG - Received webhook request from 104.192.142.240
DEBUG - Query params: {'triggeredByUser': '557058:9116cb26-9a2b-417f-9b5a-d271fc166d6d'}
DEBUG - Headers: {...}
INFO - Processing Jira webhook event: jira:issue_created for issue PROJ-123
DEBUG - Payload: {
  "timestamp": 1713782400000,
  "webhookEvent": "jira:issue_created",
  ...
}
```

## Common Validation Issues

### 1. Missing Required Fields
**Error**: `'type': 'missing', 'loc': ('body', 'issue', 'fields', 'priority')`

**Solution**: The Jira webhook is not sending the `priority` field. Options:
- Make the field optional in the model: `priority: Optional[Priority] = None`
- Configure Jira to include the field in webhooks
- Check if different webhook events have different structures

### 2. Wrong Data Type
**Error**: `'type': 'int_parsing', 'loc': ('body', 'timestamp')`

**Solution**: The field is receiving a string instead of an integer. Check the actual payload format.

### 3. Extra Fields
Pydantic ignores extra fields by default, so this shouldn't cause errors unless you've changed the model configuration.

## Troubleshooting Steps

1. **Enable DEBUG logging** (see above)

2. **Trigger a webhook from Jira** to your endpoint

3. **Check the logs** for the validation error details

4. **Compare the raw body** with the expected model structure in `app/models/jira.py`

5. **Identify the mismatch**:
   - Missing fields → Make them optional or ensure Jira sends them
   - Wrong types → Update the model to match actual data types
   - Different structure → Restructure the model to match Jira's payload

6. **Update the model** in `app/models/jira.py` based on findings

7. **Test again** with the updated model

## Example: Making Fields Optional

If you find that certain fields are not always present in Jira webhooks:

```python
# Before (required)
class IssueFields(BaseModel):
    priority: Priority

# After (optional)
class IssueFields(BaseModel):
    priority: Optional[Priority] = None
```

## Viewing Logs

### Docker Compose
```bash
docker-compose logs -f webhook-api
```

### Local Development
Logs appear in the terminal where you run the application.

### Production
Check your container orchestration platform's logging system (e.g., Kubernetes logs, AWS CloudWatch, etc.).

## Security Note

When `LOG_LEVEL=DEBUG`, the raw request body is included in error responses. In production:
- Use `LOG_LEVEL=INFO` to avoid exposing sensitive data in API responses
- The detailed logs will still be written to your logging system
- Only enable DEBUG temporarily when troubleshooting

## Next Steps

After identifying the issue:
1. Update the Pydantic models in `app/models/jira.py`
2. Test with actual Jira webhooks
3. Document any Jira-specific webhook variations
4. Consider creating different models for different webhook event types if structures vary significantly