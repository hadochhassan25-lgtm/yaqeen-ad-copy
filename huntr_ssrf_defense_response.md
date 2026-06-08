# SSRF Defense Response — huntr-helper

## الرد: SSRF في VisitWebpageTool ليست Blind

### Point 1: This is NOT a blind SSRF

The response content is **returned to the attacker**. Code evidence from `default_tools.py:528-531`:

```python
def forward(self, url: str) -> str:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    markdown_content = markdownify(response.text).strip()
    return self._truncate_content(markdown_content, self.max_output_length)
```

`response.text` is parsed and returned as a string to the caller. An attacker sees the full content.

### Point 2: Concrete attack — AWS metadata exfiltration

```python
agent.run("What's at http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2?")
```

The agent calls `VisitWebpageTool("http://169.254.169.254/latest/meta-data/...")` and returns AWS credentials in the response. This is **valid, high-impact SSRF with information disclosure**.

### Point 3: No validation whatsoever

- No IP blocklist (no filtering of 127.0.0.1, 10.x, 172.16-31.x, 192.168.x)
- No scheme restriction (accepts file://, gopher://, dict:// through redirect chains)
- No redirect limit (requests.get follows redirects by default — `allow_redirects=True`)
- No DNS rebinding protection

### Point 4: OWASP classification

This meets the exact definition of SSRF (A10 in OWASP Top 10 2021, and highly relevant in OWASP Agentic Top 10 2026):
- Attacker controls the URL → server makes request → response returned to attacker
- Three criteria met: (1) user-supplied URL, (2) server-side request, (3) response exfiltration

### Point 5: Comparison with accepted CVEs

- CVE-2024-10044 (FastChat SSRF, huntr): Similar vector — user input → HTTP request → response. Accepted and published.
- CVE-2024-9309 (LLaVA SSRF, huntr): Same pattern. Accepted.

This report clearly qualifies as High severity (CVSS 7.5), not informative.
