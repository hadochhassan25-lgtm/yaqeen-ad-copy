# SSRF via Webhook URL — RentAHuman Platform

## Summary

**Vulnerability**: Server-Side Request Forgery (SSRF)  
**Endpoint**: `PATCH /api/keys/{keyId}`  
**Parameter**: `webhookUrl`  
**Impact**: Internal network scanning, cloud metadata access, blind SSRF  
**Severity**: High (8.6)  
**Status**: Untested (requires valid API key)

## Description

RentAHuman's REST API allows API key holders to configure a webhook URL at `PATCH /api/keys/{keyId}` via the `webhookUrl` field. The server then sends HTTP POST requests to this URL for marketplace events (application.received, message.received, etc.).

If the server does not validate:
- Allowed protocols (only https?)
- Internal IP ranges (127.0.0.1, 10.x.x.x, 172.16-31.x.x, 192.168.x.x)
- Cloud metadata endpoints (169.254.169.254)

... then an attacker can use this to probe internal infrastructure.

## Attack Vector

1. Register and obtain a valid API key  
2. PATCH `/api/keys/{keyId}` with `{"webhookUrl": "http://169.254.169.254/latest/meta-data/"}`  
3. Trigger an event that causes a webhook delivery  
4. The server POSTs to the internal metadata endpoint

## Evidence from Documentation

From `https://rentahuman.ai/docs`:

```
PATCH /api/keys/{keyId}
{
  "webhookUrl": "https://your-server.com/webhooks/rentahuman"
}
```

The response includes a `webhookSecret` shown once. Webhook payloads are signed with HMAC-SHA256 (`X-RentAHuman-Signature` header). Auto-disabled after 10 consecutive delivery failures.

No mentions of:
- URL validation
- Protocol restriction
- IP blocklist
- Internal network protection

## MCP Package Analysis

In `rentahuman-mcp` v1.12.0 (`dist/serve.js`), the `configure_webhook` tool is documented in the README/instructions but not implemented as an MCP tool. Webhook configuration happens via the REST API only:

```
PATCH /api/keys/{keyId}
```

The `ApiClient.request()` function (serve.js:648) uses `fetch()` with no URL validation on the constructed URL. Endpoints are hardcoded, so no direct SSRF in the package itself, but the platform's backend API sends POSTs to user-supplied webhook URLs.

## Potential Impact

- Cloud metadata exfiltration (AWS/GCP/Azure credentials)
- Internal service discovery and port scanning  
- Access to internal APIs (Firebase Admin, Stripe, etc.)
- Potential RCE chain through internal services

## Recommended Fix

- Validate webhook URLs against an allowlist
- Block private IP ranges (RFC 1918)
- Block cloud metadata endpoints
- Require HTTPS only
- Add network-level egress controls

---

## Additional Findings

### 1. Unauthenticated Data Access
**Endpoints**: `GET /api/humans`, `GET /api/bounties`, `GET /api/services/browse`  
**Status**: Confirmed ✅  
All three endpoints return full data without any authentication. Human profiles include names, locations, skills, hourly rates, and availability schedules. Bounty listings include titles, descriptions, prices, and contact details.

### 2. Rate Limiting
**Header**: `x-ratelimit-limit: 600` per window  
**Status**: Confirmed ✅  
Rate limiting is IP-based. No CAPTCHA or additional challenge for unauthenticated users. Enables data scraping at scale.

### 3. CORS Configuration
**Header**: `access-control-allow-origin: https://rentahuman.ai`  
**Status**: Confirmed ✅  
Restrictive CORS prevents browser-based cross-origin attacks but does not protect against server-side or non-browser clients.

### 4. Agent Registration Deprecated
**Endpoint**: `POST /api/agents/register`  
**Status**: Confirmed ✅  
Returns: `{"success":false,"error":"Agent self-registration is deprecated..."}`  
Registration now requires Firebase auth through the web frontend.

### 5. Missing Content-Security-Policy
**Status**: Not directly tested  
The frontend uses Next.js with inline scripts and nonces, but no CSP header was observed.
