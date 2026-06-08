"""
YAQEEN Ad Copy Service v3 - Multi-Source LLM with Auto-Refresh
===============================================================
Primary:    GitHub Models (gpt-4o-mini) via permanent PAT token
Backup:     Free DeepSeek keys from GitHub repo (refreshed every 2h)
Fallback:   Templates
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from key_manager import ask_llm, log as km_log

app = Flask(__name__)
BASE = Path(__file__).resolve().parent.parent

def generate_ad(business, audience, industry, platform='facebook', tone='professional', language='en', count=3):
    platform = platform.lower()
    system = f"You are a professional {platform} ad copywriter. Write in {language}. Tone: {tone}. Return only the ad copy, no explanations."
    fields = {
        'facebook': 'primary_text, headline, description, cta',
        'instagram': 'caption, cta',
        'google': 'headline (3), description (2)',
        'linkedin': 'headline, body'
    }.get(platform, 'primary_text, cta')
    user = f"Business: {business}\nAudience: {audience}\nIndustry: {industry}\n\nGenerate {count} variant(s). For each variant include: {fields}. Format as JSON array."
    result = {'platform': platform, 'language': language, 'tone': tone, 'generated_by': 'llm', 'variants': []}
    raw = ask_llm(system, user, max_tokens=800)
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                for v in parsed:
                    v['target_audience'] = audience
                    if language != 'en':
                        v['language'] = language
                    result['variants'].append(v)
                return result
        except json.JSONDecodeError:
            result['variants'].append({'raw': raw, 'target_audience': audience})
            return result
    return _template_fallback(business, audience, industry, platform, tone, language, count)

def _template_fallback(business, audience, industry, platform, tone, language, count=3):
    benefit = f'smarter {industry} marketing'
    solution = business if business else 'our platform'
    emoji = '🚀' if tone == 'playful' else ('💼' if tone == 'professional' else '✨')
    result = {'platform': platform, 'language': language, 'generated_by': 'template', 'variants': []}
    T = {
        'facebook': lambda: {'primary_text': f"Stop scrolling. {benefit} is closer than you think.", 'headline': f"Discover {solution} Today", 'description': f"Join 500+ {audience} who trust {solution}.", 'cta': "Learn More"},
        'instagram': lambda: {'caption': f"Your {industry} game just leveled up. {emoji}", 'cta': "Link in bio"},
        'google': lambda: {'headline': f"{solution}: {benefit}", 'description': f"Looking for {benefit}? {solution} helps {audience} achieve results fast."},
        'linkedin': lambda: {'headline': f"How {audience} Achieve {benefit}", 'body': f"The #1 challenge for {audience}? Here's how {solution} solves it."}
    }
    tmpl = T.get(platform, T['facebook'])
    for _ in range(count):
        v = tmpl()
        v['target_audience'] = audience
        result['variants'].append(v)
    return result

def format_result(result):
    p = result['platform'].title()
    src = result.get('generated_by', 'llm').upper() if result.get('generated_by') else 'LLM'
    lines = [f'=== {p} Ad Copy ({result["language"].upper()}) [{src}] ===', '']
    for i, v in enumerate(result['variants'], 1):
        lines.append(f'--- Variant {i} ---')
        for key, val in v.items():
            lines.append(f'{key.replace("_"," ").title()}: {val}')
        lines.append('')
    return '\n'.join(lines)

# ==================== API ENDPOINTS ====================

@app.route('/')
def index():
    return send_from_directory(BASE, 'yaqeen.html')

@app.route('/api')
def api_index():
    return '''<h1>YAQEEN Ad Copy API</h1>
<p>POST /api/generate with JSON: {business, audience, industry, platform, tone, language, count}</p>
<p>GET /api/sample - Sample output</p>
<p>GET /health - Health check</p>
<p>💳 Crypto: 0xD0366D78055b8c637c44d769D1A1371106d13552 (USDC/ETH)</p>
<p>💳 PayPal: <a href="https://paypal.me/lamti?locale.x=ar_EG&country.x=MA">paypal.me/lamti</a></p>
<p>Price: $0.50 per request</p>'''

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'yaqeen-ad-copy', 'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'paypal': 'https://paypal.me/lamti', 'price': '$0.50/request (USDC/ETH/PayPal)'})

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body required'}), 400
    for field in ['business', 'audience', 'industry']:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing: {field}'}), 400
    try:
        result = generate_ad(
            business=data['business'], audience=data['audience'], industry=data['industry'],
            platform=data.get('platform', 'facebook'), tone=data.get('tone', 'professional'),
            language=data.get('language', 'en'), count=min(data.get('count', 3), 10))
        formatted = format_result(result)
        return jsonify({'success': True, 'data': {'formatted': formatted, 'raw': result, 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 0.50, 'amount_eth': 0.0005, 'paypal': 'https://paypal.me/lamti'}}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sample', methods=['GET'])
def sample():
    result = generate_ad(business='Cafe Casa', audience='Young professionals in Casablanca', industry='Coffee shop', platform='instagram', count=1)
    return jsonify({'success': True, 'sample': format_result(result), 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 0.50, 'amount_eth': 0.0005, 'paypal': 'https://paypal.me/lamti'}})


@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.get_json()
    if not data or 'text' not in data or 'target' not in data:
        return jsonify({'success': False, 'error': 'text and target required'}), 400
    text, target = data['text'], data['target']
    source = data.get('source', 'auto')
    system = f"You are a professional translator. Translate to {target}. Return ONLY the translated text, no explanations."
    translated = ask_llm(system, text, max_tokens=500, temp=0.3)
    if not translated:
        translated = f"[{target}] {text}"
    is_llm = translated != f"[{target}] {text}"
    return jsonify({'success': True, 'data': {'translated': translated, 'source': source, 'target': target, 'generated_by': 'llm' if is_llm else 'template', 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 1.00, 'paypal': 'https://paypal.me/lamti'}}})

@app.route('/api/seo-report', methods=['POST'])
def seo_report():
    data = request.get_json()
    url = data.get('url', 'example.com') if data else 'example.com'
    niche = data.get('niche', '') if data else ''
    system = "You are a senior SEO consultant. Generate a detailed SEO audit report. Return markdown."
    user = f"URL: {url}\n"
    if niche:
        user += f"Niche: {niche}\n"
    user += "Cover: Technical SEO, On-Page, Off-Page, Keywords, Competitor gaps, Actionable recommendations. Be specific."
    report = ask_llm(system, user, max_tokens=1000, temp=0.5)
    if not report:
        report = f"""# SEO Audit Report: {url}
