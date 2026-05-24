"""
YAQEEN World News - Professional Multi-Language News Aggregator & Rewriter
==========================================================================
Deploy: python yaqeen_news.py
API: /api/news, /api/rewrite, /api/sources
Zero-cost: PythonAnywhere free tier + free HuggingFace Inference API
"""
import sys, io, os, json, hashlib, random, re, html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from flask import Flask, request, jsonify
from pathlib import Path
from datetime import datetime, timezone
import threading, time, traceback, urllib.request, urllib.parse

app = Flask(__name__)
BASE = Path(__file__).resolve().parent

CACHE_FILE = BASE / 'news_cache.json'
SOURCES_FILE = BASE / 'news_sources.json'
CACHE_TTL = 600  # 10 minutes
HF_TOKEN = os.getenv('HF_TOKEN', '')

with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
    ALL_SOURCES = json.load(f)

NEWS_CACHE = []

@app.after_request
def cors(r):
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    r.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return r

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
                items.append({
                    'title': title,
                    'link': link,
                    'summary': summary[:500],
                    'published': published,
                    'source': url
                })
        return items
    except:
        return []

def fetch_all_news():
    global NEWS_CACHE
    now = time.time()
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            if now - cached.get('_ts', 0) < CACHE_TTL:
                NEWS_CACHE = [a for a in cached.get('articles', []) if a.get('title')]
                return
    except:
        pass

    if len(NEWS_CACHE) > 0:
        return

    all_articles = []
    for lang_key, lang_data in ALL_SOURCES.items():
        if lang_key.startswith('_'):
            continue
        for s in lang_data.get('sources', [])[:4]:
            try:
                items = fetch_rss(s['url'], timeout=5)
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
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'_ts': now, 'articles': deduped[:200]}, f, ensure_ascii=False)
    except:
        pass

# ---------- REWRITING ENGINE ----------

LLM_API_BASE = 'https://aiapiv2.pekpik.com/v1'
import free_api_keys
free_api_keys.init()

LANG_MODEL_MAP = {
    'en': 'deepseek-chat',
    'fr': 'deepseek-chat',
    'es': 'deepseek-chat',
    'ar': 'deepseek-chat',
    'zh': 'deepseek-chat'
}

SYSTEM_PROMPTS = {
    'en': 'You are a professional news editor. Rewrite the following news article in clear, engaging English. Preserve all facts, improve readability, and use a neutral journalistic tone. Output only the rewritten text.',
    'fr': 'Vous êtes un rédacteur de presse professionnel. Réécrivez l\'article suivant dans un français clair et engageant. Préservez tous les faits, améliorez la lisibilité, utilisez un ton journalistique neutre. Répondez uniquement avec le texte réécrit.',
    'es': 'Eres un editor de noticias profesional. Reescribe el siguiente artículo en un español claro y atractivo. Conserva todos los hechos, mejora la legibilidad y usa un tono periodístico neutral. Responde solo con el texto reescrito.',
    'ar': 'أنت محرر أخبار محترف. أعد صياغة المقال التالي بالعربية الفصحى الواضحة. حافظ على جميع الحقائق، حسّن readability، واستخدم نبرة صحفية محايدة. أجب فقط بالنص المعاد صياغته.',
    'zh': '你是一名专业新闻编辑。请用清晰简洁的中文重写以下新闻文章。保留所有事实，提高可读性，使用中立的新闻语气。只输出重写后的文本。'
}

def llm_rewrite(text, lang='en'):
    from openai import OpenAI
    model = LANG_MODEL_MAP.get(lang, 'deepseek-chat')
    prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS['en'])
    tried = set()
    for _ in range(3):
        key = free_api_keys.get_key(model)
        if not key or key in tried:
            break
        tried.add(key)
        try:
            client = OpenAI(base_url=LLM_API_BASE, api_key=key)
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': text[:1200]}
                ],
                max_tokens=500,
                temperature=0.3
            )
            content = resp.choices[0].message.content
            if content and len(content) > 20 and content.strip() != text.strip()[:500]:
                return content.strip()
        except:
            continue
    return None

def rewrite_text(text, lang='en'):
    if not text or len(text) < 20:
        return text
    result = llm_rewrite(text, lang)
    if result:
        return result
    return text

# ---------- ROUTES ----------

