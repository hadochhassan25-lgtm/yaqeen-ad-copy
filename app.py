"""
YAQEEN Vercel Entry Point — wraps services/yaqeen_ad_api_deploy for serverless
"""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'services'))
from yaqeen_ad_api_deploy import app
