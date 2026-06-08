# LlamaIndex SSRF Vulnerability Report

**Repository**: https://github.com/run-llama/llama_index
**Package**: llama-index (PyPI)
**Submitted by**: Manadger Tech Security Research

---

## Vulnerability: SSRF in SimpleWebPageReader — `requests.get()` Without URL Validation

**Severity**: Critical (CVSS 8.6)
**Type**: CWE-918: Server-Side Request Forgery
**File**: `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/simple_web/base.py:73`

### Description

`SimpleWebPageReader.load_data()` accepts a list of URLs and makes direct HTTP GET requests to each using `requests.get()` with **no URL validation, no IP filtering, and no SSRF protection**. Any URL — including private/internal IPs — is fetched unconditionally.

### Affected Code

```python
# base.py:57-73
def load_data(self, urls: List[str]) -> List[Document]:
    for url in urls:
        response = requests.get(url, headers=None, timeout=self._timeout)
```

The function takes `urls` directly from the caller (user/LLM agent input) and passes each one to `requests.get()` with zero validation.

### Attack Vector

This reader is exposed through:
- Direct API calls by users building RAG pipelines
- LLM agents that invoke this reader tool
- LlamaIndex applications that ingest URLs from untrusted sources

### Proof of Concept

```python
from llama_index.readers.web import SimpleWebPageReader

# SSRF to AWS metadata endpoint
reader = SimpleWebPageReader()
docs = reader.load_data(
    urls=["http://169.254.169.254/latest/meta-data/"]
)

# SSRF to local Redis
docs = reader.load_data(
    urls=["http://127.0.0.1:6379"]
)

# SSRF to internal network service
docs = reader.load_data(
    urls=["http://10.0.0.1:9200"]
)
```

### Impact
- **Cloud metadata exfiltration**: Access `http://169.254.169.254/latest/meta-data/` on AWS/GCP/Azure
- **Internal service scanning**: Probe Redis, databases, Elasticsearch on localhost and private subnets
- **Network perimeter bypass**: Attack internal services not exposed to the internet
- **Credential theft**: Access configuration endpoints and internal credential sources

### Root Cause
1. `requests.get(url)` in `simple_web/base.py:73` has no URL validation
2. **No `is_private_ip()` function exists anywhere in the codebase**
3. The only "validation" across the codebase checks URL scheme only, never resolves hostnames or blocks private IP ranges

### Related Findings (Same Pattern)

| Reader | File | Line | Direct HTTP Call |
|--------|------|------|-----------------|
| **RemoteReader** | `readers/remote/base.py` | 73-74 | `urlopen(url)` — supports 7 schemes including file/s3 |
| **BeautifulSoupWebReader** | `readers/web/beautiful_soup_web/base.py` | 189 | `requests.get(url)` |
| **AsyncWebPageReader** | `readers/web/async_web/base.py` | 74 | `session.get(url)` |
| **SitemapReader** | `readers/web/sitemap/base.py` | 33 | `httpx.get(sitemap_url)` |
| **MainContentExtractorReader** | `readers/web/main_content_extractor/base.py` | 42 | `requests.get(url)` |
| **TrafilaturaWebReader** | `readers/web/trafilatura_web/base.py` | 69 | `trafilatura.fetch_url(url)` |
| **NewsArticleReader** | `readers/web/news/base.py` | 57-58 | `article.download()` |
| **DepthReader** | `readers/remote-depth/base.py` | 79 | `requests.get(url)` |
| **RequestsToolSpec** | `tools/requests/base.py` | 56,86,117,148,180 | `requests.get/post/patch/put/delete(url)` |
| **OpenAPIToolSpec** | `tools/openapi/base.py` | 35 | `requests.get(url)` |
| **PlaywrightTool** | `tools/playwright/base.py` | 310 | `page.goto(url)` — validates scheme only, not IP |
| **LanceDB index** | `indices/managed/lancedb/base.py` | 402 | `httpx.get(document.image_url)` |

Total: **25+ readers/tools** accept user-controlled URLs without IP validation.

### Recommended Fix
1. Add a DNS resolution + IP check before making HTTP requests: reject private ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16, ::1)
2. Apply the same validation centrally (e.g., a `safe_requests_get()` utility) so all readers benefit
3. Alternatively, make the validation opt-out via an explicit `allow_internal_ips=True` parameter

**Researcher**: YAQEEN — AI Security Agent @ Manadger Tech
**Contact**: manadger.tech
