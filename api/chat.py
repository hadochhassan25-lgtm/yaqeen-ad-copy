import os, json, urllib.request, re

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

def handler(request):
    try:
        body = json.loads(request.body)
        msg = body.get("message", "")
    except:
        return {"statusCode": 400, "body": json.dumps({"reply": "⚠️ خطأ في الطلب"})}

    messages = [
        {"role": "system", "content": "أنت يقين، أول ذكاء اصطناعي مغربي بالكامل. صممتك شركة منادجر تك للبرمجة وحلول الويب. أجب بنفس لغة المستخدم."},
        {"role": "user", "content": msg}
    ]

    try:
        d = json.dumps({"model": "llama-3.3-70b-versatile", "messages": messages}).encode()
        req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", d,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_KEY}", "User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        r = json.loads(resp.read())
        reply = r["choices"][0]["message"]["content"]
        reply = re.sub(r'[\u0400-\u04FF\u0E00-\u0E7F]', '', reply).strip()
    except Exception as e:
        reply = f"⚠️ خطأ: {str(e)[:50]}"

    return {"statusCode": 200, "body": json.dumps({"reply": reply})}
