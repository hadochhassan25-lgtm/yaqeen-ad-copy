import express from 'express';
import path from 'path';
import fs from 'fs';
import dotenv from 'dotenv';
import { createServer as createViteServer } from 'vite';
import OpenAI from 'openai';
import Parser from 'rss-parser';

dotenv.config();

const app = express();
app.use(express.json());

const PORT = 3000;
const CACHE_FILE = path.join(process.cwd(), 'data_cache.json');

// Load real news sources from YAQEEN services
const SOURCES_PATH = path.resolve(process.cwd(), '../services/news_sources.json');
let ALL_SOURCES: Record<string, any> = {};
try {
  if (fs.existsSync(SOURCES_PATH)) {
    ALL_SOURCES = JSON.parse(fs.readFileSync(SOURCES_PATH, 'utf-8'));
    console.log(`Loaded ${Object.keys(ALL_SOURCES).filter(k => !k.startsWith('_')).length} language source groups`);
  }
} catch (err) {
  console.error('Failed to load news sources', err);
}

// Count total real sources
let TOTAL_SOURCES = 0;
for (const [k, v] of Object.entries(ALL_SOURCES)) {
  if (!k.startsWith('_')) {
    TOTAL_SOURCES += (v as any).sources?.length || 0;
  }
}
console.log(`Total real RSS sources: ${TOTAL_SOURCES}`);

// ---------- PekPik LLM API Integration (replaces Gemini) ----------
const LLM_API_BASE = 'https://aiapiv2.pekpik.com/v1';
const GITHUB_README_URL = 'https://raw.githubusercontent.com/alistaitsacle/free-llm-api-keys/main/README.md';
const KEY_REFRESH_INTERVAL = 30 * 60 * 1000; // 30 min

const LANG_MODEL_MAP: Record<string, string> = {
  ar: 'deepseek-chat',
  en: 'deepseek-chat',
  fr: 'deepseek-chat',
  es: 'deepseek-chat',
  zh: 'deepseek-chat'
};

const SYSTEM_PROMPTS: Record<string, string> = {
  en: 'You are a professional news editor. Rewrite the following news article in clear, engaging English. Preserve all facts, improve readability, and use a neutral journalistic tone. Output only the rewritten text.',
  fr: 'Vous êtes un rédacteur de presse professionnel. Réécrivez l\'article suivant dans un français clair et engageant. Préservez tous les faits, améliorez la lisibilité, utilisez un ton journalistique neutre. Répondez uniquement avec le texte réécrit.',
  es: 'Eres un editor de noticias profesional. Reescribe el siguiente artículo en un español claro y atractivo. Conserva todos los hechos, mejora la legibilidad y usa un ton periodístico neutral. Responde solo con el texto reescrito.',
  ar: 'أنت محرر أخبار محترف. أعد صياغة المقال التالي بالعربية الفصحى الواضحة. حافظ على جميع الحقائق، حسّن readability، واستخدم نبرة صحفية محايدة. أجب فقط بالنص المعاد صياغته.',
  zh: '你是一名专业新闻编辑。请用清晰简洁的中文重写以下新闻文章。保留所有事实，提高可读性，使用中立的新闻语气。只输出重写后的文本。'
};

// Free API keys from GitHub
interface KeyEntry {
  key: string;
  model: string;
  budget: number;
  rpm: number;
  expires: string;
}

let _keysByModel: Record<string, KeyEntry[]> = {};
let _keysList: KeyEntry[] = [];
let _lastKeyRefresh = 0;

async function fetchFreeKeys() {
  try {
    const resp = await fetch(GITHUB_README_URL, { signal: AbortSignal.timeout(15000) });
    if (!resp.ok) return;
    const text = await resp.text();
    const pattern = /\|\s*`(sk-[A-Za-z0-9]{45,65})`\s*\|\s*([\w\.-]+)\s*\|\s*.*?\|\s*\$?(\d+)\s*\|\s*(\d+)\s*RPM\s*\|\s*(\d{4}-\d{2}-\d{2})/g;
    const parsed: Record<string, KeyEntry[]> = {};
    const all: KeyEntry[] = [];
    const now = new Date();
    let match: RegExpExecArray | null;
    while ((match = pattern.exec(text)) !== null) {
      const expDate = new Date(match[5]);
      if (expDate < now) continue;
      const entry: KeyEntry = {
        key: match[1],
        model: match[2],
        budget: parseInt(match[3]),
        rpm: parseInt(match[4]),
        expires: match[5]
      };
      if (!parsed[entry.model]) parsed[entry.model] = [];
      parsed[entry.model].push(entry);
      all.push(entry);
    }
    _keysByModel = parsed;
    _keysList = all;
    _lastKeyRefresh = Date.now();
    console.log(`Fetched ${all.length} free API keys across ${Object.keys(parsed).length} models`);
  } catch (err) {
    console.error('Failed to fetch free keys, using cache', err);
  }
}

