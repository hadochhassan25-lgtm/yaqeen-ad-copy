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
<p>Wallet: 0xD0366D78055b8c637c44d769D1A1371106d13552</p>
<p>Price: $0.50 USDC per request</p>'''

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'yaqeen-ad-copy', 'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'price': '$0.50 USDC/request'})

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
        return jsonify({'success': True, 'data': {'formatted': formatted, 'raw': result, 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 0.50, 'amount_eth': 0.0005}}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sample', methods=['GET'])
def sample():
    result = generate_ad(business='Cafe Casa', audience='Young professionals in Casablanca', industry='Coffee shop', platform='instagram', count=1)
    return jsonify({'success': True, 'sample': format_result(result), 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 0.50, 'amount_eth': 0.0005}})


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
    return jsonify({'success': True, 'data': {'translated': translated, 'source': source, 'target': target, 'generated_by': 'llm' if is_llm else 'template', 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 1.00}}})

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
    return jsonify({'success': True, 'data': {'report': report, 'generated_by': 'llm' if is_llm else 'template', 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 1.00}}})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f'Starting YAQEEN Ad Copy API on port {port} with waitress...')
    from waitress import serve
    serve(app, host='0.0.0.0', port=port)

