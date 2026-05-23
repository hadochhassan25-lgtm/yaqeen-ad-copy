"""
YAQEEN Ad Copy Service - Single File Deployment
===============================================
Deploy anywhere: pip install flask && python app.py
Or deploy on PythonAnywhere/Render/Railway for free.
"""
import sys, io, os, json, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path

app = Flask(__name__)
BASE = Path(__file__).resolve().parent.parent

@app.after_request
def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

# ==================== AD COPY ENGINE ====================
TEMPLATES = {
    'facebook': {
        'primary_text': [
            "Stop scrolling. {benefit} is closer than you think.",
            "Your customers are looking for {benefit}. Show them you exist.",
            "Most {audience} don't know they need {benefit}. Yet.",
            "The #1 mistake {audience} make? Ignoring {benefit}."
        ],
        'headline': ["Discover {solution} Today", "Why {audience} Choose {solution}", "{benefit} — Made Simple"],
        'description': ["Join {count}+ {audience} who trust {solution}. See results in days.",
                        "Built for {audience}. {solution} delivers {benefit} without the headache."],
        'cta': ["Get Started Free", "Learn More", "Try It Now", "Book a Demo"]
    },
    'instagram': {
        'caption': ["Your {industry} game just leveled up. {emoji}",
                    "POV: You found {solution} for {audience}. {emoji}",
                    "Stop guessing. Start {benefit}. {emoji}"],
        'cta': ["Link in bio", "DM us", "Tag someone who needs this", "Swipe up"]
    },
    'google': {
        'headline': ["{solution}: {benefit}", "Best {solution} for {audience}", "Top-Rated {solution}"],
        'description': ["Looking for {benefit}? {solution} helps {audience} achieve results fast.",
                        "Trusted by {count}+ {audience}. Get {benefit} with {solution}."]
    },
    'linkedin': {
        'headline': ["How {audience} Achieve {benefit}", "Scaling {industry}? Here's Your Playbook"],
        'body': ["The #1 challenge for {audience}? {pain_point}. Here's how {solution} solves it.",
                 "Organizations using {solution} see {x}% improvement in {metric}. That's {benefit}."]
    }
}

def generate_ad(business, audience, industry, platform='facebook', tone='professional', language='en', count=3):
    platform = platform.lower()
    if platform not in TEMPLATES:
        platform = 'facebook'
    benefit = f'smarter {industry} marketing'
    solution = business if business else 'our platform'
    pain_point = f'ineffective {industry} advertising'
    emoji = '🚀' if tone == 'playful' else ('💼' if tone == 'professional' else '✨')
    result = {'platform': platform, 'language': language, 'variants': []}
    for i in range(count):
        v = {}
        tmpl = TEMPLATES[platform]
        if platform == 'facebook':
            v['primary_text'] = random.choice(tmpl['primary_text']).format(benefit=benefit, audience=audience, solution=solution, industry=industry)
            v['headline'] = random.choice(tmpl['headline']).format(solution=solution, audience=audience, benefit=benefit, industry=industry)
            v['description'] = random.choice(tmpl['description']).format(count=random.randint(100,5000), audience=audience, solution=solution, benefit=benefit)
            v['cta'] = random.choice(tmpl['cta'])
        elif platform == 'instagram':
            v['caption'] = random.choice(tmpl['caption']).format(industry=industry, emoji=emoji, solution=solution, audience=audience, benefit=benefit)
            v['cta'] = random.choice(tmpl['cta'])
        elif platform == 'google':
            v['headline'] = random.choice(tmpl['headline']).format(solution=solution, benefit=benefit, audience=audience)
            v['description'] = random.choice(tmpl['description']).format(benefit=benefit, solution=solution, audience=audience, count=random.randint(100,5000))
        elif platform == 'linkedin':
            v['headline'] = random.choice(tmpl['headline']).format(audience=audience, benefit=benefit, solution=solution, industry=industry)
            v['body'] = random.choice(tmpl['body']).format(audience=audience, pain_point=pain_point, solution=solution, benefit=benefit, x=random.randint(20,80), metric='conversion')
        v['tone'] = tone
        v['target_audience'] = audience
        result['variants'].append(v)
    return result

def format_result(result):
    p = result['platform'].title()
    lines = [f'=== {p} Ad Copy ({result["language"].upper()}) ===', '']
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

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f'Starting YAQEEN Ad Copy API on port {port}...')
    app.run(host='0.0.0.0', port=port, debug=False)
