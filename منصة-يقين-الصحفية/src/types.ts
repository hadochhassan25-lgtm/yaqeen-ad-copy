export interface Article {
  id: string;
  originalTitle: string;
  originalContent: string;
  title: string;
  content: string[]; // split into paragraphs
  source: string;
  url: string;
  fetchedAt: string; // ISO date
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

export interface Plan {
  id: string;
  name: Record<string, string>; // language code -> text
  price: number;
  billing: string;
  features: Record<string, string[]>; // language code -> arrays of strings
  maxRewrites: number;
  maxArticles: number;
  active: boolean;
}

export interface Subscription {
  id: string;
  email: string;
  clientName: string;
  planId: string;
  status: 'active' | 'suspended' | 'trial';
  startDate: string;
  expiresDate: string;
  rewritesUsed: number;
}

export interface YaqeenStats {
  totalArticles: number;
  totalRewrites: number;
  activeSubscriptions: number;
  prunedArticlesCount: number;
  lastSyncTime: string;
}
