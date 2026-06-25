#!/usr/bin/env python3
# modules/report.py - SheikhPhisher Report Generator

import os, json, logging
from datetime import datetime

log = logging.getLogger(__name__)

class ReportGenerator:
    """Generate assessment reports from capture data"""
    
    def generate(self, input_file, fmt='html'):
        """Generate report in specified format"""
        captures = []
        
        if os.path.isdir(input_file):
            for fname in os.listdir(input_file):
                if fname.endswith('.json') and fname != 'validated_creds.jsonl':
                    with open(os.path.join(input_file, fname)) as f:
                        captures.append(json.load(f))
        else:
            with open(input_file) as f:
                for line in f:
                    captures.append(json.loads(line))
        
        if fmt == 'html':
            return self._generate_html(captures)
        elif fmt == 'json':
            return self._generate_json(captures)
        else:
            log.warning(f"[REPORT] Format {fmt} not yet implemented")
            return None
    
    def _generate_html(self, captures):
        """Generate HTML assessment report"""
        total = len(captures)
        unique_ips = len(set(c.get('ip', '') for c in captures if c.get('ip')))
        templates = {}
        for c in captures:
            t = c.get('template', 'unknown')
            templates[t] = templates.get(t, 0) + 1
        
        rows = ''
        for i, c in enumerate(captures, 1):
            creds = c.get('credentials', {})
            cred_str = '<br>'.join(f'<b>{k}:</b> {v}' for k, v in creds.items())
            cookies = c.get('cookies', {})
            cookie_str = '<br>'.join(f'{k}={v}' for k, v in cookies.items()) if cookies else 'None'
            rows += f'''
            <tr>
                <td>{i}</td>
                <td>{c.get('timestamp', '')}</td>
                <td>{c.get('template', '')}</td>
                <td>{c.get('ip', '')}</td>
                <td>{cred_str}</td>
                <td><pre style="font-size:11px;">{cookie_str}</pre></td>
            </tr>'''
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>SheikhPhisher Assessment Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; background: #f5f5f5; }}
h1 {{ color: #1a1a1a; }}
.report {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
.stats {{ display: flex; gap: 20px; margin: 20px 0; }}
.stat {{ background: #f0f2f5; padding: 20px; border-radius: 8px; flex: 1; text-align: center; }}
.stat h2 {{ margin: 0; font-size: 32px; color: #0066ff; }}
.stat p {{ margin: 5px 0 0; color: #666; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
th {{ background: #f0f2f5; font-weight: 600; }}
tr:hover {{ background: #f9f9f9; }}
pre {{ background: #f5f5f5; padding: 8px; border-radius: 4px; overflow-x: auto; }}
</style></head>
<body>
<div class="report">
    <h1>🔍 SheikhPhisher Phishing Assessment Report</h1>
    <p>Generated: {datetime.utcnow().isoformat()}</p>
    <p>Assessment Tool: SheikhPhisher v1.0 by Sheikh-CoedexTech</p>
    
    <div class="stats">
        <div class="stat"><h2>{total}</h2><p>Total Captures</p></div>
        <div class="stat"><h2>{unique_ips}</h2><p>Unique IPs</p></div>
        <div class="stat"><h2>{len(templates)}</h2><p>Template Types</p></div>
    </div>
    
    <h2>Captured Data</h2>
    <table>
        <tr><th>#</th><th>Timestamp</th><th>Template</th><th>IP</th><th>Credentials</th><th>Session Cookies</th></tr>
        {rows}
    </table>
    
    <div class="footer" style="margin-top:30px; padding-top:20px; border-top:1px solid #ddd; color:#888; font-size:12px;">
        <p>Authorized Penetration Test | Client: Confidential</p>
        <p>Tool: <b>SheikhPhisher</b> by Sheikh-CoedexTech</p>
    </div>
</div>
</body></html>'''
        
        output_path = f'./reports/sheikhphisher_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.html'
        os.makedirs('./reports', exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)
        log.info(f"[REPORT] HTML report saved: {output_path}")
        return output_path
    
    def _generate_json(self, captures):
        """Generate JSON report"""
        output_path = f'./reports/sheikhphisher_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
        os.makedirs('./reports', exist_ok=True)
        
        report = {
            'tool': 'SheikhPhisher v1.0',
            'author': 'Sheikh-CoedexTech',
            'generated': datetime.utcnow().isoformat(),
            'total_captures': len(captures),
            'captures': captures
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        log.info(f"[REPORT] JSON report saved: {output_path}")
        return output_path