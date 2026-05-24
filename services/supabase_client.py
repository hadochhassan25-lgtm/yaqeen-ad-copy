import os, requests, time

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://zbduwiftxyeyuyokefnq.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_publishable_Rf7qQ9OgP4VOSVs0WeHByQ_kYoNl7s9')
AUTH_URL = SUPABASE_URL.rstrip('/') + '/auth/v1'

HEADERS = {'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'}

def _auth_headers(token):
    return {**HEADERS, 'Authorization': f'Bearer {token}'}

def sign_up(email, password, user_metadata=None):
    body = {'email': email, 'password': password}
    if user_metadata:
        body['data'] = user_metadata
    r = requests.post(AUTH_URL + '/signup', json=body, headers=HEADERS)
    if r.status_code in (200, 201, 204):
        d = r.json() if r.text else {'success': True}
        return {'success': True, 'user': d.get('user', d), 'session': d.get('access_token', '')}
    return {'success': False, 'error': r.json().get('error_description', r.json().get('msg', 'Signup failed'))}

def sign_in(email, password):
    r = requests.post(AUTH_URL + '/token?grant_type=password', json={'email': email, 'password': password}, headers=HEADERS)
    if r.status_code == 200:
        d = r.json()
        meta = d.get('user', {}).get('user_metadata', {})
        return {'success': True, 'access_token': d['access_token'], 'refresh_token': d['refresh_token'],
                'user_id': d['user']['id'], 'email': d['user']['email'], 'user_metadata': meta}
    return {'success': False, 'error': r.json().get('error_description', r.json().get('msg', 'Login failed'))}

def get_user_metadata(access_token):
    """Fetch the current user's metadata from Supabase Auth."""
    r = requests.get(AUTH_URL + '/user', headers=_auth_headers(access_token))
    if r.status_code == 200:
        d = r.json()
        meta = d.get('user_metadata', {})
        return {'success': True, 'email': d.get('email', ''), 'user_metadata': meta}
    return {'success': False, 'error': 'Failed to fetch user', 'raw': r.text}

def update_user_metadata(access_token, metadata):
    """Update current user's metadata via PUT /auth/v1/user."""
    r = requests.put(AUTH_URL + '/user', json={'data': metadata}, headers=_auth_headers(access_token))
    return r.status_code == 200

def update_usage(access_token, field, increment=1):
    p = get_user_metadata(access_token)
    if not p['success']:
        return False
    meta = p['user_metadata']
    current = meta.get(field, 0)
    meta[field] = current + increment
    return update_user_metadata(access_token, meta)

def get_limits(access_token):
    p = get_user_metadata(access_token)
    if not p['success']:
        return {'rewrites_used': 0, 'rewrites_limit': 5, 'adcopies_used': 0, 'adcopies_limit': 2,
                'subscription_tier': 'free', 'is_admin': False, 'email': ''}
    meta = p['user_metadata']
    is_admin = meta.get('is_admin', False)
    email = p.get('email', '')
    if is_admin:
        return {'rewrites_used': 0, 'rewrites_limit': 999999, 'adcopies_used': 0, 'adcopies_limit': 999999,
                'subscription_tier': 'admin', 'is_admin': True, 'email': email}
    return {
        'rewrites_used': meta.get('rewrites_used', 0),
        'rewrites_limit': meta.get('rewrites_limit', 5),
        'adcopies_used': meta.get('adcopies_used', 0),
        'adcopies_limit': meta.get('adcopies_limit', 2),
        'subscription_tier': meta.get('subscription_tier', 'free'),
        'is_admin': False,
        'email': email
    }

def set_admin(access_token):
    meta = get_user_metadata(access_token)
    if not meta['success']:
        return False
    um = meta['user_metadata']
    um['is_admin'] = True
    return update_user_metadata(access_token, um)