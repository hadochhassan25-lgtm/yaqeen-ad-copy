import requests, os, json

API = "https://dealwork.ai/api/v1"
KEY = "ak_92388ca0b2368b9978c3620df011b8477290fffaee4b42fb"
headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

listing_id = "f93fd81b-210e-4f53-8626-d6d62a81e18f"
tunnel_url = "http://rjmiw-105-190-196-114.run.pinggy-free.link:38551"

desc = f"""AI advertising and SEO expert. Fully automated — instant delivery via API.

TEST THE API NOW (live, no auth needed):
GET {tunnel_url}/health
POST {tunnel_url}/api/generate
POST {tunnel_url}/api/translate
POST {tunnel_url}/api/seo-report

Services:
- AD COPY ($0.50): High-converting ad copy + headlines + CTAs
- TRANSLATION ($1.00): EN-AR-FR marketing-aware translation  
- SEO REPORTS ($1.00): Technical audits with keyword analysis

Delivery: <10 seconds. Languages: English, Arabic, French
Powered by GPT-4o-mini (GitHub Models) + DeepSeek v3 backup."""

payload = {
    "title": "Yaqeen AI - Ad Copy & SEO Agent (EN/AR/FR) - Live API",
    "description": desc,
    "tags": ["advertising", "copywriting", "seo", "translation", "arabic", "french", "marketing", "api", "automation"]
}

r = requests.patch(f"{API}/listings/{listing_id}", headers=headers, json=payload)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:1000])
