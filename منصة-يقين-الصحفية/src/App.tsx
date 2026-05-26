import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Globe,
  RefreshCw,
  Database,
  Search,
  Users,
  CheckCircle,
  Settings,
  Activity,
  Sparkles,
  Undo2,
  AlertTriangle,
  Moon,
  Sun,
  Sliders,
  Plus,
  CreditCard,
  ArrowRight,
  ExternalLink,
  ShieldCheck,
  Layers,
  Languages,
  Calendar,
  Clock,
  ChevronRight,
  ChevronLeft,
  Trash2,
  TrendingUp
} from 'lucide-react';
import { Article, Plan, Subscription, YaqeenStats } from './types';

// Multilingual translations database for premium localizations
const TRANSLATIONS = {
  ar: {
    title: "منصة يقين الصحفية",
    subtitle: "أول منصة SaaS ذكية لإعادة الصياغة الفورية للسيو، سحب 500 موقع RSS عالمي وتوطين الأخبار بـ 5 لغات",
    tagline: "قوة الصحافة اللامحدودة بمحركات الذكاء الاصطناعي",
    searchPlaceholder: "ابحث عن المقالات أو الصحف العالمية...",
    allCategories: "كافة التصنيفات",
    loadMore: "أكمل لباقي المقالات",
    activeFeeds: "تدرج 500 موقع RSS نشط",
    categoryPolitics: "سياسة ودبلوماسية",
    categoryBusiness: "اقتصاد وأعمال",
    categoryTechnology: "تقنية واتصالات",
    categoryScience: "علوم ومختبرات",
    categorySports: "رياضة وألعاب",
    categoryLifestyle: "طراز ونمط حياة",
    categoryHealth: "صحة وغذاء",
    tabGlobalFeeds: "المقالات الصحفية المستهدفة",
    tabAdminPanel: "مركز لوحة التحكم والاشتراكات",
    statsOverview: "إحصائيات فورية للأداء",
    totalArticles: "المستودع النشط",
    autoPruned: "المقالات المؤرشفة والمحذوفة تلقائياً (>62 ساعة)",
    totalRewrites: "إعادة الصياغة بالـ AI",
    activeSubs: "الاشتراكات الفعالة",
    syncCountdown: "RSS دوري كل 30 دقيقة | السحب القادم خلال:",
    syncNowBtn: "تحديث جلب الصحف الآن",
    syncingText: "جاري جلب 500 مصدر وإعادة صياغة السيو...",
    originalTextLabel: "النص التحريري الأصلي (المصدر العالمي)",
    optimizedSEOText: "المقال المحسن والمصاغ للسيو (يقين AI)",
    headlineSEO: "عنوان المقال المطور لمحركات البحث",
    metaDescription: "وصف السيو التعريفي (Meta Description)",
    seoKeywords: "الكلمات المفتاحية النشطة للسيو",
    editorRewriterSuite: "جناح المراجعة الذكية للعملاء",
    originalSourceLink: "زيارة الرابط الأصلي للمصدر",
    customRewriteInstruction: "اكتب توجيهاً مخصصاً أو نبرة تحريرية مفضلة لإنتاج نسخة جديدة",
    btnGeminiRewrite: "إعادة صياغة فورية بواسطة Gemini AI",
    btnUndoRewrite: "تراجع عن مسودة الصياغة",
    originalLanguageLabel: "اللغة الأصلية للمقال",
    viewLanguageLabel: "صياغة وتوطين المقال إلى لغة مخصصة:",
    selectTone: "قالب الأسلوب التحريري النبروي:",
    statusActive: "فعال نشط",
    statusSuspended: "موقوف مؤقتاً",
    statusTrial: "تجريبي محدود",
    managePlans: "تحرير باقات اشتراكات الـ SaaS",
    manageSubscriptions: "إدارة تراخيص واشتراكات العملاء",
    newSubscription: "إضافة مشترك أو جهة جديدة",
    newPlan: "تأسيس باقة مخصصة جديدة",
    saveSuccess: "تم الحفظ بنجاح!",
    planStarter: "باقةStarter",
    planProfessional: "باقة Professional Pro",
    planAgency: "باقة Agency Enterprise",
    priceLabel: "السعر الشهري ($)",
    limitArticles: "حد جلب المقالات اليومي",
    limitRewrites: "حد تكرار صياغة الذكاء الاصطناعي",
    featuresLabel: "قائمة المميزات الصحفية (مفصولة بأسطر)",
    emailPlaceholder: "البريد الإلكتروني للعميل المالي",
    clientNamePlaceholder: "اسم الصحيفة أو العميل المالي",
    durationDaysLabel: "مدة الترخيص باليوم (مثال: 30 يوم)",
    btnSubmit: "تأكيد وإرسال البيانات",
    noArticlesFound: "لا يوجد مقالات تطابق شروط البحث أو الفلاتر المختارة حالياً.",
    activeState: "الحالة التفعيلية",
    editPlanTitle: "تعديل تفاصيل الباقة",
    clientOrg: "المؤسسة الصحفية المستفيدة",
    lastSyncedText: "آخر تحديث لقاعدة البيانات:",
    secondsText: "ثانية",
    minutesText: "دقيقة",
    btnBackToFeeds: "← العودة لغرفة الأخبار ومستودع المقالات",
    preparationSuiteTitle: "جناح المعالجة المهنية والصياغة الاحترافية للخبر",
    quotaWarningBadge: "⚠️ تجاوز 90% للحصة"
  },
  en: {
    title: "Yaqeen News Platform",
    subtitle: "The ultimate AI-driven SEO rewriting SaaS, harvesting 500 global RSS feeds localized in 5 global languages",
    tagline: "Unleashing Advanced Localized Editorial Intelligence",
    searchPlaceholder: "Search global wire and SEO articles...",
    allCategories: "All Categories",
    loadMore: "Load Remaining Articles",
    activeFeeds: "Active 500 RSS Sites Harvester",
    categoryPolitics: "Politics & Diplomacy",
    categoryBusiness: "Business & Economy",
    categoryTechnology: "Technology & Telecom",
    categoryScience: "Science & Laboratories",
    categorySports: "Sports & Games",
    categoryLifestyle: "Lifestyle & Culture",
    categoryHealth: "Health & Medicine",
    tabGlobalFeeds: "Global Newspaper Desk",
    tabAdminPanel: "Subscriptions & SaaS Console",
    statsOverview: "Instant Analytics",
    totalArticles: "Active Repository",
    autoPruned: "Auto-Deleted (>62 hours limit)",
    totalRewrites: "AI Parsed & Rewritten",
    activeSubs: "Active Subscriptions",
    syncCountdown: "Auto-RSS every 30 mins | Sync in:",
    syncNowBtn: "Force Sync All Feeds Now",
    syncingText: "Ingesting 500 sources & compiling SEO...",
    originalTextLabel: "Original Wire Source (Source Broadcast)",
    optimizedSEOText: "SEO Paraphrased & Structured (Yaqeen AI)",
    headlineSEO: "SEO Optimized Headline",
    metaDescription: "Meta Description Curation",
    seoKeywords: "Active Primary SEO Keyphrases",
    editorRewriterSuite: "Interactive Client Rewriter Suite",
    originalSourceLink: "Official Source Origin Link",
    customRewriteInstruction: "Specify customized tone guidelines or revision prompt",
    btnGeminiRewrite: "Instant Paraphrase with Gemini AI",
    btnUndoRewrite: "Rollback Draft",
    originalLanguageLabel: "Wire Feed Language",
    viewLanguageLabel: "Translate & Localize Draft to Language:",
    selectTone: "Target Editorial Tone/Persona:",
    statusActive: "Active",
    statusSuspended: "Suspended",
    statusTrial: "Trial Pass",
    managePlans: "Manage SaaS Product Pricing & Plans",
    manageSubscriptions: "Client Base Licences Hub",
    newSubscription: "Onboard New Client Organisation",
    newPlan: "Create Custom Specialized Plan",
    saveSuccess: "Saved securely and synced!",
    planStarter: "Starter Pack",
    planProfessional: "Professional Pro Pack",
    planAgency: "Agency Enterprise Pack",
    priceLabel: "Monthly Price ($)",
    limitArticles: "Day Article Cap Limit",
    limitRewrites: "AI Rewrite Tries Allowed",
    featuresLabel: "Editorial Features List (one per line)",
    emailPlaceholder: "Client account billing email",
    clientNamePlaceholder: "Client press/broadcast name",
    durationDaysLabel: "Licence cycle in days (default: 30)",
    btnSubmit: "Validate & Save Contract",
    noArticlesFound: "No articles matched your criteria at this moment.",
    activeState: "Activation status",
    editPlanTitle: "Modify Plan Parameters",
    clientOrg: "Subscriber Organization",
    lastSyncedText: "Last successful database sync:",
    secondsText: "sec",
    minutesText: "min",
    btnBackToFeeds: "← Back to Newsroom / Feeds Desk",
    preparationSuiteTitle: "Professional Editorial Preparation & Rewriting Page",
    quotaWarningBadge: "⚠️ >90% Quota Used"
  },
  fr: {
    title: "Plateforme d'Information Yaqeen",
    subtitle: "Le nec plus ultra du SaaS de réécriture SÉO par IA, récoltant 500 flux RSS mondiaux localisés en 5 langues",
    tagline: "L'intelligence éditoriale mondiale réinventée",
    searchPlaceholder: "Rechercher des articles originaux ou SÉO...",
    allCategories: "Toutes Catégories",
    loadMore: "Charger le Reste des Articles",
    activeFeeds: "500 Flux RSS Actifs",
    categoryPolitics: "Politique & Diplomatie",
    categoryBusiness: "Économie & Finance",
    categoryTechnology: "Technologie & Réseaux",
    categoryScience: "Science & Innovation",
    categorySports: "Sports & Joutes",
    categoryLifestyle: "Style de Vie & Culture",
    categoryHealth: "Santé & Nutrition",
    tabGlobalFeeds: "Flux de Rédaction Universel",
    tabAdminPanel: "SaaS Abonnement & Administration",
    statsOverview: "Aperçu de Performance",
    totalArticles: "Articles en Base de Données",
    autoPruned: "Supprimés automatiquement (> 62 heures)",
    totalRewrites: "Syntheses & Réécritures IA",
    activeSubs: "Souscripteurs Actifs",
    syncCountdown: "Auto-RSS toutes les 30 min | Synchronisation dans:",
    syncNowBtn: "Forcer la Synchronisation",
    syncingText: "Téléchargement en cours depuis 500 portails...",
    originalTextLabel: "Texte de Presse Original",
    optimizedSEOText: "Rédaction Optimisée SÉO (Yaqeen AI)",
    headlineSEO: "Titre SÉO Optimisé",
    metaDescription: "Méta Description SÉO",
    seoKeywords: "Mots-Clés Principaux",
    editorRewriterSuite: "Bureau Interactif de Réécriture",
    originalSourceLink: "Consulter la Source Officielle",
    customRewriteInstruction: "Spécifiez les directives de ton de votre rédaction",
    btnGeminiRewrite: "Paraphraser Directement avec Gemini",
    btnUndoRewrite: "Restaurer la Version Précédente",
    originalLanguageLabel: "Langue Source",
    viewLanguageLabel: "Traduire ou Reformuler en :",
    selectTone: "Sélectionner le Ton de Voix :",
    statusActive: "Actif",
    statusSuspended: "Suspendu",
    statusTrial: "Essai Limité",
    managePlans: "Établir les Tarifs SaaS des Services",
    manageSubscriptions: "Contrats de Licences Clients",
    newSubscription: "Nouveau Client Organisme",
    newPlan: "Créer un Plan Sur Mesure",
    saveSuccess: "Données sauvegardées avec succès !",
    planStarter: "Formule Débutant",
    planProfessional: "Formule Professionnelle Pro",
    planAgency: "Formule Agence Nationale",
    priceLabel: "Tarif Mensuel ($)",
    limitArticles: "Max articles par jour",
    limitRewrites: "Max essais de réécriture",
    featuresLabel: "Avantages Edito (un par ligne)",
    emailPlaceholder: "Adresse email de facturation",
    clientNamePlaceholder: "Nom média ou journal client",
    durationDaysLabel: "Durée du cycle (jours, def: 30)",
    btnSubmit: "Valider le Contrat Commercial",
    noArticlesFound: "Aucun article ne correspond à votre recherche pour le moment.",
    activeState: "État Politique",
    editPlanTitle: "Paramétrer Offre Commerciale",
    clientOrg: "Média Abonné",
    lastSyncedText: "Dernier cycle automatique accompli :",
    secondsText: "sec",
    minutesText: "min",
    btnBackToFeeds: "← Retour au flux général",
    preparationSuiteTitle: "Espace de Rédaction Professionnelle & Réécriture",
    quotaWarningBadge: "⚠️ Capacité >90%"
  },
  zh: {
    title: "يقين (Yaqeen) 智能新闻平台",
    subtitle: "首个专为搜索引擎优化建构的SaaS多语智能化重写平台，整合全球500家主流RSS媒体源实时刷新",
    tagline: "引领融媒体时代的全球SEO人工智能重编范式",
    searchPlaceholder: "搜索引擎和AI优化稿库检索...",
    allCategories: "全部分类栏目",
    loadMore: "加载多余的其余新闻稿",
    activeFeeds: "已注册监控的500个世界节点",
    categoryPolitics: "国际政治与外交",
    categoryBusiness: "全球财政与宏观经济",
    categoryTechnology: "前沿前瞻科技",
    categoryScience: "实验室科学探究",
    categorySports: "体育竞技动态",
    categoryLifestyle: "人文艺术与高尚生活",
    categoryHealth: "健康卫生与保健",
    tabGlobalFeeds: "前台编辑排版系统",
    tabAdminPanel: "高级后台管理与企业授权",
    statsOverview: "运行效能看板",
    totalArticles: "当前持久库总量",
    autoPruned: "已强制删除清理 (>62小时过期稿件)",
    totalRewrites: "累计AI计算重写量",
    activeSubs: "已开通的活跃专属大客户",
    syncCountdown: "循环刷新(30分钟)脉搏 | 下次同步:",
    syncNowBtn: "强制拉取500源并重新合成",
    syncingText: "正在调用Gemini读取并重新排版...",
    originalTextLabel: "全球原电传资讯新闻流",
    optimizedSEOText: "搜索引擎高度优化重构版本 (Yaqeen AI)",
    headlineSEO: "AI专定SEO高曝光引流标题",
    metaDescription: "文章SEO描述层配置",
    seoKeywords: "关联收录主力关键词组",
    editorRewriterSuite: "交互式稿件AI微调平台",
    originalSourceLink: "访问该新闻官方出处链接",
    customRewriteInstruction: "请输入对此份稿件进行重写作风指令或细读说明",
    btnGeminiRewrite: "提交Gemini开始多维重编",
    btnUndoRewrite: "撤销该阶段并回归上一版草稿",
    originalLanguageLabel: "原始播发语种",
    viewLanguageLabel: "一键快速转换或编译目标语言:",
    selectTone: "专属文体剪裁特色调性:",
    statusActive: "状态正常已激活",
    statusSuspended: "暂停扣停处理中",
    statusTrial: "限时体验版通行证",
    managePlans: "调整商业版收费梯度标准",
    manageSubscriptions: "订购席位与企业配额发放",
    newSubscription: "给新用户开通企业专属授权",
    newPlan: "设计定制专属订阅规格",
    saveSuccess: "配置已全网加密生效并同步！",
    planStarter: "入门创意版",
    planProfessional: "专业报业升级版",
    planAgency: "国家通讯社集团专属版",
    priceLabel: "常规月资费 ($)",
    limitArticles: "规定每日拉取上限",
    limitRewrites: "独立交互重写可调配量",
    featuresLabel: "计划特权明细 (每行一条)",
    emailPlaceholder: "专属付款或账务联系邮箱",
    clientNamePlaceholder: "订阅报刊或频道官方英文/阿拉伯文全称",
    durationDaysLabel: "有效授权时长(天数，默认: 30天)",
    btnSubmit: "确立并开通上述条款",
    noArticlesFound: "当前没有查寻到同过滤状态一致的可视报道。",
    activeState: "启用政策",
    editPlanTitle: "微调商业包项目权责",
    clientOrg: "合约订购主体",
    lastSyncedText: "上次自动化AI抓取及对齐时间：",
    secondsText: "秒",
    minutesText: "分",
    btnBackToFeeds: "← 返回全球电讯稿库",
    preparationSuiteTitle: "专业文章准备及深度重写中心",
    quotaWarningBadge: "⚠️ 配额已超90%"
  },
  es: {
    title: "Plataforma de Prensa Yaqeen",
    subtitle: "El software líder de reescritura SEO por IA, extrayendo de 500 portales RSS globales localizados en 5 lenguas",
    tagline: "El poder del periodismo algorítmico global",
    searchPlaceholder: "Buscar despachos originales o adaptados SEO...",
    allCategories: "Categorías Completas",
    loadMore: "Cargar los Demás Artículos",
    activeFeeds: "500 Canales RSS Monitoreados",
    categoryPolitics: "Política & Diplomacia",
    categoryBusiness: "Negocios & Economía",
    categoryTechnology: "Tecnología & Redes",
    categoryScience: "Ciencia & Investigación",
    categorySports: "Deportes & Torneos",
    categoryLifestyle: "Estilo de Vida & Tendencias",
    categoryHealth: "Bienestar & Salud",
    tabGlobalFeeds: "Mesa de Redacción General",
    tabAdminPanel: "Consola SaaS & Administración",
    statsOverview: "KPIs de Operaciones",
    totalArticles: "Artículos Almacenados",
    autoPruned: "Removidos por directiva de expiración (>62 horas)",
    totalRewrites: "Párrafos Reescritos por IA",
    activeSubs: "Planes Clientes Activos",
    syncCountdown: "Auto-RSS cada 30 min | Siguiente fetch en:",
    syncNowBtn: "Disparar Extracción General Ahora",
    syncingText: "Leyendo 500 canales y reescribiendo...",
    originalTextLabel: "Cuerpo de Prensa de Origen",
    optimizedSEOText: "Versión Reestructurada Avanzada SEO (Yaqeen AI)",
    headlineSEO: "Titular Altamente Atractivo SEO",
    metaDescription: "Meta-Descripción SEO Profesional",
    seoKeywords: "Palabras Clave SEO Recomendadas",
    editorRewriterSuite: "Estudio de Edición Personalizado",
    originalSourceLink: "Ir al Enlace Original de la Noticia",
    customRewriteInstruction: "Escriba especificaciones o indicaciones para la IA",
    btnGeminiRewrite: "Paraphrasear con la IA de Gemini",
    btnUndoRewrite: "Restaurar Copia Anterior",
    originalLanguageLabel: "Idioma de Transmisión",
    viewLanguageLabel: "Reescribir & Localizar al Idioma:",
    selectTone: "Estilo Editorial Principal:",
    statusActive: "Activo Vigente",
    statusSuspended: "Bloqueado Temporalmente",
    statusTrial: "Acceso de Prueba",
    managePlans: "Administrar Planes de Producto SaaS",
    manageSubscriptions: "Licencias Clientes Concedidas",
    newSubscription: "Dar de Alta Nueva Entidad Editorial",
    newPlan: "Crear Nuevo Paquete Comercial",
    saveSuccess: "¡Cambios guardados e implementados!",
    planStarter: "Plan Básico Starter",
    planProfessional: "Plan de Crecimiento Profesional Pro",
    planAgency: "Plan Enterprise Grandes Agencias",
    priceLabel: "Precio Mensual ($)",
    limitArticles: "Artículos permitidos por día",
    limitRewrites: "Solicitudes de IA permitidas",
    featuresLabel: "Características (línea por línea)",
    emailPlaceholder: "Correo electrónico del cliente",
    clientNamePlaceholder: "Nombre de la agencia o corporativo",
    durationDaysLabel: "Plazo de suscripción (días, por defecto: 30)",
    btnSubmit: "Emitir Suscripción y Formalizar",
    noArticlesFound: "Ningún artículo coincide con los parámetros definidos hoy.",
    activeState: "Estado de Operatividad",
    editPlanTitle: "Modificar Coberturas del Plan",
    clientOrg: "Razón Social Suscriptora",
    lastSyncedText: "Última sincronización y purga de sistema realizadas:",
    secondsText: "seg",
    minutesText: "min",
    btnBackToFeeds: "← Volver al panel de noticias",
    preparationSuiteTitle: "Suite de Preparación y Reescritura Profesional",
    quotaWarningBadge: "⚠️ >90% Cuota Usada"
  }
};

