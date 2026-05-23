import os, requests, time

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://zbduwiftxyeyuyokefnq.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_publishable_Rf7qQ9OgP4VOSVs0WeHByQ_kYoNl7s9')
AUTH_URL = SUPABASE_URL.rstrip('/') + '/auth/v1'
API_URL = SUPABASE_URL.rstrip('/') + '/rest/v1'

HEADERS = {'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'}

def sign_up(email, password):
    r = requests.post(AUTH_URL + '/signup', json={'email': email, 'password': password}, headers=HEADERS)
    if r.status_code in (200, 201, 204):
        d = r.json() if r.text else {'success': True}
        return {'success': True, 'user': d.get('user', d), 'session': d.get('access_token', '')}
    return {'success': False, 'error': r.json().get('error_description', r.json().get('msg', 'Signup failed'))}

def sign_in(email, password):
    r = requests.post(AUTH_URL + '/token?grant_type=password', json={'email': email, 'password': password}, headers=HEADERS)
    if r.status_code == 200:
        d = r.json()
        return {'success': True, 'access_token': d['access_token'], 'refresh_token': d['refresh_token'], 'user_id': d['user']['id'], 'email': d['user']['email']}
    return {'success': False, 'error': r.json().get('error_description', r.json().get('msg', 'Login failed'))}

def get_profile(access_token):
    headers = {**HEADERS, 'Authorization': f'Bearer {access_token}'}
    r = requests.get(API_URL + '/profiles?select=*', headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data:
            return {'success': True, 'profile': data[0]}
    return {'success': False, 'error': 'Profile not found', 'raw': r.text}

def update_usage(access_token, field, increment=1):
    headers = {**HEADERS, 'Authorization': f'Bearer {access_token}', 'Prefer': 'return=minimal'}
    p = get_profile(access_token)
    if not p['success']:
        return False
    current = p['profile'].get(field, 0)
    r = requests.patch(API_URL + '/profiles', json={field: current + increment}, headers=headers)
    return r.status_code in (200, 204)

def get_limits(access_token):
    p = get_profile(access_token)
    if not p['success']:
        return {'rewrites_used': 0, 'rewrites_limit': 5, 'adcopies_used': 0, 'adcopies_limit': 2, 'subscription_tier': 'free'}
    pr = p['profile']
    return {
        'rewrites_used': pr.get('rewrites_used', 0),
        'rewrites_limit': pr.get('rewrites_limit', 5),
        'adcopies_used': pr.get('adcopies_used', 0),
        'adcopies_limit': pr.get('adcopies_limit', 2),
        'subscription_tier': pr.get('subscription_tier', 'free')
    }