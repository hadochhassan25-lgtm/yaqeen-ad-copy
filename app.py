import sys, io, os, json, random, hashlib, re, html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from flask import Flask, request, jsonify
from pathlib import Path
from datetime import datetime, timezone
import threading, time, requests

app = Flask(__name__)
BASE = Path(__file__).resolve().parent

# ============ FREE API KEYS ============
LLM_API_BASE = 'https://aiapiv2.pekpik.com/v1'
_keys_by_model = {}
_keys_list = []
_last_refresh = 0
_lock = threading.Lock()
REFRESH_INTERVAL = 1800

def fetch_keys():
    try:
        r = requests.get('https://raw.githubusercontent.com/alistaitsacle/free-llm-api-keys/main/README.md', timeout=15)
        if r.status_code != 200:
            return
        text = r.text
        pattern = r'\|\s*`(sk-[A-Za-z0-9]{45,65})`\s*\|\s*([\w\.-]+)\s*\|\s*.*?\|\s*\$?(\d+)\s*\|\s*(\d+)\s*RPM\s*\|\s*(\d{4}-\d{2}-\d{2})'
        matches = re.findall(pattern, text)
        parsed = {}
        all_keys = []
        now = datetime.now()
        for key, model, budget, rpm, exp_date in matches:
            try:
                exp = datetime.strptime(exp_date, '%Y-%m-%d')
                if exp < now:
                    continue
            except:
                continue
            entry = {'key': key, 'model': model, 'budget': int(budget), 'rpm': int(rpm), 'expires': exp_date}
            if model not in parsed:
                parsed[model] = []
            parsed[model].append(entry)
            all_keys.append(entry)
        with _lock:
            _keys_by_model.clear()
            _keys_by_model.update(parsed)
            _keys_list.clear()
            _keys_list.extend(all_keys)
            global _last_refresh
            _last_refresh = time.time()
    except:
        pass

def get_key(model='smart-chat'):
    if time.time() - _last_refresh > REFRESH_INTERVAL:
        fetch_keys()
    with _lock:
        keys = _keys_by_model.get(model, [])
        if not keys:
            keys = _keys_by_model.get('smart-chat', [])
        if not keys:
            for m, ks in _keys_by_model.items():
                keys.extend(ks)
        if keys:
            keys.sort(key=lambda k: k.get('budget', 0), reverse=True)
            return keys[0]['key']
    return None

def get_models():
    if time.time() - _last_refresh > REFRESH_INTERVAL:
        fetch_keys()
    with _lock:
        return {m: len(ks) for m, ks in _keys_by_model.items()}