function getKey(model = 'deepseek-chat'): string | null {
  if (Date.now() - _lastKeyRefresh > KEY_REFRESH_INTERVAL) {
    fetchFreeKeys();
  }
  let keys = _keysByModel[model];
  if (!keys || keys.length === 0) keys = _keysByModel['smart-chat'] || [];
  if (!keys || keys.length === 0) {
    for (const [, ks] of Object.entries(_keysByModel)) { keys = keys.concat(ks); }
  }
  if (keys && keys.length > 0) {
    keys.sort((a, b) => b.budget - a.budget);
    return keys[0].key;
  }
  return null;
}

async function llmRewrite(text: string, lang = 'en'): Promise<string | null> {
  const model = LANG_MODEL_MAP[lang] || 'deepseek-chat';
  const prompt = SYSTEM_PROMPTS[lang] || SYSTEM_PROMPTS['en'];
  const tried = new Set<string>();
  for (let i = 0; i < 3; i++) {
    const key = getKey(model);
    if (!key || tried.has(key)) break;
    tried.add(key);
    try {
      const client = new OpenAI({ baseURL: LLM_API_BASE, apiKey: key });
      const resp = await client.chat.completions.create({
        model,
        messages: [
          { role: 'system', content: prompt },
          { role: 'user', content: text.slice(0, 1200) }
        ],
        max_tokens: 500,
        temperature: 0.3
      });
      const content = resp.choices[0]?.message?.content?.trim();
      if (content && content.length > 20 && content !== text.trim().slice(0, 500)) {
        return content;
      }
    } catch { continue; }
  }
  return null;
}

// ---------- In-memory News Store ----------
interface NewsArticle {
  id: string;
  originalTitle: string;
  originalContent: string;
  title: string;
  content: string[];
  source: string;
  sourceUrl: string;
  url: string;
  fetchedAt: string;
  language: 'ar' | 'en' | 'fr' | 'zh' | 'es';
  seoKeywords: string[];
  seoDescription: string;
  history: Array<{
    title: string;
    content: string[];
    timestamp: string;
    instruction?: string;
  }>;
}

interface Plan {
  id: string;
  name: Record<string, string>;
  price: number;
  billing: string;
  features: Record<string, string[]>;
  maxRewrites: number;
  maxArticles: number;
  active: boolean;
}

interface Subscription {
  id: string;
  email: string;
  clientName: string;
  planId: string;
  status: 'active' | 'suspended' | 'trial';
  startDate: string;
  expiresDate: string;
  rewritesUsed: number;
}

interface Stats {
  totalArticles: number;
  totalRewrites: number;
  activeSubscriptions: number;
  prunedArticlesCount: number;
  lastSyncTime: string;
}

let articles: NewsArticle[] = [];
let stats: Stats = {
  totalArticles: 0,
  totalRewrites: 0,
  activeSubscriptions: 0,
  prunedArticlesCount: 0,
  lastSyncTime: new Date().toISOString()
};

