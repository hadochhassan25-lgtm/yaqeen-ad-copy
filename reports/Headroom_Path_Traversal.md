# Headroom — Arbitrary File Read via Path Traversal in `headroom_read` MCP Tool

**Report ID:** YAQEEN-HEADROOM-001
**Severity:** High (CVSS 7.5)
**Affected File:** `headroom/ccr/mcp_server.py:757-803`
**CWE:** CWE-22 (Path Traversal)
**Researcher:** Yaqeen / Manadger Tech

---

## Summary

Headroom's `headroom_read` MCP tool reads files from the filesystem using a user-supplied `file_path` parameter with no directory confinement. An attacker who can influence the tool's arguments (e.g. via prompt injection in an LLM agent session) can read arbitrary files on the host system, including SSH keys, cloud credentials, environment files, and other sensitive data.

---

## Vulnerability Details

**File:** `headroom/ccr/mcp_server.py` (lines 757-803)

```python
async def _handle_read(self, arguments: dict[str, Any]) -> list[TextContent]:
    file_path = arguments.get("file_path", "")
    ...
    path = Path(file_path).expanduser().resolve()   # <-- No directory confinement
    if not path.exists():
        return error("File not found")
    if not path.is_file():
        return error("Not a file")
    content = safe_decode_for_logging(path.read_bytes())  # <-- File read
    ...
```

The `file_path` parameter is taken directly from the tool call arguments, resolved via `Path().expanduser().resolve()`, and read with no check that the path stays within an allowed directory (e.g. project workspace, temp directory).

Path traversal sequences like `../../../etc/shadow` are fully supported:
- `expanduser()` resolves `~` to the home directory
- `resolve()` resolves `..` and symlinks
- No call to `relative_to()`, `commonpath()`, or any containment check

### Attack Vector

1. **Prompt Injection** — An attacker crafts a message that causes the LLM agent to call `mcp__headroom__headroom_read` with a malicious `file_path`
2. **Direct API Access** — Any process that can send JSON-RPC messages to the MCP server can read arbitrary files
3. **Connected MCP Client** — Any client connected to this MCP server

### PoC

```json
{
    "tool": "mcp__headroom__headroom_read",
    "arguments": {
        "file_path": "/etc/shadow"
    }
}
```

Or using path traversal:

```json
{
    "tool": "mcp__headroom__headroom_read",
    "arguments": {
        "file_path": "../../../etc/shadow"
    }
}
```

Or using home directory expansion:

```json
{
    "tool": "mcp__headroom__headroom_read",
    "arguments": {
        "file_path": "~/.ssh/id_rsa"
    }
}
```

### Impact

- **SSH private key leakage**: `~/.ssh/id_rsa`, `~/.ssh/id_ed25519`
- **Cloud credential leakage**: `~/.aws/credentials`, `~/.gcloud/`, `~/.config/gcloud/`
- **Environment variable leakage**: `.env` files with API keys, database passwords
- **System file reading**: `/etc/shadow`, `/etc/ssl/private/`, `/proc/self/environ`
- **Source code access**: Any file on the filesystem readable by the process user

### Suggested Fix

Add a directory confinement check:

```python
ALLOWED_ROOTS = [
    Path("/workspace").resolve(),
    Path.home() / ".headroom",
]

async def _handle_read(self, arguments):
    file_path = arguments.get("file_path", "")
    path = Path(file_path).expanduser().resolve()
    
    # Confine to allowed roots
    allowed = False
    for root in ALLOWED_ROOTS:
        try:
            path.relative_to(root)
            allowed = True
            break
        except ValueError:
            continue
    
    if not allowed:
        return error("Access denied: path outside allowed directories")
    ...
```

---

## Timeline

- **2026-06-07**: Vulnerability discovered and reported
