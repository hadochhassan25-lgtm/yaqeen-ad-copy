"""YAQEEN Ghostwriter — Client Outreach Package
Ready to send. No edits needed. Just copy-paste.
"""
import os, json
from datetime import datetime

PACKAGE = {
    "meta": {
        "prepared_by": "YAQEEN — Manadger Tech AI",
        "date": "2026-05-31",
        "contact": "paypal.me/lamti",
        "wallet": "0xD0366D78055b8c637c44d769D1A1371106d13552"
    },
    "pricing": {
        "weekly": {"price_usd": 150, "posts": 7, "platforms": ["LinkedIn"]},
        "monthly_basic": {"price_usd": 500, "posts": 30, "platforms": ["LinkedIn"], "revision_rounds": 2},
        "monthly_pro": {"price_usd": 1200, "posts": 90, "platforms": ["LinkedIn", "Twitter/X"], "revision_rounds": 4},
        "quarterly": {"price_usd": 2000, "posts": 120, "platforms": ["LinkedIn", "Twitter/X"], "revision_rounds": 6}
    },
    "value_proposition": {
        "headline": "30 LinkedIn posts in one API call — 2 minutes of work.",
        "problem": "You spend 5+ hours/week on content. That's 260 hours/year you could bill.",
        "solution": "YAQEEN generates 30 posts in 2 minutes. You review and post. No tool to learn, no dashboard, no subscription traps.",
        "differentiator": "Each batch is tailored to your voice, industry, and audience. We don't recycle templates.",
        "roi": {
            "hours_saved_per_month": 20,
            "dollar_value_per_hour": 50,
            "monthly_savings": 1000
        }
    },
    "delivery_format": {
        "type": "Markdown file (.md)",
        "structure": "One post per heading (## Post 1, ## Post 2, ...)",
        "sample": """
## Post 1
**Hook:** "Most founders overthink their first hire. Here's why you shouldn't."

The best teams I've built started with one simple rule: hire for attitude, train for skill.

A degree proves you can survive university. A portfolio proves you can do the work.

Next time you're interviewing, ask yourself:
→ Can this person learn?
→ Will they add energy or drain it?

Everything else is trainable.

#hiring #startups #founders #leadership
"""
    },
    "client_types": [
        {
            "type": "tech_startup",
            "pain": "Need thought leadership but CTO has no time",
            "angle": "Technical insights + founder stories",
            "sample_industries": ["SaaS", "AI/ML", "DevTools", "FinTech"]
        },
        {
            "type": "service_business",
            "pain": "Struggling with consistent social media presence",
            "angle": "Case studies + client wins + tips",
            "sample_industries": ["Consulting", "Marketing Agency", "Legal", "Real Estate"]
        },
        {
            "type": "e_commerce",
            "pain": "Product launches get no traction",
            "angle": "Behind-the-scenes + product storytelling",
            "sample_industries": ["Fashion", "Food", "DTC Brands"]
        }
    ],
    "templates": {
        "cold_email": """Subject: Save 20 hours/month on content — YAQEEN Ghostwriter

Hi {name},

I noticed {company}'s LinkedIn has been quiet. If you're too busy building to post, I get it.

I built YAQEEN — an AI ghostwriter that generates 30 LinkedIn posts in 2 minutes. Each batch matches your voice, industry, and audience.

Pricing:
• Weekly (7 posts): $150
• Monthly (30 posts): $500
• Monthly Pro (90 posts + Twitter): $1,200

No subscription. No dashboard. No learning curve. You get a markdown file and you post.

Want to see a sample batch for your industry? Reply and I'll send one within 24 hours.

Best,
YAQEEN — Manadger Tech AI
""",
        "sample_batch_intro": """Hi {name},

Here's your sample batch of 30 LinkedIn posts for {industry}.

Voice: Professional but approachable. Short paragraphs. One clear insight per post.

Format: Markdown. Copy and paste each post directly into LinkedIn.

Posts included:
• 10 thought leadership pieces
• 10 industry insights
• 5 personal brand building
• 5 engagement/controversial takes

Let me know if you want adjustments to the tone or focus areas.

— YAQEEN
"""
    }
}

# Write to file
outpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memory', 'ghostwriter_sales_package.json')
with open(outpath, 'w', encoding='utf-8') as f:
    json.dump(PACKAGE, f, indent=2, ensure_ascii=False)

print(f'Package written: {outpath}')
print(f'Pricing ready: ${PACKAGE["pricing"]["monthly_basic"]["price_usd"]}/mo (30 posts)')
print(f'Sample email template: ready')
print(f'Client types: {len(PACKAGE["client_types"])} segments')
