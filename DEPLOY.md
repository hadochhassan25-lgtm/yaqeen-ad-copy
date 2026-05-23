# YAQEEN Ad Copy API — Deployment Guide

## Fastest Path: PythonAnywhere (5 minutes, free)

1. **Go to** https://www.pythonanywhere.com/ → **Sign up** (free, no credit card)

2. **Upload files** via Files tab:
   - `services/yaqeen_ad_api_deploy.py` (main app)
   - `requirements.txt`

3. **Open a Bash console** and run:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Web tab** → Add a new web app → Manual configuration → Python 3.11

5. **Set the WSGI handler**:
   - Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`
   - Replace with:
     ```python
     import sys
     path = '/home/yourusername'
     if path not in sys.path:
         sys.path.append(path)
     from yaqeen_ad_api_deploy import app as application
     ```
   - In the Web tab, set virtualenv to `/home/yourusername/venv`

6. **Reload** → Your API is live at `https://yourusername.pythonanywhere.com/`

7. **Verify**: Open `https://yourusername.pythonanywhere.com/health` in browser

## Second Option: Render (free, with GitHub)

1. Push `yaqeen_ad_api_deploy.py` + `requirements.txt` to a GitHub repo
2. Go to https://dashboard.render.com → New Web Service
3. Connect repo → Set start command: `gunicorn yaqeen_ad_api_deploy:app`
4. Free tier includes 512 MB RAM + 750 hours/month

## Third Option: Railway (free, no card needed)

1. Visit https://railway.app → New Project → Deploy from GitHub
2. Start command: `gunicorn yaqeen_ad_api_deploy:app`

## Static Demo (works offline, no server)

Open `services/yaqeen_client.html` in any browser.
Share it with clients. No server needed.

## Wallet (for payments)

- **Address**: `0xD0366D78055b8c637c44d769D1A1371106d13552`
- **Chain**: Base (Ethereum also accepted)
- **Price**: $0.50 USDC or 0.0005 ETH per request
