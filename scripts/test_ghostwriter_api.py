import requests, json
r = requests.post("http://localhost:5000/api/ghostwriter", json={"client": "Iliass Lamti", "industry": "tech"}, timeout=180)
data = r.json()
print("Success:", data.get("success"))
if data.get("success"):
    posts = data["data"]["posts"]
    for p in posts[:3]:
        print(f"  Day {p['day']}: {p['body'][:80]}...")
    print(f"  ... and {len(posts)-3} more")
    print(f"Price: ${data['data']['payment']['amount_usdc']}")
else:
    print("Error:", data)