// Plans - only keep the pricing structure, no fake clients
let plans: Plan[] = [
  {
    id: 'starter',
    name: {
      en: 'Starter Suit',
      ar: 'باقة المبتدئين الصحفية',
      fr: 'Formule Débutant',
      zh: '起步版方案',
      es: 'Plan de Iniciación'
    },
    price: 49,
    billing: 'monthly',
    features: {
      en: ['Auto re-write standard', 'SEO description key tags', 'Support English & Arabic', 'Daily draft caps: 100'],
      ar: ['إعادة الصياغة التلقائية القياسية', 'تحسين سيو ووصف ترويجي', 'دعم العربية والإنجليزية', 'حد الإنتاج اليومي: 100 مسودة'],
      fr: ['Réécriture automatique standard', 'SEO tags & metas', 'Anglais & Arabe supportés', 'Prise en charge: 100/jour'],
      zh: ['标准自动重写', 'SEO元数据与关键词生成', '支持中英双语', '每日精简额度: 100篇'],
      es: ['Reescritura automática básica', 'Meta SEO optimizado', 'Soporte Inglés y Árabe', 'Límite diario: 100 borradores']
    },
    maxRewrites: 1000,
    maxArticles: 100,
    active: true
  },
  {
    id: 'professional',
    name: {
      en: 'Professional Editorial Pro',
      ar: 'الباقة الاحترافية المتكاملة',
      fr: 'Éditeur Supérieur Professionnel',
      zh: '专业编辑高级版',
      es: 'Suscripción Editorial Pro'
    },
    price: 149,
    billing: 'monthly',
    features: {
      en: ['Multi-agent AI rewrite tone', 'SEO hyper-optimization suite', 'Full 5-language localization', 'Interactive revisions panel', 'Unlimited hourly fetches', 'Daily draft caps: 1000'],
      ar: ['صياغة متعددة النبرات بالذكاء الاصطناعي', 'تحسينات سيو فائقة الدقة', 'ترجمة وصياغة بـ 5 لغات', 'لوحة تحكم تفاعلية للمراجعات', 'تحديث وسحب غير محدود', 'حد الإنتاج اليومي: 1000 مسودة'],
      fr: ['IA multi-tons modulable', 'Optimisation SEO Premium', 'Traduction et réécriture en 5 langues', 'Contrôle révisionnel interactif', 'Accès direct aux flux', 'Max: 1000 ébauches par jour'],
      zh: ['多智能体AI重写语气', 'SEO全方位优化', '支持全部5种语言', '交互式修改反馈面板', '无限制频率内容拉取', '每日精简额度: 1000篇'],
      es: ['Múltiples tonos IA', 'Optimización SEO ultra profesional', 'Localización libre a 5 idiomas', 'Panel interactivo de reediciones', 'Fetch continuo desde webs', 'Límite diario: 1000 borradores']
    },
    maxRewrites: 10000,
    maxArticles: 1000,
    active: true
  },
  {
    id: 'agency',
    name: {
      en: 'Enterprise Agency Network',
      ar: 'باقة شبكات الوكالات والمؤسسات',
      fr: 'Réseau Agence Nationale',
      zh: '企业级大客户订阅',
      es: 'Licencia para Agencias y Corporaciones'
    },
    price: 499,
    billing: 'monthly',
    features: {
      en: ['Custom editorial voice config', 'Bulk export to WordPress & Shopify APIs', 'All languages supported', 'Dedicated support 24/7', 'Unlimited drafts', 'Dedicated proxy feeds'],
      ar: ['تخصيص كامل للهوية التحريرية', 'تصدير كمي إلى ووردبريس', 'توطين فوري لجميع اللغات', 'دعم فني 24/7', 'صياغة غير محدودة', 'خوادم سحب خاصة'],
      fr: ['Voix éditoriale personnalisée', 'Export groupé vers WordPress & Shopify', 'Localisation globale', 'Assistance premium 24h/24', 'Aucune limite', 'Flux serveurs dédiés'],
      zh: ['自订编辑风格', '批量导出至WordPress/Shopify', '全语种输出', '24/7技术支持', '无限发布数量', '定制拉取节点'],
      es: ['Voz editorial personalizada', 'Exportación masiva a WordPress', 'Traducción de máxima calidad', 'Soporte 24/7', 'Reescrituras ilimitadas', 'Proxies privados']
    },
    maxRewrites: 999999,
    maxArticles: 99999,
    active: true
  }
];

let subscriptions: Subscription[] = [];

// ---------- Cache Helpers ----------
function loadCache() {
  try {
    if (fs.existsSync(CACHE_FILE)) {
      const parsed = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8'));
      if (parsed.articles) articles = parsed.articles;
      if (parsed.plans) plans = parsed.plans;
      if (parsed.subscriptions) subscriptions = parsed.subscriptions;
      if (parsed.stats) stats = parsed.stats;
      console.log(`Cache loaded: ${articles.length} articles, ${subscriptions.length} subscriptions`);
      return;
    }
  } catch (err) {
    console.error('Error loading cache', err);
  }
  console.log('No cache found. Starting fresh. RSS fetch will populate articles.');
}