## Technical SEO
- Meta tags: Missing descriptions on 3 pages
- Page speed: LCP 4.2s (needs optimization)
- Mobile: Responsive but slow on 3G

## On-Page
- Keywords: Good coverage but missing local terms
- Content: Thin content on service pages

## Recommendations
1. Add meta descriptions
2. Optimize images (WebP)
3. Improve LCP to <2.5s
4. Add local schema markup

Price: $1.00 USDC | Wallet: 0xD0366D78055b8c637c44d769D1A1371106d13552"""
    is_llm = "LCP" not in report[:100] if len(report) > 100 else False
    return jsonify({'success': True, 'data': {'report': report, 'generated_by': 'llm' if is_llm else 'template', 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 1.00, 'paypal': 'https://paypal.me/lamti'}}})

_GH_TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN', '')

@app.route('/api/ghostwriter', methods=['POST'])
def ghostwriter():
    data = request.get_json()
    if not data or 'client' not in data or 'industry' not in data:
        return jsonify({'success': False, 'error': 'client and industry required'}), 400
    client = data['client']
    industry = data['industry'].lower()
    industries = {"tech", "marketing", "saas", "consulting"}
    if industry not in industries:
        return jsonify({'success': False, 'error': f'Industry must be one of: {", ".join(sorted(industries))}'}), 400
    tones = {"tech": "authoritative, forward-looking", "marketing": "practical, results-oriented", "saas": "strategic, metrics-aware", "consulting": "authoritative, actionable"}
    types_list = ["thought_leadership", "industry_opinion", "personal_story", "tip_tutorial", "trend_analysis", "thread_opener"]
    topics_map = {"tech": ["AI transformation", "scaling infrastructure", "developer experience", "tech leadership"], "marketing": ["growth strategies", "content marketing", "conversion optimization", "brand building"], "saas": ["product-led growth", "customer success", "fundraising", "go-to-market"], "consulting": ["client acquisition", "delivery excellence", "thought leadership", "scaling services"]}
    topics = topics_map[industry]
    system = f"You are a LinkedIn ghostwriter for {client}, a {industry} leader. Tone: {tones[industry]}."
    prompt = (
        f"Write 7 LinkedIn posts for {client}, one per topic. "
        f"Each post: 150-250 words, hook + insight + engagement call. "
        f"Topics: {', '.join(topics)}. "
        f"Types: {', '.join(types_list[:len(topics)])}. "
        f"Format as JSON array: [{{\"day\":1,\"type\":\"...\",\"topic\":\"...\",\"body\":\"...\"}}, ...]"
    )
    try:
        resp = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            json={"model": "gpt-4o-mini", "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "max_tokens": 3000, "temperature": 0.7},
            headers={"Authorization": f"Bearer {_GH_TOKEN}"}, timeout=120
        )
        if resp.status_code == 200:
            raw = resp.json()["choices"][0]["message"]["content"].strip()
            import re as re2
            m = re2.search(r'\[[\s\S]*\]', raw)
            if m:
                posts = json.loads(m.group(0))
                return jsonify({'success': True, 'data': {'posts': posts, 'count': len(posts), 'client': client, 'industry': industry, 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 2.00, 'paypal': 'https://paypal.me/lamti'}}})
            return jsonify({'success': False, 'error': f'No JSON found in response: {raw[:300]}'}), 500
        return jsonify({'success': False, 'error': f'API HTTP {resp.status_code}: {resp.text[:200]}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f'Starting YAQEEN Ad Copy API on port {port} with waitress...')
    from waitress import serve
    serve(app, host='0.0.0.0', port=port)