@app.route('/api/news')
def get_news():
    lang = request.args.get('lang', 'all')
    articles = NEWS_CACHE
    if lang and lang != 'all' and lang in ALL_SOURCES:
        articles = [a for a in articles if a.get('lang') == lang]
    return jsonify({
        'success': True,
        'count': len(articles),
        'language': lang,
        'articles': articles[:50],
        'cached_at': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/sources')
def get_sources():
    result = {}
    for k, v in ALL_SOURCES.items():
        if k.startswith('_'):
            continue
        result[k] = {
            'display': v.get('display', k),
            'flag': v.get('flag', ''),
            'source_count': len(v.get('sources', []))
        }
    return jsonify({'success': True, 'languages': result, 'total': len(NEWS_CACHE)})

@app.route('/api/rewrite', methods=['POST'])
def rewrite():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body required'}), 400
    text = data.get('text', '').strip()
    lang = data.get('language', 'en')
    style = data.get('style', 'neutral')

    if not text:
        return jsonify({'success': False, 'error': 'No text provided'}), 400
    if len(text) < 20:
        return jsonify({'success': False, 'error': 'Text too short (min 20 chars)'}), 400

    try:
        rewritten = rewrite_text(text, lang)
        return jsonify({
            'success': True,
            'original': text[:1000],
            'rewritten': rewritten,
            'language': lang,
            'style': style,
            'service': 'YAQEEN News AI'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def index():
    return serve_ui()

@app.route('/api')
def api_docs():
    return jsonify({
        'service': 'YAQEEN World News',
        'endpoints': {
            'GET /api/news?lang=en|fr|es|ar|zh|all': 'Fetch latest news from global sources',
            'GET /api/sources': 'List available languages and source counts',
            'POST /api/rewrite': 'Rewrite article text professionally',
            'GET /': 'Professional web UI'
        },
        'languages': ['en', 'fr', 'es', 'ar', 'zh'],
        'price': '$0.00 (free tier)',
        'wallet': '0xD0366D78055b8c637c44d769D1A1371106d13552'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'service': 'yaqeen-news',
        'cached_articles': len(NEWS_CACHE),
        'sources': sum(len(v.get('sources', [])) for k, v in ALL_SOURCES.items() if not k.startswith('_'))
    })

# ---------- PROFESSIONAL UI ----------
UI = None

def build_ui():
    global UI
    langs = {}
    for k, v in ALL_SOURCES.items():
        if not k.startswith('_'):
            langs[k] = {'display': v['display'], 'flag': v['flag']}

    UI = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YAQEEN World News — Global Intelligence, Any Language</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root {{
    --bg: #0a0a0f;
    --card: #12121a;
    --card-hover: #181825;
    --accent: #ff6b35;
    --accent2: #7c3aed;
    --gold: #f59e0b;
    --text: #e8e8ee;
    --text-dim: #8888a0;
    --border: #1e1e30;
    --radius: 12px;
    --shadow: 0 4px 24px rgba(0,0,0,.3);
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background: var(--bg); color: var(--text); min-height: 100vh;
    line-height: 1.6;
}}
.nav {{
    position: sticky; top: 0; z-index: 100;
    background: rgba(10,10,15,.85); backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border); padding: 12px 24px;
    display: flex; align-items: center; justify-content: space-between;
}}
.nav-logo {{ font-size: 20px; font-weight: 800; color: var(--accent); letter-spacing: -0.5px; }}
.nav-logo span {{ color: var(--gold); }}
.nav-stats {{ font-size: 13px; color: var(--text-dim); }}
.lang-bar {{
    display: flex; gap: 6px; padding: 12px 24px;
    overflow-x: auto; scrollbar-width: none;
    background: rgba(10,10,15,.5); border-bottom: 1px solid var(--border);
}}
.lang-btn {{
    background: var(--card); border: 1px solid var(--border);
    color: var(--text-dim); padding: 8px 18px; border-radius: 20px;
    cursor: pointer; font-size: 14px; font-weight: 500;
    transition: all .2s; white-space: nowrap;
    font-family: inherit;
}}
.lang-btn:hover {{ border-color: var(--accent); color: var(--text); }}
.lang-btn.active {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 16px 24px 80px; }}
.hero {{
    text-align: center; padding: 40px 20px 30px;
    background: linear-gradient(135deg, rgba(124,58,237,.08) 0%, rgba(255,107,53,.08) 100%);
    border-radius: var(--radius); margin-bottom: 24px;
    border: 1px solid var(--border);
}}
.hero h1 {{ font-size: 32px; font-weight: 800; margin-bottom: 8px; }}
.hero h1 span {{ background: linear-gradient(135deg, var(--accent), var(--accent2), var(--gold));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.hero p {{ color: var(--text-dim); font-size: 16px; max-width: 600px; margin: 0 auto; }}
.grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 16px; margin-top: 16px;
}}
.card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px;
    transition: all .25s; display: flex; flex-direction: column;
    position: relative; overflow: hidden;
}}
.card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 3px; background: linear-gradient(90deg, var(--accent), var(--accent2));
    opacity: 0; transition: opacity .25s;
}}
.card:hover {{ background: var(--card-hover); border-color: var(--accent); transform: translateY(-2px); box-shadow: var(--shadow); }}
.card:hover::before {{ opacity: 1; }}
.card-badge {{
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    color: var(--gold); margin-bottom: 8px;
    letter-spacing: .5px;
}}
.card-title {{
    font-size: 16px; font-weight: 600; line-height: 1.4;
    margin-bottom: 8px; display: -webkit-box;
    -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}}