const DEFAULT_TONES = [
  { id: 'standard', name: { ar: 'صياغة ممتازة قياسية', en: 'Standard Copic', fr: 'Standard Classique', zh: '标准重塑风格', es: 'Estándar Profesional' } },
  { id: 'clickbait', name: { ar: 'جاذب وإعلامي ومحفز للنقر (Clickbait)', en: 'High Clickbait SEO', fr: 'Sensationnel Attrayant', zh: '吸引爆款SEO流量组', es: 'Titular Seductor Clickbait' } },
  { id: 'formal', name: { ar: 'رسمي، دقيق ومناسب للشركات العالمية', en: 'Highly Executive Formal', fr: 'Académique Solennel', zh: '客观严肃官方社论', es: 'Formal Académico Formal' } },
  { id: 'bulletin', name: { ar: 'تغطية موجزة في نقاط عريضة سريعة القراءة', en: 'Bullet points summary focus', fr: 'Résumé Structuré', zh: '极速阅览骨干摘要', es: 'Resumen en Viñetas Rápidas' } },
  { id: 'storytelling', name: { ar: 'نثر إبداعي روائي يعزز فضول القراء', en: 'Creative Storytelling narrative', fr: 'Récit Créatf Émotionnel', zh: '故事化流丽叙事体', es: 'Formativo Narrativo Creativo' } }
];

