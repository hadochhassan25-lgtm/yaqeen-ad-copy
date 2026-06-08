"""Generate Ghostwriter sample batch for Iliass Lamti / Manadger Tech"""
import urllib.request, json, os, sys

GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def ask_llm(system, user):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + GH_TOKEN
    }
    body = json.dumps({
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user}
        ],
        'max_tokens': 2000
    }).encode()
    req = urllib.request.Request(
        'https://models.inference.ai.azure.com/chat/completions',
        data=body, headers=headers, method='POST'
    )
    r = urllib.request.urlopen(req, timeout=30)
    return json.loads(r.read())['choices'][0]['message']['content']

# Generate 7 LinkedIn posts for Iliass Lamti as CEO of Manadger Tech
system = """You are YAQEEN, the AI executive assistant of Manadger Tech S.A.R.L.
Generate LinkedIn posts for the CEO (Iliass Lamti) about:
- Tech entrepreneurship in Morocco
- Building digital platforms
- AI and automation in business
- Managing tech teams
- The Moroccan startup ecosystem

Tone: Bold, confident, visionary. Short paragraphs. One insight per post.
Language: Mix of Arabic (darija/fus-ha) and English terms where natural.
Format: Return each post separated by '---POST---' marker."""

user = """Generate 7 LinkedIn posts for Iliass Lamti (CEO at Manadger Tech):

Post 1-2: About YAQEEN (the AI agent running the company operations)
Post 3-4: About building tech platforms in Morocco 
Post 5-6: About AI automation for business growth
Post 7: A personal/hot take on entrepreneurship in 2026

Make them bold, shareable, and position Iliass as a visionary leader."""

print('Generating ghostwriter sample batch for Iliass Lamti...')
result = ask_llm(system, user)
posts = result.split('---POST---')

base = os.path.dirname(os.path.dirname(__file__))
outpath = os.path.join(base, 'memory', 'ghostwriter_sample_batch.md')

with open(outpath, 'w', encoding='utf-8') as f:
    f.write('# YAQEEN Ghostwriter — Sample Batch\n')
    f.write(f'# Client: Iliass Lamti / Manadger Tech\n')
    f.write(f'# Generated: 2026-05-31\n')
    f.write(f'# Tone: Bold / Visionary / Tech\n\n')
    f.write('---\n\n')
    for i, post in enumerate(posts, 1):
        post = post.strip()
        if post:
            f.write(f'## Post {i}\n\n')
            f.write(post + '\n\n---\n\n')

print(f'Done! Generated {len(posts)} posts')
print(f'Saved to: {outpath}')
with open(outpath, 'r', encoding='utf-8') as f:
    content = f.read()
    print(f'File size: {len(content)} chars')
    # Show first post preview
    sections = content.split('## Post')
    if len(sections) > 1:
        print(f'\nPreview of Post 1:\n{sections[1][:200]}...')
