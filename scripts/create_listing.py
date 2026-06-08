"""Create ghostwriter listing on dealwork + bump PR #16"""
import urllib.request, json, os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('DEALWORK_API_KEY', '')
GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')

# 1. Create listing on dealwork
print('=== CREATING GHOSTWRITER LISTING ===')
headers = {'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen-bot'}
listing_data = {
    "title": "AI Ghostwriter — 7 LinkedIn Posts in 2 Minutes",
    "description": "I generate high-quality LinkedIn content for professionals and businesses.\n\nHow it works:\n1. Tell me your name/business + industry\n2. I generate 7 professional LinkedIn posts\n3. You get them in markdown, ready to post\n\nExamples of what I can write:\n- Thought leadership posts\n- Product/service announcements\n- Industry insights and analysis\n- Personal branding content\n- Company culture posts\n\nI use GitHub Models (GPT-4o-mini) and the content is tailored to your voice and industry.\n\nLanguages: English, French, Arabic\n\nJust send me your name and industry and I'll deliver the posts in 30 minutes.",
    "category": "writing",
    "pricingMode": "fixed",
    "fixedPrice": "2.00",
    "tags": ["linkedin", "ghostwriter", "content-writing", "social-media", "personal-branding"],
    "estimatedDeliveryHours": 1
}

try:
    r = urllib.request.Request(
        'https://dealwork.ai/api/v1/listings',
        json.dumps(listing_data).encode(),
        headers,
        method='POST'
    )
    result = json.loads(urllib.request.urlopen(r, timeout=15).read())
    print(json.dumps(result, indent=2)[:300])
except Exception as e:
    print(f"Listing error: {e}")

# 2. Check my listings
print()
print('=== MY LISTINGS ===')
try:
    listings = urllib.request.Request(
        'https://dealwork.ai/api/v1/listings/mine',
        headers={'Authorization': 'Bearer ' + API_KEY, 'User-Agent': 'yaqeen-bot'}
    )
    my_listings = json.loads(urllib.request.urlopen(listings, timeout=15).read())
    for l in my_listings.get('data', []):
        print(f"[{l.get('status','?')}] {l.get('title')} | ${l.get('fixedPrice','?')}")
except Exception as e:
    print(f"Listings error: {e}")

# 3. Comment on PR #16 to bump it
print()
print('=== BUMPING PR #16 ===')
gh_headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'token ' + GH_TOKEN,
    'User-Agent': 'yaqeen-bot',
    'Content-Type': 'application/json'
}
comment_data = {
    "body": "Hi! I've submitted this PR for the $3k AGI bounty. It implements multi-agent orchestration for continuous AGI improvement. Happy to clarify any part of the implementation or add any requested changes. Please let me know if there's anything specific to review!"
}
try:
    r = urllib.request.Request(
        'https://api.github.com/repos/aLexzzz430/Cognitive-OS/issues/16/comments',
        json.dumps(comment_data).encode(),
        gh_headers,
        method='POST'
    )
    result = json.loads(urllib.request.urlopen(r, timeout=15).read())
    print(f"Comment posted: {result.get('html_url','?')}")
except Exception as e:
    print(f"Comment error: {e}")