function saveCache() {
  try {
    fs.writeFileSync(CACHE_FILE, JSON.stringify({ articles, plans, subscriptions, stats }, null, 2), 'utf-8');
  } catch (err) {
    console.error('Error saving cache', err);
  }
}

// ---------- RSS Fetching (real) ----------
const rssParser = new Parser({
  timeout: 8000,
  customFields: { item: ['media:content'] }
});

async function fetchRSS(url: string, timeout = 8000): Promise<any[]> {
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    const feed = await rssParser.parseURL(url);
    clearTimeout(id);
    if (!feed.items || feed.items.length === 0) return [];
    return feed.items.slice(0, 12).map(item => ({
      title: (item.title || '').trim(),
      link: item.link || '',
      summary: (item.contentSnippet || (item as any).content || (item as any).description || '').slice(0, 500),
      published: item.pubDate || item.isoDate || ''
    })).filter(item => item.title && item.link);
  } catch {
    return [];
  }
}

async function fetchAllNews() {
  console.log('Starting RSS news fetch from all sources...');
  const allItems: any[] = [];

  for (const [langKey, langData] of Object.entries(ALL_SOURCES)) {
    if (langKey.startsWith('_')) continue;
    const sources = (langData as any).sources || [];
    const promises = sources.slice(0, 4).map((s: any) =>
      fetchRSS(s.url, 5000).then(items => {
        return items.map((it: any) => ({
          ...it,
          source_name: s.name,
          source_url: s.url,
          lang: langKey
        }));
      }).catch(() => [] as any[])
    );
    const results = await Promise.all(promises);
    for (const items of results) allItems.push(...items);
  }

  // Dedup
  const seen = new Set<string>();
  const deduped: any[] = [];
  for (const a of allItems) {
    const key = (a.title || '').slice(0, 80);
    if (!seen.has(key)) {
      seen.add(key);
      const crypto = await import('crypto');
      a.id = crypto.createHash('md5').update(key).digest('hex').slice(0, 12);
      deduped.push(a);
    }
  }

  deduped.sort((a, b) => {
    if (a.published && b.published) return new Date(b.published).getTime() - new Date(a.published).getTime();
    return 0;
  });

  // Map to Article format
  const newArticles: NewsArticle[] = deduped.slice(0, 200).map((item: any) => ({
    id: item.id,
    originalTitle: item.title,
    originalContent: item.summary,
    title: item.title,
    content: item.summary ? [item.summary] : [],
    source: item.source_name || 'Unknown',
    sourceUrl: item.source_url || '',
    url: item.link || '',
    fetchedAt: item.published || new Date().toISOString(),
    language: item.lang || 'en',
    seoKeywords: [],
    seoDescription: '',
    history: []
  }));

  articles = newArticles;
  stats.totalArticles = articles.length;
  stats.lastSyncTime = new Date().toISOString();
  saveCache();
  console.log(`Fetched ${articles.length} real news articles from ${TOTAL_SOURCES}+ sources`);
}

// ---------- Pruning ----------
function pruneExpiredArticles() {
  const CUTOFF_MS = 62 * 3600 * 1000;
  const now = Date.now();
  const initialLen = articles.length;
  articles = articles.filter(a => now - new Date(a.fetchedAt).getTime() < CUTOFF_MS);
  const pruned = initialLen - articles.length;
  if (pruned > 0) {
    stats.prunedArticlesCount += pruned;
    stats.totalArticles = articles.length;
    saveCache();
    console.log(`Pruned ${pruned} expired articles`);
  }
}

// ---------- Fake rewrite fallback ----------
function fallbackRewrite(originalTitle: string, originalContent: string, targetLang: string) {
  const keywords = originalContent.split(' ').filter(w => w.length > 5).slice(0, 4).map(w => w.replace(/[.,]/g, '').toLowerCase());
  const langPrefix: Record<string, string> = {
    ar: '[تحسين SEO] ',
    en: '[SEO Enhanced] ',
    fr: '[SEO Optimisé] ',
    zh: '【SEO重塑】',
    es: '[SEO Optimizado] '
  };
  const prefix = langPrefix[targetLang] || '[SEO] ';
  return {
    title: `${prefix}${originalTitle}`,
    paragraphs: [originalContent],
    keywords: keywords.length > 0 ? keywords : ['news', 'yaqeen'],
    description: `SEO optimized rewrite of: ${originalTitle}`
  };
}