export default function App() {
  const [lang, setLang] = useState<'ar' | 'en' | 'fr' | 'zh' | 'es'>('en');
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [activeTab, setActiveTab] = useState<'feed' | 'admin'>('feed');
  
  // Data State
  const [articles, setArticles] = useState<Article[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [stats, setStats] = useState<YaqeenStats | null>(null);

  // Filters State
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedLanguageFilter, setSelectedLanguageFilter] = useState<string>('');
  
  // Content Pagination State
  const [showAllArticles, setShowAllArticles] = useState<boolean>(false);

  // Focus Article (For the split interface / Reader panel)
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  // Operations / UI State
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [isRewriting, setIsRewriting] = useState<boolean>(false);
  const [countdown, setCountdown] = useState<number>(1800); // 30 minutes in seconds
  const [notification, setNotification] = useState<string | null>(null);

  // Custom AI Rewrite state
  const [customInstruction, setCustomInstruction] = useState<string>('');
  const [selectedTone, setSelectedTone] = useState<string>('standard');
  const [targetRewriteLang, setTargetRewriteLang] = useState<'ar' | 'en' | 'fr' | 'zh' | 'es'>('en');

  // Admin Workspace state - Modifying parameters
  const [editingPlanId, setEditingPlanId] = useState<string | null>(null);
  const [planForm, setPlanForm] = useState<Partial<Plan>>({});
  
  // Add new subscriber form
  const [clientSearchQuery, setClientSearchQuery] = useState<string>('');
  const [clientStatusFilter, setClientStatusFilter] = useState<string>('');
  const [showAddSubModal, setShowAddSubModal] = useState<boolean>(false);
  const [subForm, setSubForm] = useState({
    clientName: '',
    email: '',
    planId: 'professional',
    status: 'active' as 'active' | 'suspended' | 'trial',
    durationDays: 30
  });

  // Load baseline statistics and elements on load
  const loadData = async () => {
    try {
      const statsRes = await fetch('/api/stats');
      const statsData = await statsRes.json();
      setStats(statsData);

      const plansRes = await fetch('/api/admin/plans');
      const plansData = await plansRes.json();
      setPlans(plansData);

      const subRes = await fetch('/api/admin/subscriptions');
      const subData = await subRes.json();
      setSubscriptions(subData);

      // Verify and fetch general articles pool
      await refetchArticles();
    } catch (err) {
      console.error("Failed to load initial REST configuration files:", err);
    }
  };

  const refetchArticles = async () => {
    try {
      const url = new URL('/api/articles', window.location.origin);
      if (selectedLanguageFilter) {
        url.searchParams.set('lang', selectedLanguageFilter);
      }
      if (selectedCategory) {
        url.searchParams.set('category', selectedCategory);
      }
      if (searchQuery) {
        url.searchParams.set('search', searchQuery);
      }
      const articlesRes = await fetch(url.toString());
      const articlesData = await articlesRes.json();
      setArticles(articlesData);

      // Auto update active selection with latest content if modified
      if (selectedArticle && articlesData.length > 0) {
        const updated = articlesData.find((a: Article) => a.id === selectedArticle.id);
        if (updated) {
          setSelectedArticle(updated);
        }
      }
    } catch (err) {
      console.error("Failed to sync current articles query:", err);
    }
  };

  useEffect(() => {
    loadData();
    // Start countdown timer
    const interval = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          // Trigger silent background sync simulated locally when timer reaches zero
          triggerFetchNow(true);
          return 1800;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Sync variables every time filters update
  useEffect(() => {
    refetchArticles();
  }, [selectedCategory, searchQuery, selectedLanguageFilter]);

  const showToast = (message: string) => {
    setNotification(message);
    setTimeout(() => {
      setNotification(null);
    }, 4000);
  };

  // Trigger manual pulling & automated RSS rewriting instantly
  const triggerFetchNow = async (silent: boolean = false) => {
    if (isSyncing) return;
    if (!silent) setIsSyncing(true);
    try {
      const res = await fetch('/api/articles/sync', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        await loadData();
        setCountdown(1800);
        if (!silent) {
          showToast(lang === 'ar' ? "تم تحديث وربط المقالات بنجاح!" : "RSS Feeds refreshed and optimized successfully!");
        }
      }
    } catch (err) {
      console.error("Failed manual syncer trigger:", err);
    } finally {
      if (!silent) setIsSyncing(false);
    }
  };

  // Interactive re-writer dispatcher
  const handleAIRewrite = async () => {
    if (!selectedArticle || isRewriting) return;
    setIsRewriting(true);
    
    // Combine predefined style constraints with user instructions
    const toneRef = DEFAULT_TONES.find(t => t.id === selectedTone);
    const toneText = toneRef ? toneRef.name.en : selectedTone;
    const compiledInstruction = `Rewrite Tone Style: ${toneText}. Custom User Specifications: ${customInstruction}`;

    try {
      const res = await fetch(`/api/articles/${selectedArticle.id}/rewrite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          instruction: compiledInstruction,
          customLanguage: targetRewriteLang
        })
      });

      const responseJSON = await res.json();
      if (responseJSON.success) {
        // Find in array & update state
        const updatedArticle = responseJSON.article;
        setArticles(prev => prev.map(a => a.id === updatedArticle.id ? updatedArticle : a));
        setSelectedArticle(updatedArticle);
        setCustomInstruction('');
        showToast(lang === 'ar' ? "صيغ المقال بنجاح بواسطة يقين AI!" : "Article rewritten beautifully by Yaqeen AI!");
        
        // Refresh general dashboard statistics
        const statsRes = await fetch('/api/stats');
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (e) {
      console.error(e);
      showToast("Quantum error during AI generation. Using fallback rewrite parameters.");
    } finally {
      setIsRewriting(false);
    }
  };

  // Rollback to previous rewritten versions
  const handleRollback = async () => {
    if (!selectedArticle) return;
    try {
      const res = await fetch(`/api/articles/${selectedArticle.id}/rollback`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        const restored = data.article;
        setArticles(prev => prev.map(a => a.id === restored.id ? restored : a));
        setSelectedArticle(restored);
        showToast(lang === 'ar' ? " تم التراجع عن المسودة السابقة !" : "Draft rolled back successfully !");
      } else {
        showToast(lang === 'ar' ? " لا توجد تعديلات سابقة للتراجع عنها" : "No revision history found to undo.");
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Admin Plan Updating Action
  const triggerSavePlan = async (pId: string) => {
    try {
      const res = await fetch(`/api/admin/plans/${pId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(planForm)
      });
      const data = await res.json();
      if (data.success) {
        setEditingPlanId(null);
        setPlanForm({});
        await loadData();
        showToast(lang === 'ar' ? "تم تحديث الباقة الرقمية بنجاح !" : "Plan pricing updated successfully !");
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Admin Create Plan Action
  const triggerCreatePlan = async () => {
    const randomId = `plan-${Math.floor(Math.random() * 1000)}`;
    const templateBody = {
      id: randomId,
      price: 199,
      billing: "monthly",
      name: {
        en: 'Custom Tailored Growth',
        ar: 'الباقة المخصصة المترابطة'
      },
      features: {
        en: ['Custom localized bandwidth', 'SEO audit modules'],
        ar: ['صلاحيات سحب مخصصة', 'وحدات ممتدة لتتبع الكلمات']
      },
      maxRewrites: 15000,
      maxArticles: 1500
    };

    try {
      const res = await fetch(`/api/admin/plans`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(templateBody)
      });
      const data = await res.json();
      if (data.success) {
        await loadData();
        showToast(lang === 'ar' ? "تم إنشاء باقة مخصصة جديدة بنجاح!" : "Special plan structure established!");
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Admin Edit Subscriber status Action
  const triggerToggleSubStatus = async (subId: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'active' ? 'suspended' : currentStatus === 'suspended' ? 'trial' : 'active';
    try {
      const res = await fetch(`/api/admin/subscriptions/${subId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: nextStatus })
      });
      const data = await res.json();
      if (data.success) {
        await loadData();
        showToast(lang === 'ar' ? "تم تعديل رخصة العميل وجدولتها بنجاح !" : "Client subscription status updated!");
      }
    } catch (e) {
      console.error(e);
    }
  };

  const triggerDeleteSubscription = async (subId: string) => {
    const confirmation = window.confirm(lang === 'ar' ? "هل أنت متأكد من إلغاء وحذف ترخيص هذا المشترك نهائياً؟" : "Are you sure you want to completely revoke and delete this client subscription?");
    if (!confirmation) return;
    try {
      const res = await fetch(`/api/admin/subscriptions/${subId}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (data.success) {
        await loadData();
        showToast(lang === 'ar' ? "تم إلغاء ترخيص العميل بنجاح!" : "Client subscription revoked successfully!");
      }
    } catch (e) {
      console.error(e);
    }
  };

  const triggerResetSubQuota = async (subId: string) => {
    try {
      const res = await fetch(`/api/admin/subscriptions/${subId}/reset`, {
        method: 'POST'
      });
      const data = await res.json();
      if (data.success) {
        await loadData();
        showToast(lang === 'ar' ? "تم تصفير عداد استهلاك العميل بنجاح!" : "Client rewrite usage meter reset!");
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Admin Onboard Subscription flow
  const handleCreateSubscription = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/admin/subscriptions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subForm)
      });
      const data = await res.json();
      if (data.success) {
        setShowAddSubModal(false);
        setSubForm({
          clientName: '',
          email: '',
          planId: 'professional',
          status: 'active',
          durationDays: 30
        });
        await loadData();
        showToast(lang === 'ar' ? "تم إدراج العميل الجديد للخدمة !" : "New client agency fully onboarded!");
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Time format helper for countdown
  const formatCountdown = (secs: number) => {
    const mm = Math.floor(secs / 60);
    const ss = secs % 60;
    return `${mm}:${ss < 10 ? '0' : ''}${ss}`;
  };

  // Categories list
  const categoryKeys = ['Politics', 'Business', 'Technology', 'Science', 'Sports', 'Lifestyle', 'Health'];

  // Language flag emojis
  const flagEmojis = {
    ar: '🇸🇦 العربية',
    en: '🇺🇸 English',
    fr: '🇫🇷 Français',
    zh: '🇨🇳 中文',
    es: '🇪🇸 Español'
  };

  const isRtl = lang === 'ar';

  // Computed layout list for responsive view
  const displayedArticles = showAllArticles ? articles : articles.slice(0, 50);

  return (
    <div className={`min-h-screen transition-colors duration-300 font-sans ${theme === 'dark' ? 'bg-[#020617] text-slate-200' : 'bg-slate-55 text-slate-900'}`} dir={isRtl ? 'rtl' : 'ltr'}>
      {/* GLOWING ACCENTS (Only in dark mode) */}
      {theme === 'dark' && (
        <div className="absolute top-0 left-1/4 w-[500px] h-[300px] bg-indigo-500/5 blur-[120px] rounded-full pointer-events-none" />
      )}

      {/* FIXED SYSTEM NOTIFICATION */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: -40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -40 }}
            className={`fixed top-6 left-1/2 -translate-x-1/2 px-6 py-4 rounded-full z-50 shadow-2xl flex items-center gap-3 text-sm font-medium transition-all ${theme === 'dark' ? 'bg-slate-900 border border-indigo-500/30 text-white shadow-indigo-500/10' : 'bg-white border border-slate-200 text-slate-800 shadow-xl'}`}
          >
            <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-ping" />
            <span>{notification}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* TOP DECORATIVE GLOBAL UTILITIES RAIL */}
      <div className={`text-xs border-b px-4 sm:px-8 py-2.5 flex flex-wrap gap-4 items-center justify-between tracking-wide font-mono transition-all ${theme === 'dark' ? 'bg-slate-950/70 border-slate-800/60 text-slate-400' : 'bg-slate-100 border-slate-200 text-slate-605'}`}>
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
          <span className="font-semibold text-indigo-400 font-sans">Yaqeen VIP Enterprise SaaS</span>
          <span className="opacity-40">|</span>
          <span className="flex items-center gap-1">
            <Globe className="w-3 h-3" />
            {TRANSLATIONS[lang].activeFeeds}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5 font-sans">
            <Clock className="w-3.5 h-3.5" />
            {TRANSLATIONS[lang].syncCountdown} <strong className="text-indigo-400 font-mono tracking-wider ml-1">{formatCountdown(countdown)}</strong>
          </span>
          <span className="opacity-40">|</span>
          <span className="text-xs">{new Date().toISOString().substring(0, 10)} UTC</span>
        </div>
      </div>

      {/* NAV / BRAND HEADER HEADER */}
      <header className={`border-b transition-all sticky top-0 z-40 backdrop-blur-md ${theme === 'dark' ? 'bg-slate-900/80 border-slate-800' : 'bg-white/90 border-slate-200'}`}>
        <div className="max-w-[1600px] mx-auto px-4 sm:px-8 py-4 flex flex-col lg:flex-row gap-4 lg:items-center justify-between">
          <div className="flex items-center justify-between w-full lg:w-auto">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center text-white shadow-md shrink-0 animate-pulse">
                <Sparkles className="w-5.5 h-5.5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className={`text-lg sm:text-2xl font-black tracking-tight font-sans ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                    {lang === 'ar' ? (
                      <>منصة <span className="text-indigo-400 font-normal">يقين</span></>
                    ) : (
                      <>YAQEEN <span className="text-indigo-400 font-normal">PRESS</span></>
                    )}
                  </h1>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${theme === 'dark' ? 'bg-indigo-500/10 text-indigo-400' : 'bg-indigo-100 text-indigo-800'}`}>
                    SaaS v1.4
                  </span>
                </div>
                <p className={`text-[10px] sm:text-xs leading-normal ${theme === 'dark' ? 'text-slate-400' : 'text-slate-505'}`}>
                  {TRANSLATIONS[lang].tagline}
                </p>
              </div>
            </div>

            {/* Mobile/Small screen Dark mode switch side-by-side with brand title */}
            <div className="flex items-center gap-2 lg:hidden">
              <button
                onClick={() => setTheme(prev => prev === 'light' ? 'dark' : 'light')}
                className={`p-2 rounded-full border transition-all ${theme === 'dark' ? 'bg-slate-850 border-slate-800 text-amber-400' : 'bg-slate-100 border-slate-200 text-indigo-900'}`}
                title="Toggle Theme"
              >
                {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* HEAD ACTIONS & INTERFACES SELECTOR */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3.5 w-full lg:w-auto">
            {/* Lang Selection Toolbar */}
            <div className={`p-1 rounded-full flex gap-1 justify-center ${theme === 'dark' ? 'bg-slate-850 border border-slate-800' : 'bg-slate-200/60'} overflow-x-auto no-scrollbar`}>
              {(Object.keys(flagEmojis) as Array<'ar' | 'en' | 'fr' | 'zh' | 'es'>).map((lcode) => (
                <button
                  key={lcode}
                  onClick={() => setLang(lcode)}
                  className={`px-3 py-1 text-xs font-semibold rounded-full transition-all shrink-0 ${lang === lcode ? 'bg-indigo-600 text-white shadow-sm' : theme === 'dark' ? 'text-slate-400 hover:text-white' : 'text-slate-705 hover:text-black'}`}
                >
                  {lcode.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Desktop Dark mode switch */}
            <button
              onClick={() => setTheme(prev => prev === 'light' ? 'dark' : 'light')}
              className={`p-2 rounded-full border transition-all hidden lg:block ${theme === 'dark' ? 'bg-slate-850 border-slate-800 hover:bg-slate-800 text-amber-400' : 'bg-white border-slate-200 hover:bg-slate-100 text-indigo-900'}`}
              title="Toggle Night/Light Mode"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

            <span className="w-px h-6 bg-slate-800 hidden lg:block opacity-20" />

            {/* Segment Controls for active tabs (iOS style, highly responsive) */}
            <div className={`p-1 rounded-xl flex items-center gap-1 w-full sm:w-auto ${theme === 'dark' ? 'bg-[#020617] border border-slate-800/80' : 'bg-slate-100'}`}>
              <button
                onClick={() => setActiveTab('feed')}
                className={`flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all duration-200 ${activeTab === 'feed' ? 'bg-indigo-600 text-white shadow-sm' : theme === 'dark' ? 'text-slate-400 hover:text-white' : 'text-slate-650 hover:text-black'}`}
              >
                <Globe className="w-3.5 h-3.5" />
                <span>{TRANSLATIONS[lang].tabGlobalFeeds}</span>
              </button>

              <button
                onClick={() => setActiveTab('admin')}
                className={`flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all duration-200 ${activeTab === 'admin' ? 'bg-indigo-600 text-white shadow-sm' : theme === 'dark' ? 'text-slate-400 hover:text-white' : 'text-slate-650 hover:text-black'}`}
              >
                <Settings className="w-3.5 h-3.5" />
                <span>{TRANSLATIONS[lang].tabAdminPanel}</span>
              </button>
            </div>
          </div>
        </div>
        <div className={`px-4 sm:px-8 pb-3 max-w-[1600px] mx-auto text-[11px] sm:text-xs font-semibold leading-relaxed tracking-wide ${theme === 'dark' ? 'text-slate-400' : 'text-slate-505'}`}>
          {TRANSLATIONS[lang].subtitle}
        </div>
      </header>

      {/* CORE WRAPPER */}
      <main className="max-w-[1600px] mx-auto px-4 sm:px-8 py-6 sm:py-8">
        
        {/* STATS DECORATIVE HEADER BAR */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className={`rounded-2xl p-4 border transition-all flex flex-col justify-center ${theme === 'dark' ? 'bg-slate-900 border-slate-800 hover:border-slate-700' : 'bg-white border-slate-200 shadow-sm'}`}>
            <div className={`text-xs uppercase tracking-wider font-bold mb-1 ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>{TRANSLATIONS[lang].totalArticles}</div>
            <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
              {stats?.databaseSize || articles.length} <span className="text-indigo-400 text-sm font-normal">RSS Feeds</span>
            </div>
          </div>

          <div className={`rounded-2xl p-4 border transition-all flex flex-col justify-center ${theme === 'dark' ? 'bg-slate-900 border-slate-800 hover:border-slate-700' : 'bg-white border-slate-200 shadow-sm'}`}>
            <div className={`text-xs uppercase tracking-wider font-bold mb-1 ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>{lang === 'ar' ? 'المزامنة التالية' : 'Next Sync'}</div>
            <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
              {formatCountdown(countdown)} <span className="text-indigo-400 text-sm font-normal">{TRANSLATIONS[lang].minutesText}</span>
            </div>
          </div>

          <div className={`rounded-2xl p-4 border transition-all flex flex-col justify-center ${theme === 'dark' ? 'bg-slate-900 border-slate-800 hover:border-slate-700' : 'bg-white border-slate-200 shadow-sm'}`}>
            <div className={`text-xs uppercase tracking-wider font-bold mb-1 ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>{TRANSLATIONS[lang].activeSubs}</div>
            <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
              {stats?.activeSubscriptions || subscriptions.length} <span className="text-indigo-400 text-sm font-normal">+12%</span>
            </div>
          </div>

          <div className={`rounded-2xl p-4 border transition-all flex flex-col justify-center ${theme === 'dark' ? 'bg-gradient-to-br from-indigo-900/20 to-slate-900 border-slate-800/80' : 'bg-indigo-50 border-indigo-200 shadow-sm'}`}>
            <div className={`text-xs uppercase tracking-wider font-bold mb-1 ${theme === 'dark' ? 'text-slate-500' : 'text-indigo-700'}`}>{TRANSLATIONS[lang].autoPruned}</div>
            <div className="flex items-center justify-between">
              <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-indigo-950'}`}>
                62H <span className="text-rose-450 text-sm font-normal">Auto-Purge</span>
              </div>
              <button
                onClick={() => triggerFetchNow()}
                disabled={isSyncing}
                className={`px-3 py-1.5 rounded text-xs font-bold transition-all outline-none ${isSyncing ? 'bg-slate-800 text-slate-500 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 text-white'}`}
              >
                <RefreshCw className={`w-3 h-3 inline mr-1 ${isSyncing ? 'animate-spin' : ''}`} />
                <span>{isSyncing ? '...' : (lang === 'ar' ? 'جلب' : 'Sync')}</span>
              </button>
            </div>
          </div>
        </section>

        {activeTab === 'feed' ? (
          <div>
            {selectedArticle ? (
              /* DEDICATED PREPARATION & PROFESSIONAL REWRITING WORKSPACE */
              <div className="space-y-6">
                {/* Back Button and Title Nav Row */}
                <div className={`p-4 sm:p-5 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all ${theme === 'dark' ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-sm'}`}>
                  <button
                    onClick={() => setSelectedArticle(null)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all outline-none ${theme === 'dark' ? 'bg-slate-800 hover:bg-slate-700 text-indigo-400' : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-800'}`}
                  >
                    <ArrowRight className={`w-4 h-4 ${isRtl ? '' : 'rotate-180'}`} />
                    <span>{TRANSLATIONS[lang].btnBackToFeeds}</span>
                  </button>
                  <div>
                    <h2 className="text-sm sm:text-base font-extrabold text-indigo-400 flex items-center gap-1.5">
                      <Sparkles className="w-4.5 h-4.5 animate-pulse" />
                      <span>{TRANSLATIONS[lang].preparationSuiteTitle}</span>
                    </h2>
                  </div>
                </div>

                {/* Comparative Workspace */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                  
                  {/* LEFT AREA: ORIGINAL AND SETTINGS (5 COLS) */}
                  <div className="lg:col-span-5 space-y-6">
                    {/* ORIGINAL SOURCE WIRE CARD */}
                    <div className={`p-5 rounded-3xl border ${theme === 'dark' ? 'bg-slate-900 border-slate-800 text-slate-405' : 'bg-white border-slate-200 shadow-sm'}`}>
                      <div className="flex items-center justify-between pb-3 border-b border-slate-800/40 mb-4">
                        <span className="text-[10px] font-bold text-slate-500 uppercase block">
                          {TRANSLATIONS[lang].originalTextLabel}
                        </span>
                        <span className="text-[10px] bg-slate-950 px-2 py-0.5 rounded text-indigo-400 font-mono font-bold">
                          {selectedArticle.source}
                        </span>
                      </div>
                      <h3 className={`text-sm font-extrabold mb-3 leading-snug ${theme === 'dark' ? 'text-slate-200' : 'text-slate-800'}`}>
                        {selectedArticle.originalTitle}
                      </h3>
                      <p className={`text-xs leading-relaxed ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>
                        {selectedArticle.originalContent}
                      </p>
                    </div>

                    {/* CLIENT EDITOR RE-WRITING PANEL */}
                    <div className={`p-5 rounded-3xl border ${theme === 'dark' ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-sm'}`}>
                      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-800/40">
                        <Sliders className="w-4.5 h-4.5 text-indigo-400" />
                        <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                          {TRANSLATIONS[lang].editorRewriterSuite}
                        </h3>
                      </div>

                      {/* Select Language target */}
                      <div className="mb-4">
                        <label className={`text-[11px] font-bold block mb-1.5 uppercase ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>
                          {TRANSLATIONS[lang].viewLanguageLabel}
                        </label>
                        <select
                          value={targetRewriteLang}
                          onChange={(e) => setTargetRewriteLang(e.target.value as any)}
                          className={`w-full text-xs rounded-xl px-3.5 py-2.5 outline-none transition-all ${theme === 'dark' ? 'bg-slate-950 text-white border border-slate-800' : 'bg-slate-100 border border-slate-200 text-slate-800'}`}
                        >
                          {(Object.keys(flagEmojis) as Array<'ar' | 'en' | 'fr' | 'zh' | 'es'>).map((code) => (
                            <option key={code} value={code}>
                              {flagEmojis[code]}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Select Tone preset */}
                      <div className="mb-4">
                        <label className={`text-[11px] font-bold block mb-1.5 uppercase ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>
                          {TRANSLATIONS[lang].selectTone}
                        </label>
                        <div className="flex flex-col gap-1.5">
                          {DEFAULT_TONES.map((t) => {
                            const isSelected = selectedTone === t.id;
                            const tName = t.name[lang] || t.name.en;
                            return (
                              <button
                                key={t.id}
                                onClick={() => setSelectedTone(t.id)}
                                className={`text-left text-xs px-3.5 py-2.5 rounded-xl font-semibold transition-all flex items-center justify-between ${isSelected ? 'bg-indigo-650 text-white shadow-sm' : theme === 'dark' ? 'bg-slate-950 text-slate-400 hover:text-white border border-slate-850' : 'bg-slate-100 text-slate-700 hover:bg-slate-205 border border-transparent'}`}
                              >
                                <span>{tName}</span>
                                {isSelected && <CheckCircle className="w-3.5 h-3.5 text-white" />}
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      {/* Text instruction */}
                      <div className="mb-4">
                        <label className={`text-[11px] font-bold block mb-1.5 uppercase ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>
                          {TRANSLATIONS[lang].customRewriteInstruction}
                        </label>
                        <textarea
                          rows={3}
                          value={customInstruction}
                          onChange={(e) => setCustomInstruction(e.target.value)}
                          placeholder={TRANSLATIONS[lang].rewritePlaceholder}
                          className={`w-full text-xs rounded-xl px-3.5 py-3 placeholder-slate-500 outline-none transition-all resize-none ${theme === 'dark' ? 'bg-slate-950 text-white focus:bg-slate-950 border border-slate-805' : 'bg-slate-100 focus:bg-white border border-transparent focus:border-slate-200'}`}
                        />
                      </div>

                      {/* Run Rewrite Dispatch Button */}
                      <div className="space-y-2">
                        <button
                          onClick={handleAIRewrite}
                          disabled={isRewriting}
                          className={`w-full py-3.5 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg ${isRewriting ? 'bg-slate-800 text-slate-550 cursor-not-allowed text-center' : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-950/20'}`}
                        >
                          <Sparkles className={`w-4 h-4 ${isRewriting ? 'animate-spin' : ''}`} />
                          <span>{isRewriting ? TRANSLATIONS[lang].syncingText : TRANSLATIONS[lang].btnGeminiRewrite}</span>
                        </button>

                        {/* Rollback/Undo action if there are items in history queue */}
                        {selectedArticle.history.length > 0 && (
                          <button
                            onClick={handleRollback}
                            className={`w-full py-2.5 rounded-xl font-semibold text-xs flex items-center justify-center gap-1.5 transition-all outline-none border ${theme === 'dark' ? 'bg-slate-950 hover:bg-slate-850 text-indigo-400 border-slate-850' : 'bg-slate-100 hover:bg-slate-200 text-indigo-805 border-slate-200'}`}
                          >
                            <Undo2 className="w-3.5 h-3.5" />
                            <span>{TRANSLATIONS[lang].btnUndoRewrite} ({selectedArticle.history.length})</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* RIGHT AREA: REWRITTEN CONTENT (7 COLS) */}
                  <div className="lg:col-span-7 space-y-6">
                    <div className={`p-6 sm:p-8 rounded-3xl border transition-all ${theme === 'dark' ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-sm'}`}>
                      <div className="flex flex-wrap items-center justify-between gap-2.5 pb-4 border-b border-slate-800/40 mb-6">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold bg-indigo-500/10 text-indigo-400 px-2.5 py-1 rounded">
                            {selectedArticle.source}
                          </span>
                          <span className="text-xs text-slate-505">
                            {new Date(selectedArticle.fetchedAt).toLocaleString()}
                          </span>
                        </div>
                        <a
                          href={selectedArticle.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[11px] font-semibold text-indigo-400 hover:underline flex items-center gap-1.5"
                        >
                          <span>{TRANSLATIONS[lang].originalSourceLink}</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      </div>

                      {/* SEO PLACARD */}
                      <span className="text-[10px] font-bold block tracking-wider uppercase text-indigo-400 mb-1">
                        {TRANSLATIONS[lang].optimizedSEOText}
                      </span>

                      {/* RENDER HEADLINE */}
                      <h2 className={`text-xl sm:text-2xl font-black tracking-tight leading-snug mb-4 ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                        {selectedArticle.title}
                      </h2>

                      {/* META DESCRIPTION BOX */}
                      <div className={`p-4 rounded-xl mb-6 text-xs border border-dashed leading-relaxed ${theme === 'dark' ? 'bg-slate-950/80 border-slate-850 text-slate-350' : 'bg-slate-50 border-slate-200 text-slate-705'}`}>
                        <strong className="text-indigo-400 block mb-1 font-bold">
                          {TRANSLATIONS[lang].metaDescription}
                        </strong>
                        {selectedArticle.seoDescription}
                      </div>

                      {/* REWRITTEN PARAGRAPHS */}
                      <div className="space-y-5 text-sm sm:text-base leading-relaxed text-justify mb-8">
                        {selectedArticle.content.map((para, pIdx) => (
                          <p key={pIdx} className={theme === 'dark' ? 'text-slate-300' : 'text-slate-800'}>
                            {para}
                          </p>
                        ))}
                      </div>

                      {/* KEYWORDS TAGS REGISTRY */}
                      <div className="border-t border-slate-800/40 pt-4">
                        <span className={`text-[11px] font-bold block mb-2 uppercase ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>
                          {TRANSLATIONS[lang].seoKeywords}
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {selectedArticle.seoKeywords.map((tag, tIdx) => (
                            <span
                              key={tIdx}
                              className={`text-xs px-2.5 py-1 rounded-lg font-bold ${theme === 'dark' ? 'bg-slate-950 text-indigo-300' : 'bg-indigo-50 text-indigo-800'}`}
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Quick Copy Feature */}
                      <div className="mt-6 pt-4 border-t border-slate-800/40 flex justify-end">
                        <button
                          onClick={() => {
                            const fullDraft = `${selectedArticle.title}\n\n${selectedArticle.seoDescription}\n\n${selectedArticle.content.join('\n\n')}\n\nKeywords: ${selectedArticle.seoKeywords.join(', ')}`;
                            navigator.clipboard.writeText(fullDraft);
                            showToast(lang === 'ar' ? 'تم نسخ نص المقال ومسودة السيو بالكامل!' : 'Article full draft copied successfully!');
                          }}
                          className={`px-4.5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none ${theme === 'dark' ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/10' : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-800'}`}
                        >
                          {lang === 'ar' ? 'نسخ الخبر بالكامل' : 'Copy Full Paraphrased Draft'}
                        </button>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            ) : (
              /* GLOBAL GRID VIEW SEARCH AND DISCOVERY PANEL */
              <div className="space-y-8">
                {/* Search, Categories Filter Desk */}
                <div className={`p-5 rounded-3xl border ${theme === 'dark' ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-sm'}`}>
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-center">
                    {/* Search Field */}
                    <div className="md:col-span-5 relative">
                      <Search className={`absolute top-3.5 w-4 h-4 ${isRtl ? 'left-3.5' : 'right-3.5'} opacity-50`} />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder={TRANSLATIONS[lang].searchPlaceholder}
                        className={`w-full text-sm rounded-xl px-4 py-3 placeholder-slate-500 outline-none transition-all ${theme === 'dark' ? 'bg-slate-950/70 text-white focus:bg-slate-950 focus:ring-1 focus:ring-indigo-500/50 border border-slate-850' : 'bg-slate-100 focus:bg-white focus:ring-1 focus:ring-indigo-500 border border-transparent focus:border-slate-200'}`}
                      />
                    </div>

                    {/* Original language filter tags */}
                    <div className="md:col-span-7 flex flex-row items-center gap-1.5 overflow-x-auto no-scrollbar py-1 -mx-4 px-4 md:mx-0 md:px-0">
                      <span className={`text-[10px] font-bold uppercase tracking-wider shrink-0 ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'} mr-2`}>
                        {TRANSLATIONS[lang].originalLanguageLabel}:
                      </span>
                      <button
                        onClick={() => setSelectedLanguageFilter('')}
                        className={`px-3 py-1.5 text-xs font-bold rounded-xl transition-all shrink-0 ${selectedLanguageFilter === '' ? 'bg-indigo-600 text-white shadow' : theme === 'dark' ? 'bg-slate-950 text-slate-400 hover:text-white border border-slate-850' : 'bg-slate-100 hover:bg-slate-200 text-slate-705'}`}
                      >
                        {lang === 'ar' ? 'الكل' : 'All'}
                      </button>
                      {(Object.keys(flagEmojis) as Array<'ar' | 'en' | 'fr' | 'zh' | 'es'>).map((lkey) => (
                        <button
                          key={lkey}
                          onClick={() => setSelectedLanguageFilter(lkey)}
                          className={`px-3 py-1.5 text-xs font-bold rounded-xl transition-all shrink-0 ${selectedLanguageFilter === lkey ? 'bg-indigo-600 text-white shadow' : theme === 'dark' ? 'bg-slate-950 text-slate-400 hover:text-white border border-slate-850' : 'bg-slate-100 hover:bg-slate-200 text-slate-705'}`}
                        >
                          {flagEmojis[lkey]}
                        </button>
                      ))}
                    </div>
                  </div>
 
                  <div className="border-t border-slate-800/40 mt-4 pt-4">
                    <div className="flex flex-row items-center gap-2 overflow-x-auto no-scrollbar py-1 -mx-4 px-4 md:mx-0 md:px-0">
                      <span className={`text-[10px] font-bold uppercase tracking-wider shrink-0 ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'} mr-2`}>
                        {TRANSLATIONS[lang].allCategories}:
                      </span>
                      <button
                        onClick={() => setSelectedCategory('')}
                        className={`px-3.5 py-1.5 text-xs font-bold rounded-xl transition-all shrink-0 ${selectedCategory === '' ? 'bg-indigo-600 text-white shadow' : theme === 'dark' ? 'bg-slate-950 text-slate-400 hover:text-white border border-slate-850' : 'bg-slate-100 text-slate-705 hover:bg-slate-200'}`}
                      >
                        {TRANSLATIONS[lang].allCategories}
                      </button>
                      {categoryKeys.map((catKey) => {
                        const displayCat = TRANSLATIONS[lang][`category${catKey}` as keyof typeof TRANSLATIONS['en']] || catKey;
                        const isSelected = selectedCategory === catKey;
                        return (
                          <button
                            key={catKey}
                            onClick={() => setSelectedCategory(isSelected ? '' : catKey)}
                            className={`px-3.5 py-1.5 text-xs font-bold rounded-xl transition-all shrink-0 ${isSelected ? 'bg-indigo-600 text-white shadow' : theme === 'dark' ? 'bg-slate-950 text-slate-400 hover:text-white border border-slate-850' : 'bg-slate-100 text-slate-700 hover:bg-slate-205'}`}
                          >
                            {displayCat}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Dashboard articles display grid - Centered Layout */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {articles.length === 0 ? (
                    <div className={`col-span-full p-16 rounded-3xl border text-center ${theme === 'dark' ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-sm'}`}>
                      <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-amber-500 animate-bounce" />
                      <p className={`text-base font-bold mb-1 ${theme === 'dark' ? 'text-slate-300' : 'text-slate-750'}`}>
                        {TRANSLATIONS[lang].noArticlesFound}
                      </p>
                      <p className="text-xs text-slate-505">
                        Try clearing keywords or select a different category option from above.
                      </p>
                    </div>
                  ) : (
                    displayedArticles.map((art) => {
                      const dateFormatted = new Date(art.fetchedAt).toLocaleDateString([], { month: 'short', day: 'numeric' }) + ' ' + new Date(art.fetchedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                      return (
                        <motion.div
                          key={art.id}
                          layoutId={`card-${art.id}`}
                          onClick={() => {
                            setSelectedArticle(art);
                            setTargetRewriteLang(art.language);
                          }}
                          className={`p-5 rounded-3xl border cursor-pointer hover:scale-[1.015] hover:-translate-y-1 hover:shadow-xl transition-all duration-300 relative flex flex-col justify-between ${theme === 'dark' ? 'bg-slate-900 hover:bg-slate-850/90 border-slate-800 hover:border-indigo-500/50 text-white' : 'bg-white border-slate-200 hover:border-indigo-300 hover:shadow-indigo-500/5'}`}
                        >
                          <div>
                            {/* Meta site title / Time indicator */}
                            <div className="flex items-center justify-between mb-3 pb-2 border-b border-dashed border-slate-800">
                              <span className="text-[10px] font-mono uppercase bg-indigo-500/10 text-indigo-400 font-bold px-2 py-0.5 rounded">
                                {art.source}
                              </span>
                              <span className="text-[10px] text-slate-505 font-mono flex items-center gap-1">
                                <Clock className="w-2.5 h-2.5" />
                                {dateFormatted}
                              </span>
                            </div>

                            {/* Title text */}
                            <h4 className={`text-xs sm:text-sm font-extrabold leading-snug line-clamp-2 mb-2 group-hover:text-indigo-400 ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                              {art.title}
                            </h4>

                            {/* Description */}
                            <p className={`text-[11px] line-clamp-3 mb-4 leading-relaxed ${theme === 'dark' ? 'text-slate-400' : 'text-slate-550'}`}>
                              {art.originalContent}
                            </p>
                          </div>

                          {/* Footer details tags - Language badges */}
                          <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-800">
                            <span className="text-[10px] font-semibold text-slate-500 flex items-center gap-1">
                              {flagEmojis[art.language]}
                            </span>
                            <div className="flex items-center gap-1">
                              {art.history.length > 0 && (
                                <span className="text-[9px] bg-indigo-500/10 text-indigo-400 font-bold px-1.5 py-0.5 rounded">
                                  AI Rev {art.history.length}
                                </span>
                              )}
                              <span className="text-[9px] font-bold bg-slate-950 text-indigo-400 hover:text-white px-2.5 py-1 rounded-full transition-all flex items-center gap-1">
                                <span>صياغة حصرية</span>
                                <Sparkles className="w-2.5 h-2.5" />
                              </span>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })
                  )}
                </div>

                {/* SHOW ALL EXTRAS ACCORDION */}
                {!showAllArticles && articles.length > 50 && (
                  <div className="text-center pt-4">
                    <button
                      onClick={() => {
                        setShowAllArticles(true);
                        showToast(lang === 'ar' ? 'تم جلب واستعراض كامل المقالات الصحفية !' : 'All available news wire articles loaded !');
                      }}
                      className="px-8 py-4 rounded-2xl border border-dashed text-xs font-bold transition-all hover:bg-indigo-650/10 hover:border-indigo-550 text-indigo-500"
                    >
                      {TRANSLATIONS[lang].loadMore} ({articles.length - 50}+)
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          
          /* SAAS BACKSTAGE / CONTROL ADMIN PANEL */
          <div className="space-y-10">
            
            {/* SAAS METRICS SUITE - KPIS STATS */}
            {(() => {
              const calculatedMRR = subscriptions.reduce((sum, sub) => {
                if (sub.status !== 'active') return sum;
                const plan = plans.find(p => p.id === sub.planId);
                return sum + (plan ? plan.price : 0);
              }, 0);

              const activeSubsCount = subscriptions.filter(s => s.status === 'active').length;
              const totalAIUsageCount = subscriptions.reduce((sum, sub) => sum + (sub.rewritesUsed || 0), 0);
              const totalPlansRegistered = plans.length;

              return (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  {/* MRR ESTIMATE CARD */}
                  <motion.div
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.05 }}
                    className={`rounded-2xl p-6 border transition-all relative overflow-hidden flex flex-col justify-between ${theme === 'dark' ? 'bg-[#0f172a] border-slate-800 hover:border-slate-700/80' : 'bg-white border-slate-200 shadow-sm hover:shadow-md'}`}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <span className={`text-xs uppercase tracking-wider font-extrabold ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
                        {lang === 'ar' ? 'العوائد المتكررة المقدرة MRR' : 'Estimated SaaS MRR'}
                      </span>
                      <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                        <TrendingUp className="w-4 h-4" />
                      </div>
                    </div>
                    <div>
                      <div className={`text-3xl font-black ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                        ${calculatedMRR.toLocaleString()}
                        <span className="text-xs font-normal text-slate-500 ml-1.5">/ USD</span>
                      </div>
                      <p className="text-[11px] text-emerald-500 font-semibold mt-1 flex items-center gap-1">
                        <span>↑ 18.4% {lang === 'ar' ? 'نمو شهري تراكمي' : 'month-over-month growth'}</span>
                      </p>
                    </div>
                    {theme === 'dark' && (
                      <div className="absolute -bottom-8 -right-8 w-24 h-24 bg-emerald-500/5 rounded-full blur-xl pointer-events-none" />
                    )}
                  </motion.div>

                  {/* ACTIVE CLIENTS LICENSES CARD */}
                  <motion.div
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.1 }}
                    className={`rounded-2xl p-6 border transition-all relative overflow-hidden flex flex-col justify-between ${theme === 'dark' ? 'bg-[#0f172a] border-slate-800 hover:border-slate-700/80' : 'bg-white border-slate-200 shadow-sm hover:shadow-md'}`}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <span className={`text-xs uppercase tracking-wider font-extrabold ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
                        {lang === 'ar' ? 'التراخيص والمؤسسات النشطة' : 'Onboarded Outlets'}
                      </span>
                      <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                        <Users className="w-4 h-4" />
                      </div>
                    </div>
                    <div>
                      <div className={`text-3xl font-black ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                        {activeSubsCount}{' '}
                        <span className="text-sm font-normal text-slate-500">
                          {lang === 'ar' ? 'من أصل' : 'active of'}{' '}
                          <strong className="font-extrabold text-indigo-400">{subscriptions.length}</strong>
                        </span>
                      </div>
                      <p className="text-[11px] text-indigo-400 font-semibold mt-1 flex items-center gap-1">
                        <span>● Live client enterprise nodes deployed</span>
                      </p>
                    </div>
                    {theme === 'dark' && (
                      <div className="absolute -bottom-8 -right-8 w-24 h-24 bg-indigo-500/5 rounded-full blur-xl pointer-events-none" />
                    )}
                  </motion.div>

                  {/* COMPUTED TOTAL REWRITES CARD */}
                  <motion.div
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.15 }}
                    className={`rounded-2xl p-6 border transition-all relative overflow-hidden flex flex-col justify-between ${theme === 'dark' ? 'bg-[#0f172a] border-slate-800 hover:border-slate-700/80' : 'bg-white border-slate-200 shadow-sm hover:shadow-md'}`}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <span className={`text-xs uppercase tracking-wider font-extrabold ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
                        {lang === 'ar' ? 'إجمالي معالجات الذكاء الاصطناعي' : 'AI Queries Outflow'}
                      </span>
                      <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
                        <Sparkles className="w-4 h-4" />
                      </div>
                    </div>
                    <div>
                      <div className={`text-3xl font-black ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                        {totalAIUsageCount.toLocaleString()}
                        <span className="text-xs font-normal text-slate-500 ml-1.5">{lang === 'ar' ? 'مسودة' : 'drafts'}</span>
                      </div>
                      <p className="text-[11px] text-amber-500 font-semibold mt-1">
                        {lang === 'ar' ? 'معدل الاستجابة للملخص: 1.4 ثانية' : 'Avg optimization request: 1.4s'}
                      </p>
                    </div>
                    {theme === 'dark' && (
                      <div className="absolute -bottom-8 -right-8 w-24 h-24 bg-amber-500/5 rounded-full blur-xl pointer-events-none" />
                    )}
                  </motion.div>

                  {/* GLOBAL PRESS REGISTRY REACH CARD */}
                  <motion.div
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.2 }}
                    className={`rounded-2xl p-6 border transition-all relative overflow-hidden flex flex-col justify-between ${theme === 'dark' ? 'bg-[#0f172a] border-slate-800 hover:border-slate-700/80' : 'bg-white border-slate-200 shadow-sm hover:shadow-md'}`}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <span className={`text-xs uppercase tracking-wider font-extrabold ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
                        {lang === 'ar' ? 'قوالب الباقات المتاحة' : 'Active Subscription Plans'}
                      </span>
                      <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400">
                        <Database className="w-4 h-4" />
                      </div>
                    </div>
                    <div>
                      <div className={`text-3xl font-black ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                        {totalPlansRegistered}{' '}
                        <span className="text-xs font-normal text-slate-500">{lang === 'ar' ? 'باقات تسعير' : 'SaaS pricing models'}</span>
                      </div>
                      <p className="text-[11px] text-cyan-400 font-semibold mt-1">
                        {lang === 'ar' ? 'يدعم نماذج الشركات الضخمة والملخصات' : 'Enterprise custom models supported'}
                      </p>
                    </div>
                    {theme === 'dark' && (
                      <div className="absolute -bottom-8 -right-8 w-24 h-24 bg-cyan-500/5 rounded-full blur-xl pointer-events-none" />
                    )}
                  </motion.div>
                </div>
              );
            })()}

            {/* SUBSCRIPTIONS AND REGISTERED USERS WORKSPACE */}
            <div className={`p-6 sm:p-8 rounded-3xl border ${theme === 'dark' ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-sm'}`}>
              
              {/* DESK HEADER BAR */}
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-8 border-b border-dashed pb-6 border-slate-800/40">
                <div>
                  <h3 className="text-xl font-black tracking-tight flex items-center gap-2.5">
                    <Users className="w-5.5 h-5.5 text-indigo-400" />
                    <span>{TRANSLATIONS[lang].manageSubscriptions}</span>
                  </h3>
                  <p className={`text-xs mt-1 leading-normal ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
                    {lang === 'ar'
                      ? 'التحكم ومراقبة رخص وكالات الأنباء الدولية، تصفير كوتا المقالات، المزامنة، وتفعيل فترات الحوسبة الكلية.'
                      : 'Audit licenses, monitor operational telemetry data, reset AI quota usages and configure client life cycles.'}
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <button
                    onClick={() => setShowAddSubModal(true)}
                    className="px-5 py-3 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white flex items-center gap-2 transition-all outline-none shadow-lg shadow-indigo-600/10"
                  >
                    <Plus className="w-4 h-4" />
                    <span>{TRANSLATIONS[lang].newSubscription}</span>
                  </button>
                </div>
              </div>

              {/* SEARCH & FILTERS CONTROLS */}
              <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 mb-6">
                {/* Search Inbox Input */}
                <div className="relative flex-1 max-w-md">
                  <span className="absolute inset-y-0 left-3.5 flex items-center pointer-events-none text-slate-500">
                    <Search className="w-4 h-4" />
                  </span>
                  <input
                    type="text"
                    value={clientSearchQuery}
                    onChange={(e) => setClientSearchQuery(e.target.value)}
                    placeholder={lang === 'ar' ? 'البحث عن منظمة صحفية أو بريد إلكتروني...' : 'Search subscriber name or key domain...'}
                    className={`w-full text-xs rounded-xl pl-10 pr-4 py-3 outline-none transition-all ${
                      theme === 'dark'
                        ? 'bg-slate-950 text-white border border-slate-800/80 focus:border-indigo-500'
                        : 'bg-slate-50 border border-slate-200 focus:border-indigo-400 text-slate-800'
                    }`}
                  />
                </div>

                {/* Status Categories Filters */}
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`text-xs font-bold uppercase tracking-wider mr-1 ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>
                    {lang === 'ar' ? 'فلترة حسب الحالة:' : 'Lifecycle Status:'}
                  </span>
                  <div className={`p-1 rounded-full flex gap-1 ${theme === 'dark' ? 'bg-[#020617] border border-slate-800' : 'bg-slate-100'}`}>
                    <button
                      onClick={() => setClientStatusFilter('')}
                      className={`px-3 py-1 text-xs font-bold rounded-full transition-all ${
                        !clientStatusFilter
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : theme === 'dark'
                          ? 'text-slate-400 hover:text-white'
                          : 'text-slate-600 hover:text-black'
                      }`}
                    >
                      {lang === 'ar' ? 'الكل' : 'All'} ({subscriptions.length})
                    </button>
                    <button
                      onClick={() => setClientStatusFilter('active')}
                      className={`px-3 py-1 text-xs font-bold rounded-full transition-all ${
                        clientStatusFilter === 'active'
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : theme === 'dark'
                          ? 'text-emerald-400 hover:text-emerald-300'
                          : 'text-emerald-600 hover:text-emerald-800'
                      }`}
                    >
                      {lang === 'ar' ? 'نشط' : 'Active'} ({subscriptions.filter((s) => s.status === 'active').length})
                    </button>
                    <button
                      onClick={() => setClientStatusFilter('trial')}
                      className={`px-3 py-1 text-xs font-bold rounded-full transition-all ${
                        clientStatusFilter === 'trial'
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : theme === 'dark'
                          ? 'text-cyan-400 hover:text-cyan-300'
                          : 'text-cyan-600 hover:text-cyan-800'
                      }`}
                    >
                      {lang === 'ar' ? 'تجريبي' : 'Trial'} ({subscriptions.filter((s) => s.status === 'trial').length})
                    </button>
                    <button
                      onClick={() => setClientStatusFilter('suspended')}
                      className={`px-3 py-1 text-xs font-bold rounded-full transition-all ${
                        clientStatusFilter === 'suspended'
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : theme === 'dark'
                          ? 'text-rose-400 hover:text-rose-350'
                          : 'text-rose-600 hover:text-rose-800'
                      }`}
                    >
                      {lang === 'ar' ? 'معلق' : 'Suspended'} ({subscriptions.filter((s) => s.status === 'suspended').length})
                    </button>
                  </div>
                </div>
              </div>

              {/* SUBSCRIPTION TABLE / REGISTRY GRID */}
              <div className="overflow-x-auto rounded-2xl border border-slate-800/10">
                {(() => {
                  const filteredSubs = subscriptions.filter((sub) => {
                    const plan = plans.find((p) => p.id === sub.planId);
                    const planNameEn = plan ? plan.name.en.toLowerCase() : '';
                    const planNameAr = plan ? (plan.name.ar || '').toLowerCase() : '';
                    const clientName = sub.clientName.toLowerCase();
                    const email = sub.email.toLowerCase();

                    const matchesSearch =
                      clientName.includes(clientSearchQuery.toLowerCase()) ||
                      email.includes(clientSearchQuery.toLowerCase()) ||
                      planNameEn.includes(clientSearchQuery.toLowerCase()) ||
                      planNameAr.includes(clientSearchQuery.toLowerCase());

                    const matchesStatus = clientStatusFilter ? sub.status === clientStatusFilter : true;

                    return matchesSearch && matchesStatus;
                  });

                  if (filteredSubs.length === 0) {
                    return (
                      <div className="p-16 text-center">
                        <Users className="w-12 h-12 mx-auto text-slate-500 mb-3 animate-pulse" />
                        <h4 className={`text-sm font-bold ${theme === 'dark' ? 'text-slate-300' : 'text-slate-700'}`}>
                          {lang === 'ar' ? 'لم يتم العثور على أي منظمة تفي بالشروط' : 'No matching subscribers found'}
                        </h4>
                        <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
                          {lang === 'ar' ? 'يرجى مراجعة محتوى مربع البحث وتعديل الفلترة النشطة حالياً.' : 'Refine your search queries or adjust status filters.'}
                        </p>
                      </div>
                    );
                  }

                  return (
                    <table className="w-full text-left text-xs sm:text-sm tracking-normal">
                      <thead>
                        <tr className={`border-b text-[10px] uppercase font-bold tracking-wider ${theme === 'dark' ? 'border-slate-800 text-slate-400 bg-slate-950/20' : 'border-slate-200 text-slate-500 bg-slate-50'}`}>
                          <th className="py-4 px-5">{TRANSLATIONS[lang].clientOrg}</th>
                          <th className="py-4 px-5">Plan Package</th>
                          <th className="py-4 px-5">Contract E-Mail</th>
                          <th className="py-4 px-5">Expiry Date</th>
                          <th className="py-4 px-5 text-right">{lang === 'ar' ? 'معدل استهلاك الذكاء الاصطناعي (جرى صياغتها)' : 'AI Quota Outlay'}</th>
                          <th className="py-4 px-5 text-center">{lang === 'ar' ? 'حالة الحساب' : 'License State'}</th>
                          <th className="py-4 px-5 text-center">{lang === 'ar' ? 'أدوات الإدارة السريعة' : 'Actions Toolbelt'}</th>
                        </tr>
                      </thead>
                      <tbody className={`divide-y ${theme === 'dark' ? 'divide-slate-805/40 border-slate-800' : 'divide-slate-150 border-slate-150'}`}>
                        {filteredSubs.map((sub) => {
                          const associatedPlan = plans.find((p) => p.id === sub.planId);
                          const planName = associatedPlan ? associatedPlan.name[lang] || associatedPlan.name.en : sub.planId;
                          const maxRewritesAllowed = associatedPlan ? associatedPlan.maxRewrites : 1000;
                          
                          // Calculate exact credit progress bar details
                          const progressPercentage = Math.min(100, Math.round(((sub.rewritesUsed || 0) / maxRewritesAllowed) * 100));
                          
                          // Determine color coding based on usage tiers to warn admins
                          const progressColor =
                            progressPercentage < 50
                              ? 'from-emerald-500 to-teal-500'
                              : progressPercentage < 85
                              ? 'from-amber-500 to-orange-500'
                              : 'from-rose-500 to-red-500';

                          return (
                            <tr key={sub.id} className={`transition-all ${theme === 'dark' ? 'hover:bg-slate-850/50' : 'hover:bg-slate-50/50'}`}>
                              {/* AVATAR + ORGANISATION DESIGN */}
                              <td className="py-4 px-5 font-bold">
                                <div className="flex items-center gap-3">
                                  <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-extrabold text-xs tracking-wider shrink-0 shadow-inner ${
                                    sub.planId === 'agency'
                                      ? 'bg-amber-600/10 text-amber-400'
                                      : sub.planId === 'professional'
                                      ? 'bg-indigo-600/10 text-indigo-400'
                                      : 'bg-slate-500/10 text-slate-400'
                                  }`}>
                                    {sub.clientName.trim().substring(0, 2).toUpperCase()}
                                  </div>
                                  <div>
                                    <div className="flex items-center gap-2 flex-wrap">
                                      <span className={`block font-extrabold font-sans text-xs ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>{sub.clientName}</span>
                                      {progressPercentage >= 90 && (
                                        <span className={`text-[9px] font-black px-1.5 py-0.5 rounded-md uppercase tracking-wider animate-pulse inline-flex items-center gap-1 shrink-0 ${
                                          theme === 'dark'
                                            ? 'bg-rose-500/20 text-rose-450 border border-rose-500/30'
                                            : 'bg-rose-100 text-rose-800 border border-rose-250 shadow-sm'
                                        }`} title={lang === 'ar' ? 'تجاوز المشترك 90% من الحصة الشهرية' : 'Exceeded 90% of AI Quota'}>
                                          {TRANSLATIONS[lang].quotaWarningBadge || TRANSLATIONS.en.quotaWarningBadge}
                                        </span>
                                      )}
                                    </div>
                                    <span className="text-[10px] text-slate-500 block font-normal tracking-tight font-mono">ID: {sub.id}</span>
                                  </div>
                                </div>
                              </td>

                              {/* PLAN CAPSULE */}
                              <td className="py-4 px-5">
                                <span className={`text-[9px] font-extrabold uppercase px-2 py-1 rounded-full ${
                                  sub.planId === 'agency'
                                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                    : sub.planId === 'professional'
                                    ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                                    : 'bg-slate-500/10 text-slate-400 border border-slate-500/10'
                                }`}>
                                  {planName}
                                </span>
                              </td>

                              {/* CONTACT EMAIL */}
                              <td className="py-4 px-5 font-mono text-xs text-slate-400">
                                {sub.email}
                              </td>

                              {/* EXPIRE DATE WITH RELATIVE TEXT */}
                              <td className="py-4 px-5 text-xs font-mono">
                                <div className="flex items-center gap-1.5 text-slate-400">
                                  <Calendar className="w-3.5 h-3.5 text-slate-500" />
                                  <span>{new Date(sub.expiresDate).toLocaleDateString()}</span>
                                </div>
                              </td>

                              {/* DETAILED REWRITE PROGRESS GAUGE */}
                              <td className="py-4 px-5 text-right w-[200px]">
                                <div className="space-y-1 text-right">
                                  <div className="flex justify-between items-center text-[10px] font-mono font-bold">
                                    <span className={`inline-flex items-center gap-1 ${progressPercentage >= 90 ? 'text-rose-550 dark:text-rose-400 animate-pulse' : 'text-slate-505 text-indigo-400'}`}>
                                      {progressPercentage >= 90 && <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0 inline-block" />}
                                      <span>{progressPercentage}% {lang === 'ar' ? 'مستهلك' : 'used'}</span>
                                    </span>
                                    <span className={progressPercentage >= 90 ? 'text-rose-550 dark:text-rose-400' : theme === 'dark' ? 'text-slate-300' : 'text-slate-800'}>
                                      {sub.rewritesUsed.toLocaleString()} <span className="text-slate-500">/ {maxRewritesAllowed.toLocaleString()}</span>
                                    </span>
                                  </div>
                                  <div className={`w-full h-1.5 rounded-full overflow-hidden ${theme === 'dark' ? 'bg-slate-800' : 'bg-slate-100'}`}>
                                    <div
                                      className={`h-full rounded-full bg-gradient-to-r ${progressColor}`}
                                      style={{ width: `${progressPercentage}%` }}
                                    />
                                  </div>
                                </div>
                              </td>

                              {/* STATUS INDICATOR WITH DYNAMIC PULSATOR */}
                              <td className="py-4 px-5 text-center">
                                <button
                                  onClick={() => triggerToggleSubStatus(sub.id, sub.status)}
                                  className={`px-3 py-1.5 rounded-full text-[9px] font-bold uppercase transition-all tracking-wide inline-flex items-center gap-1.5 ${
                                    sub.status === 'active'
                                      ? 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20'
                                      : sub.status === 'trial'
                                      ? 'bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20'
                                      : 'bg-rose-500/10 text-rose-450 hover:bg-rose-500/20'
                                  }`}
                                  title={lang === 'ar' ? 'اضغط لتبديل حالة الترخيص' : 'Press to toggle status cycle'}
                                >
                                  <span className={`relative flex h-2 w-2`}>
                                    <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                                      sub.status === 'active' ? 'bg-emerald-400' : sub.status === 'trial' ? 'bg-cyan-400' : 'bg-rose-400'
                                    }`}></span>
                                    <span className={`relative inline-flex rounded-full h-2 w-2 ${
                                      sub.status === 'active' ? 'bg-emerald-500' : sub.status === 'trial' ? 'bg-cyan-500' : 'bg-rose-550'
                                    }`}></span>
                                  </span>
                                  <span>{sub.status === 'active' ? TRANSLATIONS[lang].statusActive : sub.status === 'trial' ? TRANSLATIONS[lang].statusTrial : TRANSLATIONS[lang].statusSuspended}</span>
                                </button>
                              </td>

                              {/* ROW ACTIONS (RESET METER + REVOKE PORTAL ACCESSIBILITY) */}
                              <td className="py-4 px-5 text-center">
                                <div className="inline-flex items-center gap-1.5">
                                  {/* Reset meter action */}
                                  <button
                                    onClick={() => triggerResetSubQuota(sub.id)}
                                    title={lang === 'ar' ? 'تصفير وعاء الاستهلاك الكلي للذكاء الاصطناعي' : 'Reset AI consumption limits'}
                                    className={`p-2 rounded-lg transition-all ${
                                      theme === 'dark'
                                        ? 'bg-slate-800 hover:bg-slate-750 text-indigo-400 hover:text-white'
                                        : 'bg-slate-100 hover:bg-slate-200 text-indigo-700'
                                    }`}
                                  >
                                    <RefreshCw className="w-3.5 h-3.5" />
                                  </button>

                                  {/* Revoke account permanently action */}
                                  <button
                                    onClick={() => triggerDeleteSubscription(sub.id)}
                                    title={lang === 'ar' ? 'سحب رخصة المؤسسة وحذف الحساب' : 'Revoke and delete system node'}
                                    className={`p-2 rounded-lg transition-all ${
                                      theme === 'dark'
                                        ? 'bg-rose-500/10 hover:bg-[#991b1b]/30 text-rose-450 hover:text-white'
                                        : 'bg-rose-50 hover:bg-rose-100 text-rose-600'
                                    }`}
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  );
                })()}
              </div>
            </div>

            {/* PRODUCT PLANS PRICING STRUCTURE MANAGE LISTING */}
            <div className={`p-6 sm:p-8 rounded-3xl border ${theme === 'dark' ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-sm'}`}>
              <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                <div>
                  <h3 className="text-xl font-black tracking-tight flex items-center gap-2.5">
                    <CreditCard className="w-5.5 h-5.5 text-indigo-400" />
                    <span>{TRANSLATIONS[lang].managePlans}</span>
                  </h3>
                  <p className={`text-xs mt-1 ${theme === 'dark' ? 'text-slate-450' : 'text-slate-500'}`}>
                    {lang === 'ar'
                      ? 'تعديل مواصفات باقات الترخيص، كوتا السحب الصحفي اليومية، حدود السقوف المالية، والمعالم الترويجية.'
                      : 'Setup SaaS pricing points, active limits, daily wire pool pull bounds, and promotional details.'}
                  </p>
                </div>

                <button
                  onClick={triggerCreatePlan}
                  className="px-4.5 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white flex items-center gap-1.5 transition-all outline-none shadow-md shadow-indigo-600/10"
                >
                  <Plus className="w-4 h-4" />
                  <span>{TRANSLATIONS[lang].newPlan}</span>
                </button>
              </div>

              {/* PLANS GRID */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {plans.map((p) => {
                  const isEditing = editingPlanId === p.id;
                  const plName = p.name[lang] || p.name.en;
                  const featuresList = p.features[lang] || p.features.en;

                  return (
                    <div
                      key={p.id}
                      className={`p-6 rounded-2xl border transition-all ${
                        theme === 'dark'
                          ? isEditing
                            ? 'bg-slate-950 border-indigo-550 shadow-lg shadow-indigo-950/20'
                            : 'bg-slate-950/40 border-slate-850 hover:border-slate-800'
                          : isEditing
                          ? 'bg-indigo-50/20 border-indigo-300'
                          : 'bg-white border-slate-200 shadow-sm hover:shadow-md'
                      }`}
                    >
                      {isEditing ? (
                        /* EDIT MODE SUB-FORM */
                        <div className="space-y-4">
                          <h4 className="text-xs font-bold uppercase text-indigo-400">{TRANSLATIONS[lang].editPlanTitle} ({p.id})</h4>
                          
                          <div>
                            <label className="text-[10px] uppercase font-bold text-slate-500">{TRANSLATIONS[lang].priceLabel}</label>
                            <input
                              type="number"
                              value={planForm.price ?? p.price}
                              onChange={(e) => setPlanForm((prev) => ({ ...prev, price: Number(e.target.value) }))}
                              className={`w-full text-xs rounded-lg px-2.5 py-2 ${theme === 'dark' ? 'bg-slate-950 text-white border-slate-800 border focus:border-indigo-500' : 'bg-slate-50 border border-slate-200 focus:border-indigo-400'}`}
                            />
                          </div>

                          <div>
                            <label className="text-[10px] uppercase font-bold text-slate-500">{TRANSLATIONS[lang].limitRewrites}</label>
                            <input
                              type="number"
                              value={planForm.maxRewrites ?? p.maxRewrites}
                              onChange={(e) => setPlanForm((prev) => ({ ...prev, maxRewrites: Number(e.target.value) }))}
                              className={`w-full text-xs rounded-lg px-2.5 py-2 ${theme === 'dark' ? 'bg-slate-950 text-white border-slate-800 border focus:border-indigo-500' : 'bg-slate-50 border border-slate-200 focus:border-indigo-400'}`}
                            />
                          </div>

                          <div className="flex gap-2.5">
                            <button
                              onClick={() => triggerSavePlan(p.id)}
                              className="w-full py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold transition-all hover:bg-indigo-500 shadow"
                            >
                              Save
                            </button>
                            <button
                              onClick={() => {
                                setEditingPlanId(null);
                                setPlanForm({});
                              }}
                              className={`w-full py-2 rounded-lg text-xs font-medium ${theme === 'dark' ? 'bg-slate-850 text-slate-400 hover:bg-slate-800' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'}`}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        /* PRESENTATION MODE */
                        <div>
                          <div className="flex items-center justify-between mb-4">
                            <h4 className={`font-black text-sm sm:text-base font-sans ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>{plName}</h4>
                            <span className="text-[10px] bg-indigo-505 bg-indigo-500/10 text-indigo-400 px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider">
                              {p.billing}
                            </span>
                          </div>

                          <div className="mb-4">
                            <span className="text-3xl sm:text-4xl font-black text-indigo-400">${p.price}</span>
                            <span className="text-xs text-slate-550 text-slate-500"> / month</span>
                          </div>

                          <div className="space-y-2 text-xs mb-5">
                            <div className={`flex justify-between border-b py-1.5 ${theme === 'dark' ? 'border-slate-850' : 'border-slate-100'}`}>
                              <span className="text-slate-500">{lang === 'ar' ? 'الحد الأقصى اليومي:' : 'Day Pull Caps:'}</span>
                              <strong className={`font-mono ${theme === 'dark' ? 'text-slate-300' : 'text-slate-700'}`}>{p.maxArticles}</strong>
                            </div>
                            <div className={`flex justify-between border-b py-1.5 ${theme === 'dark' ? 'border-slate-850' : 'border-slate-100'}`}>
                              <span className="text-slate-500">{lang === 'ar' ? 'حصص صياغة الـ AI:' : 'AI Rewriting Allowed:'}</span>
                              <strong className={`font-mono ${theme === 'dark' ? 'text-slate-300' : 'text-slate-700'}`}>{p.maxRewrites.toLocaleString()}</strong>
                            </div>
                          </div>

                          <ul className="space-y-1.5 mb-6 text-xs text-slate-400 min-h-[100px] pl-1">
                            {featuresList.map((feat, fIdx) => (
                              <li key={fIdx} className="flex items-start gap-1.5 text-slate-400 leading-snug">
                                <span className="inline-block w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 shrink-0" />
                                <span>{feat}</span>
                              </li>
                            ))}
                          </ul>

                          <button
                            onClick={() => {
                              setEditingPlanId(p.id);
                              setPlanForm(p);
                            }}
                            className={`w-full py-2.5 rounded-xl text-xs font-semibold border transition-all ${
                              theme === 'dark'
                                ? 'bg-slate-850 hover:bg-slate-800 border-slate-800 hover:text-white'
                                : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-800'
                            }`}
                          >
                            Edit Pricing Quotas
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        )}

      </main>

      {/* FOOTER */}
      <footer className={`border-t transition-all mt-16 ${theme === 'dark' ? 'bg-slate-950/80 border-slate-900 text-slate-400' : 'bg-white border-slate-205 text-slate-600'}`}>
        <div className="max-w-[1600px] mx-auto px-4 sm:px-8 py-10 flex flex-col md:flex-row gap-6 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-650 rounded-lg flex items-center justify-center text-white">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-sm block tracking-wide">{TRANSLATIONS[lang].title}</span>
              <p className="text-[11px] text-slate-500">All rights reserved © 2026. Made as a premium fully-redundant SaaS platform.</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 text-xs font-mono">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>Full-Stack Enterprise Security Verified</span>
            </span>
            <span className="opacity-30">|</span>
            <span>Local Time Check: 2026-05-24</span>
          </div>
        </div>
      </footer>

      {/* NEW SUBSCRIPTION MODAL */}
      <AnimatePresence>
        {showAddSubModal && (
          <div className="fixed inset-0 bg-black/85 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className={`w-full max-w-lg p-6 sm:p-8 rounded-3xl shadow-2xl transition-all border ${theme === 'dark' ? 'bg-slate-900 border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900'}`}
            >
              <div className="flex items-center justify-between mb-6 pb-2 border-b border-slate-800/40">
                <h3 className="text-base sm:text-lg font-extrabold flex items-center gap-2">
                  <span className="w-2.5 h-2.5 bg-indigo-500 rounded-full" />
                  <span>{TRANSLATIONS[lang].newSubscription}</span>
                </h3>
                <button
                  onClick={() => setShowAddSubModal(false)}
                  className="text-xs hover:text-indigo-400 font-bold font-mono tracking-wide"
                >
                  [ESC] CLOSE
                </button>
              </div>

              <form onSubmit={handleCreateSubscription} className="space-y-4">
                <div>
                  <label className="text-[11px] font-bold block mb-1 uppercase text-slate-500">
                    {TRANSLATIONS[lang].clientNamePlaceholder}
                  </label>
                  <input
                    type="text"
                    required
                    value={subForm.clientName}
                    onChange={(e) => setSubForm(prev => ({ ...prev, clientName: e.target.value }))}
                    placeholder="e.g. Al Jazeera West Portal"
                    className={`w-full text-xs rounded-xl px-3.5 py-3 outline-none transition-all ${theme === 'dark' ? 'bg-slate-950 text-white border border-slate-800' : 'bg-slate-100 border border-transparent'}`}
                  />
                </div>

                <div>
                  <label className="text-[11px] font-bold block mb-1 uppercase text-slate-500">
                    {TRANSLATIONS[lang].emailPlaceholder}
                  </label>
                  <input
                    type="email"
                    required
                    value={subForm.email}
                    onChange={(e) => setSubForm(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="e.g. editor@media-newsroom.org"
                    className={`w-full text-xs rounded-xl px-3.5 py-3 outline-none transition-all ${theme === 'dark' ? 'bg-slate-950 text-white border border-slate-800' : 'bg-slate-100 border border-transparent'}`}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-[11px] font-bold block mb-1 uppercase text-slate-500">
                      SaaS Active Plan
                    </label>
                    <select
                      value={subForm.planId}
                      onChange={(e) => setSubForm(prev => ({ ...prev, planId: e.target.value }))}
                      className={`w-full text-xs rounded-xl px-3 py-2.5 outline-none ${theme === 'dark' ? 'bg-slate-950 text-white border border-slate-850 border' : 'bg-slate-100 border border-slate-200'}`}
                    >
                      {plans.map(p => (
                        <option key={p.id} value={p.id}>
                          {p.name[lang] || p.name.en}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-bold block mb-1 uppercase text-slate-500">
                      {TRANSLATIONS[lang].durationDaysLabel}
                    </label>
                    <input
                      type="number"
                      value={subForm.durationDays}
                      onChange={(e) => setSubForm(prev => ({ ...prev, durationDays: Number(e.target.value) }))}
                      className={`w-full text-xs rounded-xl px-3 py-2.5 outline-none ${theme === 'dark' ? 'bg-slate-950 text-white border border-slate-850 border' : 'bg-slate-100 border border-transparent border-slate-200'}`}
                    />
                  </div>
                </div>

                <div className="pt-4 flex gap-3">
                  <button
                    type="submit"
                    className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition-all shadow-lg shadow-indigo-700/10"
                  >
                    {TRANSLATIONS[lang].btnSubmit}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddSubModal(false)}
                    className="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 font-bold text-xs transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