# ============ AD COPY ENGINE ============
TEMPLATES = {
    'facebook': {
        'primary_text': ["Stop scrolling. {benefit} is closer than you think.", "Your customers are looking for {benefit}. Show them you exist.", "Most {audience} don't know they need {benefit}. Yet.", "The #1 mistake {audience} make? Ignoring {benefit}."],
        'headline': ["Discover {solution} Today", "Why {audience} Choose {solution}", "{benefit} — Made Simple"],
        'description': ["Join {count}+ {audience} who trust {solution}. See results in days.", "Built for {audience}. {solution} delivers {benefit} without the headache."],
        'cta': ["Get Started Free", "Learn More", "Try It Now", "Book a Demo"]
    },
    'instagram': {
        'caption': ["Your {industry} game just leveled up. {emoji}", "POV: You found {solution} for {audience}. {emoji}", "Stop guessing. Start {benefit}. {emoji}"],
        'cta': ["Link in bio", "DM us", "Tag someone who needs this", "Swipe up"]
    },
    'google': {
        'headline': ["{solution}: {benefit}", "Best {solution} for {audience}", "Top-Rated {solution}"],
        'description': ["Looking for {benefit}? {solution} helps {audience} achieve results fast.", "Trusted by {count}+ {audience}. Get {benefit} with {solution}."]
    },
    'linkedin': {
        'headline': ["How {audience} Achieve {benefit}", "Scaling {industry}? Here's Your Playbook"],
        'body': ["The #1 challenge for {audience}? {pain_point}. Here's how {solution} solves it.", "Organizations using {solution} see {x}% improvement in {metric}. That's {benefit}."]
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

# ============ NEWS ENGINE ============
CACHE_FILE = BASE / 'services' / 'news_cache.json'
SOURCES_FILE = BASE / 'services' / 'news_sources.json'
CACHE_TTL = 600
NEWS_CACHE = []

with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
    ALL_SOURCES = json.load(f)

def fetch_rss(url, timeout=8):
    try:
        import feedparser, socket
        socket.setdefaulttimeout(timeout)
        d = feedparser.parse(url)
        if not d.entries:
            return []
        items = []
        for e in d.entries[:12]:
            title = e.get('title', '').strip()
            link = e.get('link', '')
            summary = e.get('summary', e.get('description', ''))
            published = e.get('published', '')
            if title and link:
                items.append({'title': title, 'link': link, 'summary': summary[:500], 'published': published, 'source': url})
        return items
    except:
        return []

def _cache_path():
    p = Path('/tmp/news_cache.json')
    if p.parent.exists():
        return p
    return CACHE_FILE

def fetch_all_news(fast=False):
    global NEWS_CACHE
    now = time.time()
    cache_file = _cache_path()
    try:
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            if now - cached.get('_ts', 0) < CACHE_TTL:
                NEWS_CACHE = [a for a in cached.get('articles', []) if a.get('title')]
                return
    except:
        pass
    if len(NEWS_CACHE) > 0:
        return
    all_articles = []
    max_sources = 1 if fast else 4
    rss_timeout = 3 if fast else 5
    deadline = now + 7.5
    for lang_key, lang_data in ALL_SOURCES.items():
        if lang_key.startswith('_'):
            continue
        if time.time() > deadline:
            break
        for s in lang_data.get('sources', [])[:max_sources]:
            if time.time() > deadline:
                break
            try:
                items = fetch_rss(s['url'], timeout=rss_timeout)
                for it in items:
                    it['source_name'] = s['name']
                    it['source_url'] = s['url']
                    it['lang'] = lang_key
                all_articles.extend(items)
            except:
                pass
    seen = set()
    deduped = []
    for a in all_articles:
        key = a.get('title', '')[:80]
        if key not in seen:
            seen.add(key)
            a['id'] = hashlib.md5(key.encode()).hexdigest()[:12]
            deduped.append(a)
    deduped.sort(key=lambda x: x.get('published', ''), reverse=True)
    NEWS_CACHE = deduped[:200]
    try:
        with open(_cache_path(), 'w', encoding='utf-8') as f:
            json.dump({'_ts': now, 'articles': deduped[:200]}, f, ensure_ascii=False)
    except:
        pass

SYSTEM_PROMPTS = {
    'en': 'You are a professional news editor. Rewrite the following news article in clear, engaging English. Preserve all facts, improve readability, and use a neutral journalistic tone. Output only the rewritten text.',
    'fr': 'Vous êtes un rédacteur de presse professionnel. Réécrivez l\'article suivant dans un français clair et engageant. Préservez tous les faits, améliorez la lisibilité, utilisez un ton journalistique neutre. Répondez uniquement avec le texte réécrit.',
    'es': 'Eres un editor de noticias profesional. Reescribe el siguiente artículo en un español claro y atractivo. Conserva todos los hechos, mejora la legibilidad y usa un tono periodístico neutral. Responde solo con el texto reescrito.',
    'ar': 'أنت محرر أخبار محترف. أعد صياغة المقال التالي بالعربية الفصحى الواضحة. حافظ على جميع الحقائق، حسّن readability، واستخدم نبرة صحفية محايدة. أجب فقط بالنص المعاد صياغته.',
    'zh': '你是一名专业新闻编辑。请用清晰简洁的中文重写以下新闻文章。保留所有事实，提高可读性，使用中立的新闻语气。只输出重写后的文本。'
}

def llm_rewrite(text, lang='en'):
    from openai import OpenAI
    model = 'smart-chat'
    prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS['en'])
    tried = set()
    for _ in range(3):
        key = get_key(model)
        if not key or key in tried:
            break
        tried.add(key)
        try:
            client = OpenAI(base_url=LLM_API_BASE, api_key=key)
            resp = client.chat.completions.create(
                model=model,
                messages=[{'role': 'system', 'content': prompt}, {'role': 'user', 'content': text[:1200]}],
                max_tokens=500, temperature=0.3
            )
            content = resp.choices[0].message.content
            if content and len(content) > 20 and content.strip() != text.strip()[:500]:
                return content.strip()
        except:
            continue
    return None

# ============ CORS ============
@app.after_request
def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

# ============ AD COPY ROUTES ============
@app.route('/ad-copy')
def ad_copy_landing():
    html = BASE / 'yaqeen.html'
    if html.exists():
        return html.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/html; charset=utf-8'}
    return 'YAQEEN Ad Copy Engine — see /api/generate', 200, {'Content-Type': 'text/plain; charset=utf-8'}

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
        lines = [f'=== {result["platform"].title()} Ad Copy ({result["language"].upper()}) ===', '']
        for i, v in enumerate(result['variants'], 1):
            lines.append(f'--- Variant {i} ---')
            for key, val in v.items():
                lines.append(f'{key.replace("_"," ").title()}: {val}')
            lines.append('')
        formatted = '\n'.join(lines)
        return jsonify({'success': True, 'data': {'formatted': formatted, 'raw': result, 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 0.50, 'amount_eth': 0.0005}}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sample', methods=['GET'])
def sample():
    result = generate_ad(business='Cafe Casa', audience='Young professionals in Casablanca', industry='Coffee shop', platform='instagram', count=1)
    lines = [f'=== {result["platform"].title()} Ad Copy ({result["language"].upper()}) ===', '']
    for i, v in enumerate(result['variants'], 1):
        lines.append(f'--- Variant {i} ---')
        for key, val in v.items():
            lines.append(f'{key.replace("_"," ").title()}: {val}')
        lines.append('')
    return jsonify({'success': True, 'sample': '\n'.join(lines), 'payment': {'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552', 'amount_usdc': 0.50, 'amount_eth': 0.0005}})

# ============ NEWS ROUTES ============
@app.route('/api/news')
def get_news():
    if not NEWS_CACHE:
        fetch_all_news(fast=True)
    lang = request.args.get('lang', 'all')
    articles = NEWS_CACHE
    if lang and lang != 'all' and lang in ALL_SOURCES:
        articles = [a for a in articles if a.get('lang') == lang]
    resp = jsonify({'success': True, 'count': len(articles), 'language': lang, 'articles': articles[:50], 'cached_at': datetime.now(timezone.utc).isoformat()})
    resp.headers['Cache-Control'] = 'public, s-maxage=120, max-age=60'
    return resp

@app.route('/api/refresh', methods=['POST'])
def refresh_news():
    NEWS_CACHE.clear()
    fetch_all_news()
    return jsonify({'success': True, 'count': len(NEWS_CACHE), 'message': 'News cache refreshed'})

@app.route('/api/sources')
def get_sources():
    result = {}
    for k, v in ALL_SOURCES.items():
        if k.startswith('_'):
            continue
        result[k] = {'display': v.get('display', k), 'flag': v.get('flag', ''), 'source_count': len(v.get('sources', []))}
    return jsonify({'success': True, 'languages': result, 'total': len(NEWS_CACHE)})

@app.route('/api/rewrite', methods=['POST'])
def rewrite():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body required'}), 400
    text = data.get('text', '').strip()
    lang = data.get('language', 'en')
    if not text:
        return jsonify({'success': False, 'error': 'No text provided'}), 400
    if len(text) < 20:
        return jsonify({'success': False, 'error': 'Text too short (min 20 chars)'}), 400
    try:
        rewritten = llm_rewrite(text, lang) or text
        return jsonify({'success': True, 'original': text[:1000], 'rewritten': rewritten, 'language': lang, 'service': 'YAQEEN News AI'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def _html_esc(s):
    if not s: return ''
    s = str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&#39;')
    return s

# ============ UI & SYSTEM ROUTES ============
@app.route('/')
def index():
    LANG_ORDER = ['en','fr','es','ar','zh']
    lang_opts = ''
    lang_json = ''
    lang_bar_html = '<button class="lang-btn active" onclick="setLang(\'all\',this)">🌐 All</button>'
    nav_dropdown_html = ''
    first_flag = ''
    first_short = 'EN'
    for k in LANG_ORDER:
        v = ALL_SOURCES.get(k)
        if not v:
            continue
        flag = v.get('flag','')
        disp = v.get('display',k)
        short = disp.split(' ')[0]
        if not first_flag:
            first_flag = flag
            first_short = short
        lang_opts += '<option value="'+k+'">'+flag+' '+disp+'</option>'
        lang_json += '"'+k+'":{"display":"'+disp+'","flag":"'+flag+'"},'
        nav_dropdown_html += '<button data-lang="'+k+'" onclick="switchTab(\'news\');setLang(\''+k+'\',this);document.getElementById(\'navLangDropdown\').classList.remove(\'open\')">'+flag+' '+disp+'</button>'
        lang_bar_html += '<button class="lang-btn" data-lang="'+k+'" onclick="setLang(\''+k+'\',this)">'+flag+' '+disp+'</button>'
    lang_json = lang_json.rstrip(',')

    # Try to fetch news for immediate display
    if not NEWS_CACHE:
        fetch_all_news(fast=True)
    initial_articles = NEWS_CACHE[:50]
    grid_html = ''
    for a in initial_articles:
        ld = ALL_SOURCES.get(a.get('lang', ''), {})
        flag = ld.get('flag', '')
        disp = ld.get('display', a.get('lang', ''))
        title = _html_esc(a.get('title', ''))
        summary = _html_esc((a.get('summary', '') or '')[:300])
        source = _html_esc(a.get('source_name', ''))
        link = a.get('link', '')
        aid = a.get('id', '')
        grid_html += '''<div class="card"><div class="card-badge">'''+flag+' '+disp+'''</div>
<div class="card-title">'''+title+'''</div>
<div class="card-summary">'''+summary+'''</div>
<div class="card-meta"><span>'''+source+'''</span><div class="card-actions">
<button class="card-btn" onclick="window.open(\''''+link+'''\',\'_blank\')">🔗 Open</button>
<button class="card-btn primary" onclick="openModal(\''''+aid+'''\')">⟳ Rewrite</button>
</div></div></div>'''

    if grid_html:
        news_section = '<div class="grid">'+grid_html+'</div>'
    else:
        news_section = '<div class="loading" id="initialLoading"><div class="spinner"></div><div>Fetching global news...</div><div id="debugStatus" style="margin-top:12px;font-size:12px;color:var(--text-dim)">connecting...</div></div>'

    articles_json = json.dumps(initial_articles, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<title>YAQEEN — AI Ad Copy + World News</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root {{ --bg: #0a0a0f; --card: #12121a; --card-hover: #181825; --accent: #ff6b35; --accent2: #7c3aed; --gold: #f59e0b; --text: #e8e8ee; --text-dim: #8888a0; --border: #1e1e30; --radius: 12px; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; line-height: 1.6; }}
.nav {{ position: sticky; top: 0; z-index: 100; background: rgba(10,10,15,.85); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }}
.nav-logo {{ font-size: 20px; font-weight: 800; color: var(--accent); }}
.nav-logo span {{ color: var(--gold); }}
.nav-links {{ display: flex; gap: 16px; align-items: center; }}
.nav-links a {{ color: var(--text-dim); text-decoration: none; font-size: 14px; font-weight: 500; transition: color .2s; }}
.nav-links a:hover {{ color: var(--accent); }}
.nav-lang {{ position: relative; margin-left: 8px; padding-left: 8px; border-left: 1px solid var(--border); }}
.nav-lang-btn {{ background: var(--card); border: 1px solid var(--border); color: var(--text); cursor: pointer; font-size: 13px; padding: 4px 10px; border-radius: 6px; transition: all .2s; line-height: 1; font-family: inherit; font-weight: 500; }}
.nav-lang-btn:hover {{ border-color: var(--accent); }}
.nav-lang-dropdown {{ display: none; position: absolute; top: 100%; right: 0; margin-top: 4px; background: var(--card); border: 1px solid var(--border); border-radius: 8px; min-width: 140px; box-shadow: 0 8px 32px rgba(0,0,0,.4); z-index: 200; overflow: hidden; }}
.nav-lang-dropdown.open {{ display: block; }}
.nav-lang-dropdown button {{ display: block; width: 100%; text-align: left; background: none; border: none; color: var(--text-dim); padding: 8px 14px; font-size: 13px; cursor: pointer; font-family: inherit; transition: all .1s; }}
.nav-lang-dropdown button:hover {{ background: rgba(255,107,53,.1); color: var(--accent); }}
.nav-lang-dropdown button.active {{ color: var(--accent); background: rgba(255,107,53,.08); border-left: 2px solid var(--accent); }}
.tabs {{ display: flex; gap: 0; padding: 0 24px; background: rgba(10,10,15,.5); border-bottom: 1px solid var(--border); }}
.tab {{ padding: 12px 24px; cursor: pointer; font-size: 14px; font-weight: 500; color: var(--text-dim); border-bottom: 2px solid transparent; transition: all .2s; background: none; border-top: none; border-left: none; border-right: none; font-family: inherit; }}
.tab:hover {{ color: var(--text); }}
.tab.active {{ color: var(--accent); border-bottom-color: var(--accent); }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}
.lang-bar {{ display: flex; gap: 6px; padding: 12px 24px; overflow-x: auto; scrollbar-width: none; background: rgba(10,10,15,.5); border-bottom: 1px solid var(--border); }}
.lang-btn {{ background: var(--card); border: 1px solid var(--border); color: var(--text-dim); padding: 8px 18px; border-radius: 20px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all .2s; white-space: nowrap; font-family: inherit; }}
.lang-btn:hover {{ border-color: var(--accent); color: var(--text); }}
.lang-btn.active {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 16px 24px 80px; }}
.hero {{ text-align: center; padding: 40px 20px 30px; background: linear-gradient(135deg, rgba(124,58,237,.08) 0%, rgba(255,107,53,.08) 100%); border-radius: var(--radius); margin-bottom: 24px; border: 1px solid var(--border); }}
.hero h1 {{ font-size: 32px; font-weight: 800; margin-bottom: 8px; }}
.hero h1 span {{ background: linear-gradient(135deg, var(--accent), var(--accent2), var(--gold)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.hero p {{ color: var(--text-dim); font-size: 16px; max-width: 600px; margin: 0 auto; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; margin-top: 16px; }}
.card {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; transition: all .25s; display: flex; flex-direction: column; position: relative; overflow: hidden; }}
.card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--accent), var(--accent2)); opacity: 0; transition: opacity .25s; }}
.card:hover {{ background: var(--card-hover); border-color: var(--accent); transform: translateY(-2px); }}
.card:hover::before {{ opacity: 1; }}
.card-badge {{ display: inline-flex; align-items: center; gap: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--gold); margin-bottom: 8px; letter-spacing: .5px; }}
.card-title {{ font-size: 16px; font-weight: 600; line-height: 1.4; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
.card-summary {{ font-size: 13px; color: var(--text-dim); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 12px; flex: 1; }}
.card-meta {{ display: flex; align-items: center; justify-content: space-between; font-size: 12px; color: var(--text-dim); padding-top: 12px; border-top: 1px solid var(--border); margin-top: auto; }}
.card-actions {{ display: flex; gap: 8px; }}
.card-btn {{ background: transparent; border: 1px solid var(--border); color: var(--text); padding: 6px 14px; border-radius: 8px; cursor: pointer; font-size: 12px; font-weight: 500; transition: all .2s; font-family: inherit; }}
.card-btn:hover {{ border-color: var(--accent); background: rgba(255,107,53,.1); }}
.card-btn.primary {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
.ad-form {{ max-width: 600px; margin: 0 auto; padding: 24px; }}
.ad-form label {{ display: block; font-size: 13px; font-weight: 600; color: var(--text-dim); margin-bottom: 6px; margin-top: 16px; }}
.ad-form input, .ad-form select {{ width: 100%; background: var(--card); border: 1px solid var(--border); color: var(--text); padding: 10px 16px; border-radius: 8px; font-size: 14px; font-family: inherit; }}
.ad-form input:focus, .ad-form select:focus {{ outline: none; border-color: var(--accent); }}
.ad-form .submit-btn {{ background: var(--accent); border: none; color: #fff; padding: 12px 32px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; margin-top: 24px; width: 100%; font-family: inherit; transition: all .2s; }}
.ad-form .submit-btn:hover {{ background: #e55a2b; }}
.ad-result {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; margin-top: 24px; white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; display: none; }}
.service-cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; max-width: 800px; margin: 40px auto; }}
.service-card {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 32px; text-align: center; transition: all .25s; }}
.service-card:hover {{ border-color: var(--accent); transform: translateY(-2px); }}
.service-card h3 {{ font-size: 20px; margin-bottom: 8px; }}
.service-card p {{ color: var(--text-dim); font-size: 14px; margin-bottom: 16px; }}
.service-card .price {{ color: var(--gold); font-size: 24px; font-weight: 800; }}
.loading {{ display: flex; align-items: center; justify-content: center; min-height: 300px; flex-direction: column; gap: 16px; color: var(--text-dim); }}
.spinner {{ width: 40px; height: 40px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin .8s linear infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.modal-overlay {{ position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,.7); backdrop-filter: blur(4px); z-index: 1000; display: none; align-items: center; justify-content: center; padding: 20px; }}
.modal-overlay.open {{ display: flex; }}
.modal {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; max-width: 700px; width: 100%; max-height: 85vh; overflow-y: auto; padding: 32px; }}
.modal-close {{ float: right; background: none; border: none; color: var(--text-dim); font-size: 24px; cursor: pointer; }}
.modal h2 {{ font-size: 22px; margin-bottom: 6px; }}
.modal .label {{ font-size: 12px; font-weight: 600; color: var(--gold); text-transform: uppercase; letter-spacing: 1px; margin-top: 20px; margin-bottom: 8px; }}
.modal .original, .modal .rewritten {{ background: rgba(255,255,255,.03); border-radius: 8px; padding: 16px; font-size: 14px; line-height: 1.7; white-space: pre-wrap; }}
.modal .rewritten {{ border-left: 3px solid var(--accent); }}
.modal select {{ background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px 16px; border-radius: 8px; font-size: 14px; margin-right: 8px; font-family: inherit; cursor: pointer; }}
.modal .rewrite-btn {{ background: var(--accent); border: none; color: #fff; padding: 8px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; font-family: inherit; }}
.modal .rewrite-btn:disabled {{ opacity: .5; cursor: wait; }}
.footer {{ text-align: center; padding: 32px 24px; color: var(--text-dim); font-size: 13px; border-top: 1px solid var(--border); margin-top: 40px; }}
.footer a {{ color: var(--accent); text-decoration: none; }}
.error-state {{ text-align: center; padding: 60px 20px; color: var(--text-dim); }}
.error-state h2 {{ color: var(--accent); margin-bottom: 8px; font-size: 20px; }}
.error-state p {{ font-size: 14px; margin-bottom: 16px; }}
.retry-btn {{ background: var(--accent); border: none; color: #fff; padding: 10px 28px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; font-family: inherit; transition: background .2s; }}
.retry-btn:hover {{ background: #e55a2b; }}
@media (max-width: 640px) {{ .grid {{ grid-template-columns: 1fr; }} .service-cards {{ grid-template-columns: 1fr; }} .hero h1 {{ font-size: 24px; }} .container {{ padding: 12px 16px 60px; }} }}
</style>
</head>
<body>
<div class="nav">
    <div class="nav-logo">YAQEEN <span>AI</span></div>
    <div class="nav-links">
        <a href="#" onclick="switchTab('news',this);return false">News</a>
        <a href="#" onclick="switchTab('adcopy',this);return false">Ad Copy</a>
        <a href="/api">API</a>
        <a href="/health">Health</a>
        <div class="nav-lang">
            <button class="nav-lang-btn" id="navLangBtn" onclick="document.getElementById('navLangDropdown').classList.toggle('open')">''' + first_flag + ' ' + first_short + ''' ▾</button>
            <div class="nav-lang-dropdown" id="navLangDropdown">''' + nav_dropdown_html + '''</div>
        </div>
    </div>
</div>

<div class="tabs">
    <button class="tab active" onclick="switchTab('news')">🌐 World News</button>
    <button class="tab" onclick="switchTab('adcopy')">📢 Ad Copy Generator</button>
</div>

<div id="tab-news" class="tab-content active">
    <div class="lang-bar">''' + lang_bar_html + '''</div>
    <div class="container">
        <div class="hero">
            <h1><span>Global Intelligence</span> · Any Language</h1>
            <p>Aggregating and rewriting news from 60+ trusted sources across 5 languages.</p>
        </div>
        <div id="newsContent">''' + news_section + '''</div>
    </div>
</div>

<div id="tab-adcopy" class="tab-content">
    <div class="container">
        <div class="hero">
            <h1><span>AI Ad Copy</span> · 4 Platforms</h1>
            <p>Generate high-converting ad copy for Facebook, Instagram, Google, and LinkedIn.</p>
        </div>
        <div class="ad-form">
            <label>Business Name</label>
            <input id="f_business" value="Cafe Casa" placeholder="e.g. Cafe Casa">
            <label>Target Audience</label>
            <input id="f_audience" value="Young professionals in Casablanca" placeholder="e.g. Young professionals in Casablanca">
            <label>Industry</label>
            <input id="f_industry" value="Coffee shop" placeholder="e.g. Coffee shop">
            <label>Platform</label>
            <select id="f_platform"><option>facebook</option><option>instagram</option><option>google</option><option>linkedin</option></select>
            <label>Tone</label>
            <select id="f_tone"><option>professional</option><option>playful</option><option>luxury</option></select>
            <label>Language</label>
            <select id="f_language"><option value="en">English</option><option value="fr">Français</option><option value="es">Español</option><option value="ar">العربية</option><option value="zh">中文</option></select>
            <button class="submit-btn" onclick="generateAdCopy()">🚀 Generate Ad Copy</button>
            <div class="ad-result" id="adResult"></div>
        </div>
    </div>
</div>

<div class="footer">
    Powered by <a href="https://yaqeen.manadger.tech" target="_blank">YAQEEN</a> · Manadger Tech · Wallet: 0xD0366D78055b8c637c44d769D1A1371106d13552
</div>

<div class="modal-overlay" id="modal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal()">&times;</button>
        <h2 id="modalTitle">Rewrite Article</h2>
        <div class="label">Original Text</div>
        <div class="original" id="modalOriginal"></div>
        <div style="margin:16px 0;display:flex;align-items:center;gap:8px;flex-wrap:wrap">
            <span style="font-size:13px;color:var(--text-dim)">Rewrite to:</span>
            <select id="targetLang">''' + lang_opts + '''</select>
            <button class="rewrite-btn" id="rewriteBtn" onclick="doRewrite()">⟳ Rewrite</button>
        </div>
        <div class="label">Rewritten Version</div>
        <div class="rewritten" id="modalRewritten">Click "Rewrite" to generate professional version.</div>
    </div>
</div>

<script id="initialData" type="application/json">''' + articles_json + '''</script>
<script>
const API = '';
let allArticles = [];
let currentArticle = null;
const LANG_MAP = {''' + lang_json + '''};
const LANG_ORDER = ''' + json.dumps(LANG_ORDER) + ''';
let currentLang = 'all';
let retryCount = 0;
function switchTab(name, el) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-'+name).classList.add('active');
    if (el) el.classList.add('active');
    else document.querySelectorAll('.tab')[name==='news'?0:1].classList.add('active');
    if (name === 'news' && allArticles.length === 0) fetchNews('all');
}
async function fetchNews(lang) {
    const el = document.getElementById('newsContent');
    const d = document.getElementById('debugStatus');
    function status(m){ if(d) d.textContent = m; }
    el.innerHTML = '<div class="loading"><div class="spinner"></div><div>'+(retryCount>0?'⏳ Server waking up... (attempt '+(retryCount+1)+'/3)':'🌐 Fetching global news...')+'</div><button class="retry-btn" onclick="retryCount=0;fetchNews(currentLang)" style="margin-top:16px;font-size:13px;padding:8px 20px">⟳ Click to retry</button><div style="margin-top:12px;font-size:12px;color:var(--text-dim)" id="debugStatus">loading...</div></div>';
    status('Fetching /api/news?lang='+lang+'...');
    try {
        const controller = new AbortController();
        const timeout = setTimeout(function(){ controller.abort(); status('Timed out'); }, 75000);
        const r = await fetch(API+'/api/news?lang='+lang, {signal: controller.signal});
        clearTimeout(timeout);
        if (!r.ok) { status('HTTP '+r.status); throw new Error('HTTP '+r.status); }
        status('Parsing JSON...');
        const j = await r.json();
        allArticles = j.articles || [];
        retryCount = 0;
        if (allArticles.length === 0) {
            retryCount++;
            setTimeout(function(){ fetchNews(lang); }, 8000);
            status('Empty response, retry '+retryCount);
            el.innerHTML = '<div class="loading"><div class="spinner"></div><div>📡 No articles yet, retrying...</div></div>';
            return;
        }
        status('Rendering '+allArticles.length+' articles');
        renderNews(allArticles);
    } catch(e) {
        status('Error: '+e.message);
        retryCount++;
        if (retryCount < 5) {
            setTimeout(function(){ fetchNews(lang); }, 6000);
        } else {
            el.innerHTML = '<div class="error-state"><h2>⏰ Server Warming Up</h2><p>First load can take 20-40s. Click to try again.</p><button class="retry-btn" onclick="retryCount=0;fetchNews(currentLang)">🔥 Retry</button></div>';
        }
    }
}
function renderNews(articles) {
    const el = document.getElementById('newsContent');
    if (!articles || !articles.length) { el.innerHTML = '<div class="error-state"><h2>No Articles</h2><p>Try selecting a language above.</p><button class="retry-btn" onclick="retryCount=0;fetchNews(currentLang)">⟳ Refresh</button></div>'; return; }
    let html = '<div class="grid">';
    for (const a of articles) {
        const ld = LANG_MAP[a.lang] || {display:a.lang,flag:''};
        html += '<div class="card"><div class="card-badge">'+ld.flag+' '+ld.display+'</div>';
        html += '<div class="card-title">'+esc(a.title)+'</div>';
        html += '<div class="card-summary">'+esc((a.summary||'').slice(0,300))+'</div>';
        html += '<div class="card-meta"><span>'+esc(a.source_name||'')+'</span><div class="card-actions">';
        html += '<button class="card-btn" onclick="window.open(\''+escAttr(a.link)+'\',\'_blank\')">🔗 Open</button>';
        html += '<button class="card-btn primary" onclick="openModal(\''+a.id+'\')">⟳ Rewrite</button>';
        html += '</div></div></div>';
    }
    html += '</div>';
    el.innerHTML = html;
}
function openModal(id) {
    currentArticle = allArticles.find(a => a.id === id);
    if (!currentArticle) return;
    document.getElementById('modalTitle').textContent = currentArticle.title.slice(0,80);
    document.getElementById('modalOriginal').textContent = (currentArticle.summary||currentArticle.title).slice(0,1000);
    document.getElementById('modalRewritten').textContent = 'Click "Rewrite" to generate professional version.';
    document.getElementById('targetLang').value = currentArticle.lang || 'en';
    document.getElementById('modal').classList.add('open');
}
function closeModal() { document.getElementById('modal').classList.remove('open'); currentArticle = null; }
async function doRewrite() {
    const btn = document.getElementById('rewriteBtn');
    const el = document.getElementById('modalRewritten');
    const target = document.getElementById('targetLang').value;
    const text = (currentArticle?.summary||currentArticle?.title||'').slice(0,1000);
    if (!text) { el.textContent = 'No text.'; return; }
    btn.disabled = true; btn.textContent = '⟳ Rewriting...'; el.textContent = 'Generating...';
    try {
        const r = await fetch(API+'/api/rewrite', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text,language:target})});
        const d = await r.json();
        el.textContent = d.rewritten || d.error || 'Failed';
    } catch(e) { el.textContent = 'Error: '+e.message; }
    btn.disabled = false; btn.textContent = '⟳ Rewrite';
}
async function generateAdCopy() {
    const el = document.getElementById('adResult');
    el.style.display = 'block'; el.textContent = 'Generating...';
    try {
        const r = await fetch(API+'/api/generate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
            business: document.getElementById('f_business').value,
            audience: document.getElementById('f_audience').value,
            industry: document.getElementById('f_industry').value,
            platform: document.getElementById('f_platform').value,
            tone: document.getElementById('f_tone').value,
            language: document.getElementById('f_language').value,
            count: 3
        })});
        const d = await r.json();
        el.textContent = d.data?.formatted || d.error || 'Failed';
    } catch(e) { el.textContent = 'Error: '+e.message; }
}
function esc(s) { if (!s) return ''; const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function escAttr(s) { if (!s) return ''; return s.replace(/"/g,'&quot;').replace(/'/g,'&#39;'); }
function setLang(lang, btn) {
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    // update nav dropdown label
    const info = LANG_MAP[lang];
    if (info) {
        document.getElementById('navLangBtn').textContent = info.flag+' '+info.display.split(' ')[0]+' ▾';
    }
    fetchNews(lang);
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
document.addEventListener('click', e => {
    if (e.target.classList.contains('modal-overlay')) closeModal();
    if (!e.target.closest('.nav-lang')) document.getElementById('navLangDropdown').classList.remove('open');
});
// Use server-embedded articles if available
const initEl = document.getElementById('initialData');
if (initEl) {
    try { allArticles = JSON.parse(initEl.textContent) || []; } catch(e) {}
}
if (allArticles.length > 0) {
    const ds = document.getElementById('debugStatus');
    if (ds) ds.textContent = allArticles.length+' articles loaded';
} else {
    fetchNews('all');
}
</script>
</body>
</html>'''

@app.route('/api')
def api_docs():
    return jsonify({
        'service': 'YAQEEN AI Platform',
        'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552',
        'endpoints': {
            'POST /api/generate': 'Generate ad copy (body: business, audience, industry, platform, tone, language, count)',
            'GET /api/sample': 'Sample ad copy output',
            'GET /api/news?lang=en|fr|es|ar|zh|all': 'Fetch latest news from 60+ global sources',
            'GET /api/sources': 'List available languages and source counts',
            'POST /api/rewrite': 'Rewrite article text professionally (body: text, language)',
            'GET /': 'Web UI',
            'GET /health': 'Health check'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'service': 'yaqeen-ai-platform',
        'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552',
        'cached_articles': len(NEWS_CACHE),
        'key_models': get_models(),
        'news_sources': sum(len(v.get('sources', [])) for k, v in ALL_SOURCES.items() if not k.startswith('_'))
    })

# ============ BACKGROUND ============
def bg_loop():
    fetch_keys()
    time.sleep(10)
    fetch_all_news(fast=True)
    time.sleep(20)
    NEWS_CACHE.clear()
    fetch_all_news()
    while True:
        time.sleep(600)
        fetch_keys()
        NEWS_CACHE.clear()
        fetch_all_news()

# Initialize on import (for Vercel serverless cold starts)
fetch_keys()
t = threading.Thread(target=bg_loop, daemon=True)
t.start()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f'YAQEEN AI Platform running on http://0.0.0.0:{port}')
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