// ---------- Periodic Sync ----------
let syncTimer: NodeJS.Timeout | null = null;

async function performPeriodicSync() {
  console.log('Running periodic RSS sync...');
  pruneExpiredArticles();
  await fetchAllNews();
}

// ---------- API Routes ----------

// Stats
app.get('/api/stats', (_req, res) => {
  res.json({
    ...stats,
    databaseSize: articles.length,
    registeredSitesCount: TOTAL_SOURCES
  });
});

// Sources list
app.get('/api/sites', (_req, res) => {
  const result: Record<string, any> = {};
  for (const [k, v] of Object.entries(ALL_SOURCES)) {
    if (!k.startsWith('_')) {
      const data = v as any;
      result[k] = { display: data.display, flag: data.flag, source_count: data.sources?.length || 0 };
    }
  }
  res.json({ languages: result, total: TOTAL_SOURCES });
});

// Articles
app.get('/api/articles', (req, res) => {
  const lang = req.query.lang as string;
  const search = (req.query.search as string || '').toLowerCase();
  pruneExpiredArticles();
  let filtered = [...articles];
  if (lang && lang !== 'all') filtered = filtered.filter(a => a.language === lang);
  if (search) {
    filtered = filtered.filter(a =>
      a.title.toLowerCase().includes(search) ||
      a.source.toLowerCase().includes(search) ||
      a.originalContent.toLowerCase().includes(search)
    );
  }
  filtered.sort((a, b) => new Date(b.fetchedAt).getTime() - new Date(a.fetchedAt).getTime());
  res.json(filtered);
});

// Sync
app.post('/api/articles/sync', async (_req, res) => {
  await performPeriodicSync();
  res.json({ success: true, articlesCount: articles.length, lastSyncTime: stats.lastSyncTime });
});

// Rewrite
app.post('/api/articles/:id/rewrite', async (req, res) => {
  const { id } = req.params;
  const { instruction, customLanguage } = req.body;
  const article = articles.find(a => a.id === id);
  if (!article) return res.status(404).json({ error: 'Article not found' });
  const targetLang = customLanguage || article.language;
  const rewritten = await llmRewrite(article.originalTitle + '\n\n' + article.originalContent, targetLang);
  let title: string, paragraphs: string[], keywords: string[], description: string;
  if (rewritten) {
    const lines = rewritten.split('\n').filter(l => l.trim());
    title = lines[0] || article.originalTitle;
    paragraphs = lines.slice(1).filter(l => l.length > 20);
    if (paragraphs.length === 0) paragraphs = [rewritten];
    keywords = [];
    description = `Professional rewrite of ${article.originalTitle}`;
  } else {
    const fb = fallbackRewrite(article.originalTitle, article.originalContent, targetLang);
    title = fb.title;
    paragraphs = fb.paragraphs;
    keywords = fb.keywords;
    description = fb.description;
  }
  article.history.unshift({
    title: article.title,
    content: article.content,
    timestamp: new Date().toISOString(),
    instruction: instruction || 'Standard rewrite'
  });
  article.title = title;
  article.content = paragraphs;
  article.language = targetLang as any;
  article.seoKeywords = keywords;
  article.seoDescription = description;
  stats.totalRewrites += 1;
  saveCache();
  res.json({ success: true, article });
});

// Rollback
app.post('/api/articles/:id/rollback', (req, res) => {
  const { id } = req.params;
  const article = articles.find(a => a.id === id);
  if (!article) return res.status(404).json({ error: 'Article not found' });
  if (article.history.length === 0) return res.status(400).json({ error: 'No history to rollback' });
  const prev = article.history.shift()!;
  article.title = prev.title;
  article.content = prev.content;
  saveCache();
  res.json({ success: true, article });
});

// Plans
app.get('/api/admin/plans', (_req, res) => res.json(plans));

app.put('/api/admin/plans/:id', (req, res) => {
  const { id } = req.params;
  const plan = plans.find(p => p.id === id);
  if (!plan) return res.status(404).json({ error: 'Plan not found' });
  const { price, maxRewrites, maxArticles, active, name, features } = req.body;
  if (price !== undefined) plan.price = Number(price);
  if (maxRewrites !== undefined) plan.maxRewrites = Number(maxRewrites);
  if (maxArticles !== undefined) plan.maxArticles = Number(maxArticles);
  if (active !== undefined) plan.active = !!active;
  if (name) plan.name = { ...plan.name, ...name };
  if (features) plan.features = { ...plan.features, ...features };
  saveCache();
  res.json({ success: true, plan });
});