.card-summary {{
    font-size: 13px; color: var(--text-dim); line-height: 1.5;
    display: -webkit-box; -webkit-line-clamp: 3;
    -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 12px; flex: 1;
}}
.card-meta {{
    display: flex; align-items: center; justify-content: space-between;
    font-size: 12px; color: var(--text-dim); padding-top: 12px;
    border-top: 1px solid var(--border); margin-top: auto;
}}
.card-source {{ font-weight: 500; }}
.card-actions {{ display: flex; gap: 8px; }}
.card-btn {{
    background: transparent; border: 1px solid var(--border);
    color: var(--text); padding: 6px 14px; border-radius: 8px;
    cursor: pointer; font-size: 12px; font-weight: 500;
    transition: all .2s; display: flex; align-items: center; gap: 4px;
    font-family: inherit;
}}
.card-btn:hover {{ border-color: var(--accent); background: rgba(255,107,53,.1); }}
.card-btn.primary {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
.card-btn.primary:hover {{ background: #e55a2b; }}
.loading {{
    display: flex; align-items: center; justify-content: center;
    min-height: 300px; flex-direction: column; gap: 16px;
    color: var(--text-dim);
}}
.spinner {{
    width: 40px; height: 40px; border: 3px solid var(--border);
    border-top-color: var(--accent); border-radius: 50%;
    animation: spin .8s linear infinite;
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.modal-overlay {{
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,.7); backdrop-filter: blur(4px);
    z-index: 1000; display: none; align-items: center; justify-content: center;
    padding: 20px;
}}
.modal-overlay.open {{ display: flex; }}
.modal {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 16px; max-width: 700px; width: 100%;
    max-height: 85vh; overflow-y: auto; padding: 32px;
    box-shadow: 0 20px 60px rgba(0,0,0,.5);
    animation: modal-in .3s ease;
}}
@keyframes modal-in {{
    from {{ opacity: 0; transform: translateY(20px) scale(.97); }}
    to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
.modal-close {{
    float: right; background: none; border: none; color: var(--text-dim);
    font-size: 24px; cursor: pointer; line-height: 1;
    transition: color .2s;
}}
.modal-close:hover {{ color: var(--accent); }}
.modal h2 {{ font-size: 22px; margin-bottom: 6px; }}
.modal .sub {{ color: var(--text-dim); font-size: 14px; margin-bottom: 20px; }}
.modal .label {{ font-size: 12px; font-weight: 600; color: var(--gold); text-transform: uppercase; letter-spacing: 1px; margin-top: 20px; margin-bottom: 8px; }}
.modal .original, .modal .rewritten {{
    background: rgba(255,255,255,.03); border-radius: 8px;
    padding: 16px; font-size: 14px; line-height: 1.7;
    white-space: pre-wrap; word-wrap: break-word;
}}
.modal .rewritten {{ border-left: 3px solid var(--accent); }}
.modal select {{
    background: var(--bg); border: 1px solid var(--border); color: var(--text);
    padding: 8px 16px; border-radius: 8px; font-size: 14px;
    margin-right: 8px; font-family: inherit; cursor: pointer;
}}
.modal .rewrite-btn {{
    background: var(--accent); border: none; color: #fff;
    padding: 8px 24px; border-radius: 8px; cursor: pointer;
    font-size: 14px; font-weight: 600; transition: all .2s;
    font-family: inherit;
}}
.modal .rewrite-btn:hover {{ background: #e55a2b; }}
.modal .rewrite-btn:disabled {{ opacity: .5; cursor: wait; }}
.error-state {{
    text-align: center; padding: 80px 20px; color: var(--text-dim);
}}
.error-state h2 {{ color: var(--accent); margin-bottom: 12px; }}
.retry-btn {{
    background: var(--accent); border: none; color: #fff;
    padding: 10px 28px; border-radius: 8px; cursor: pointer;
    font-size: 14px; font-weight: 600; margin-top: 16px;
    font-family: inherit;
}}
.footer {{
    text-align: center; padding: 32px 24px; color: var(--text-dim);
    font-size: 13px; border-top: 1px solid var(--border);
    margin-top: 40px;
}}
.footer a {{ color: var(--accent); text-decoration: none; }}
@media (max-width: 640px) {{
    .grid {{ grid-template-columns: 1fr; }}
    .hero h1 {{ font-size: 24px; }}
    .container {{ padding: 12px 16px 60px; }}
    .nav {{ padding: 10px 16px; }}
    .lang-bar {{ padding: 8px 16px; gap: 4px; }}
    .lang-btn {{ padding: 6px 12px; font-size: 13px; }}
}}
</style>
</head>
<body>
<div class="nav">
    <div class="nav-logo">YAQEEN <span>NEWS</span></div>
    <div class="nav-stats" id="navStats">Loading...</div>
</div>
<div class="lang-bar" id="langBar"></div>
<div class="container">
    <div class="hero">
        <h1><span>Global Intelligence</span> · Any Language</h1>
        <p>Aggregating and rewriting news from 60+ trusted sources across 5 languages. Professional, fast, zero cost.</p>
    </div>
    <div id="content"><div class="loading"><div class="spinner"></div><div>Fetching global news...</div></div></div>
</div>
<div class="footer">
    Powered by <a href="https://yaqeen.manadger.tech" target="_blank">YAQEEN</a> · Manadger Tech
</div>
<div class="modal-overlay" id="modal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal()">&times;</button>
        <h2 id="modalTitle">Rewrite Article</h2>
        <div class="sub" id="modalSub">Professional AI-powered rewriting</div>
        <div class="label">Source Language</div>
        <div id="modalLang" style="font-size:14px;color:var(--text-dim)"></div>
        <div class="label">Original Text</div>
        <div class="original" id="modalOriginal"></div>
        <div style="margin:16px 0;display:flex;align-items:center;gap:8px;flex-wrap:wrap">
            <span style="font-size:13px;color:var(--text-dim)">Rewrite to:</span>
            <select id="targetLang">'''
    lang_opts = ''
    for k, v in langs.items():
        sel = ' selected' if k == 'en' else ''
        lang_opts += f'<option value="{k}"{sel}>{v["flag"]} {v["display"]}</option>'
    # no "all" option — rewriting requires a specific target language
    UI += lang_opts + '''
            </select>
            <button class="rewrite-btn" id="rewriteBtn" onclick="doRewrite()">⟳ Rewrite</button>
        </div>
        <div class="label">Rewritten Version</div>
        <div class="rewritten" id="modalRewritten">Click "Rewrite" to generate professional version.</div>
    </div>
</div>
<script>
const API = '';
let allArticles = [];
let currentArticle = null;
const LANG_MAP = {'''
    lang_json = ','.join(f'"{k}":{{"display":"{v["display"]}","flag":"{v["flag"]}"}}' for k, v in langs.items())
    UI += lang_json + '''};
const LANG_ORDER = ["en","fr","es","ar","zh"];

async function fetchNews(lang='all') {
    const el = document.getElementById('content');
    el.innerHTML = '<div class="loading"><div class="spinner"></div><div>Fetching global news...</div></div>';
    try {
        const r = await fetch(API+'/api/news?lang='+lang);
        const d = await r.json();
        allArticles = d.articles || [];
        renderNews(allArticles);
        updateStats(d.count, lang);
    } catch(e) {
        el.innerHTML = '<div class="error-state"><h2>Connection Error</h2><p>Could not reach the news service. The server may be waking up.</p><button class="retry-btn" onclick="fetchNews(\''+lang+'\')">Retry</button></div>';
    }
}

function renderNews(articles) {
    const el = document.getElementById('content');
    if (!articles || articles.length === 0) {
        el.innerHTML = '<div class="error-state"><h2>No Articles Found</h2><p>No news articles available for this selection. Try another language.</p></div>';
        return;
    }
    let html = '<div class="grid">';
    for (const a of articles) {
        const ld = LANG_MAP[a.lang] || {display:a.lang.toUpperCase(),flag:''};
        html += '<div class="card">';
        html += '<div class="card-badge">'+ld.flag+' '+ld.display+' · '+escapeHtml(a.source_name||'')+'</div>';
        html += '<div class="card-title">'+escapeHtml(a.title||'')+'</div>';
        html += '<div class="card-summary">'+escapeHtml((a.summary||'').slice(0,300))+'</div>';
        html += '<div class="card-meta">';
        html += '<span class="card-source">'+escapeHtml(a.source_name||'')+'</span>';
        html += '<div class="card-actions">';
        html += '<button class="card-btn" onclick="window.open(\''+escapeAttr(a.link||'')+'\',\'_blank\')">🔗 Open</button>';
        html += '<button class="card-btn primary" onclick="openModal(\''+a.id+'\')">⟳ Rewrite</button>';
        html += '</div></div></div>';
    }
    html += '</div>';
    el.innerHTML = html;
}

function openModal(id) {
    currentArticle = allArticles.find(a => a.id === id);
    if (!currentArticle) return;
    document.getElementById('modalTitle').textContent = currentArticle.title.slice(0,80)+(currentArticle.title.length>80?'...':'');
    document.getElementById('modalSub').textContent = 'By '+currentArticle.source_name+' · '+LANG_MAP[currentArticle.lang]?.flag+' '+LANG_MAP[currentArticle.lang]?.display;
    document.getElementById('modalLang').textContent = LANG_MAP[currentArticle.lang]?.flag+' '+LANG_MAP[currentArticle.lang]?.display+' ('+currentArticle.lang.toUpperCase()+')';
    document.getElementById('modalOriginal').textContent = (currentArticle.summary||currentArticle.title).slice(0,1000);
    document.getElementById('modalRewritten').textContent = 'Click "Rewrite" to generate professional version.';
    document.getElementById('targetLang').value = currentArticle.lang || 'en';
    document.getElementById('modal').classList.add('open');
}

function closeModal() {
    document.getElementById('modal').classList.remove('open');
    currentArticle = null;
}

async function doRewrite() {
    const btn = document.getElementById('rewriteBtn');
    const el = document.getElementById('modalRewritten');
    const target = document.getElementById('targetLang').value;
    const text = (currentArticle?.summary||currentArticle?.title||'').slice(0,1000);
    if (!text) { el.textContent = 'No text to rewrite.'; return; }
    btn.disabled = true; btn.textContent = '⟳ Rewriting...';
    el.textContent = 'Generating professional rewrite...';
    try {
        const r = await fetch(API+'/api/rewrite', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({text,language:target,style:'neutral'})
        });
        const d = await r.json();
        el.textContent = d.rewritten || d.error || 'Rewrite failed';
    } catch(e) {
        el.textContent = 'Error: '+e.message;
    }
    btn.disabled = false; btn.textContent = '⟳ Rewrite';
}

function updateStats(count, lang) {
    const el = document.getElementById('navStats');
    const total = allArticles.length;
    const langNames = Object.values(LANG_MAP).map(l=>l.flag+' '+l.display).join(' · ');
    el.textContent = count+' articles · '+langNames;
}

function escapeHtml(s) {
    if (!s) return '';
    const d = document.createElement('div');
    d.textContent = s; return d.innerHTML;
}
function escapeAttr(s) {
    if (!s) return '';
    return s.replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

// Language bar
(function buildLangBar() {
    const bar = document.getElementById('langBar');
    const allBtn = document.createElement('button');
    allBtn.className = 'lang-btn active';
    allBtn.textContent = '🌐 All';
    allBtn.onclick = ()=>{ setLang('all', allBtn); };
    bar.appendChild(allBtn);
    for (const k of LANG_ORDER) {
        if (!LANG_MAP[k]) continue;
        const btn = document.createElement('button');
        btn.className = 'lang-btn';
        btn.textContent = LANG_MAP[k].flag+' '+LANG_MAP[k].display;
        btn.dataset.lang = k;
        btn.onclick = (e)=>{ setLang(k, btn); };
        bar.appendChild(btn);
    }
})();

let currentLang = 'all';
function setLang(lang, btn) {
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    fetchNews(lang);
}

// Init
fetchNews('all');

// Keyboard
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
document.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) closeModal(); });
</script>
</body>
</html>'''
    return UI

def serve_ui():
    global UI
    if UI is None:
        UI = build_ui()
    return UI, 200, {'Content-Type': 'text/html; charset=utf-8'}

# ---------- BACKGROUND REFRESH ----------
def background_refresh():
    time.sleep(15)
    try:
        fetch_all_news()
    except:
        pass
    while True:
        time.sleep(600)
        try:
            NEWS_CACHE.clear()
            fetch_all_news()
        except:
            pass

if __name__ == '__main__':
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            NEWS_CACHE = [a for a in cached.get('articles', []) if a.get('title')]
    except:
        pass
    t = threading.Thread(target=background_refresh, daemon=True)
    t.start()
    t2 = threading.Thread(target=fetch_all_news, daemon=True)
    t2.start()
    port = int(os.getenv('PORT', 5000))
    print(f'YAQEEN News running on http://0.0.0.0:{port}')
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
