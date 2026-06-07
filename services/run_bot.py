#!/usr/bin/env python3
"""Production runner for YAQEEN bot - wraps bot with web server for cloud hosting"""
import os, sys, json, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

PORT = int(os.environ.get("PORT", 8080))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "bot": "YAQEEN AI"}).encode())
    def log_message(self, *a): pass

def run_http():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()

if __name__ == "__main__":
    # Import and start bot in thread
    from services.telegram_bot import bot
    t = threading.Thread(target=lambda: bot.polling(non_stop=True, interval=1, timeout=30), daemon=True)
    t.start()
    print(f"YAQEEN Bot v3 — Online on port {PORT}")
    run_http()