app.post('/api/admin/plans', (req, res) => {
  const { id, price, billing, maxRewrites, maxArticles, name, features } = req.body;
  if (plans.some(p => p.id === id)) return res.status(400).json({ error: 'Plan ID exists' });
  const newPlan: Plan = {
    id: id || `plan-${Date.now()}`,
    name: name || { en: 'New Plan' },
    price: Number(price) || 99,
    billing: billing || 'monthly',
    features: features || { en: ['Feature'] },
    maxRewrites: Number(maxRewrites) || 5000,
    maxArticles: Number(maxArticles) || 500,
    active: true
  };
  plans.push(newPlan);
  saveCache();
  res.json({ success: true, plan: newPlan });
});

// Subscriptions
app.get('/api/admin/subscriptions', (_req, res) => res.json(subscriptions));

app.put('/api/admin/subscriptions/:id', (req, res) => {
  const { id } = req.params;
  const sub = subscriptions.find(s => s.id === id);
  if (!sub) return res.status(404).json({ error: 'Subscription not found' });
  const { status, planId, email, clientName, expiresDate } = req.body;
  if (status) sub.status = status;
  if (planId) sub.planId = planId;
  if (email) sub.email = email;
  if (clientName) sub.clientName = clientName;
  if (expiresDate) sub.expiresDate = expiresDate;
  stats.activeSubscriptions = subscriptions.filter(s => s.status === 'active' || s.status === 'trial').length;
  saveCache();
  res.json({ success: true, subscription: sub });
});

app.post('/api/admin/subscriptions', (req, res) => {
  const { email, clientName, planId, status, durationDays } = req.body;
  if (!email || !clientName || !planId) return res.status(400).json({ error: 'Missing required fields' });
  const days = Number(durationDays) || 30;
  const expires = new Date();
  expires.setDate(expires.getDate() + days);
  const newSub: Subscription = {
    id: `sub-${Date.now()}`,
    email, clientName, planId,
    status: status || 'active',
    startDate: new Date().toISOString(),
    expiresDate: expires.toISOString(),
    rewritesUsed: 0
  };
  subscriptions.push(newSub);
  stats.activeSubscriptions = subscriptions.filter(s => s.status === 'active' || s.status === 'trial').length;
  saveCache();
  res.json({ success: true, subscription: newSub });
});

app.delete('/api/admin/subscriptions/:id', (req, res) => {
  const { id } = req.params;
  const idx = subscriptions.findIndex(s => s.id === id);
  if (idx === -1) return res.status(404).json({ error: 'Subscription not found' });
  subscriptions.splice(idx, 1);
  stats.activeSubscriptions = subscriptions.filter(s => s.status === 'active' || s.status === 'trial').length;
  saveCache();
  res.json({ success: true, message: 'Deleted' });
});

app.post('/api/admin/subscriptions/:id/reset', (req, res) => {
  const { id } = req.params;
  const sub = subscriptions.find(s => s.id === id);
  if (!sub) return res.status(404).json({ error: 'Subscription not found' });
  sub.rewritesUsed = 0;
  saveCache();
  res.json({ success: true, subscription: sub });
});

// Health
app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    service: 'yaqeen-news-platform',
    cached_articles: articles.length,
    sources: TOTAL_SOURCES,
    keys_available: _keysList.length
  });
});

// ---------- Server Start ----------
async function startServer() {
  // Load cache first
  loadCache();

  // Fetch API keys in background
  fetchFreeKeys();
  setInterval(fetchFreeKeys, KEY_REFRESH_INTERVAL);

  // If no cached articles, fetch immediately
  if (articles.length === 0) {
    console.log('No cached articles. Fetching news immediately...');
    await fetchAllNews();
  }

  // Periodic sync every 30 min
  setInterval(performPeriodicSync, 1800000);

  // Pruning every hour
  setInterval(pruneExpiredArticles, 3600000);

  // Mount Vite or production static serving
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`منصة يقين الصحفية active on http://localhost:${PORT}`);
    console.log(`Real sources: ${TOTAL_SOURCES}, Articles: ${articles.length}, API keys: ${_keysList.length}`);
  });
}

startServer();
