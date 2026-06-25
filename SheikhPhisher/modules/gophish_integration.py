#!/usr/bin/env python3
# modules/gophish_integration.py - SheikhPhisher Gophish API Client
# Manage campaigns through Gophish framework

import os, json, logging
log = logging.getLogger(__name__)

class GophishManager:
    """Gophish REST API integration for campaign management"""
    
    def __init__(self, config):
        self.config = config
        self.api_key = config.get('api_key', '')
        self.host = config.get('host', 'https://127.0.0.1:3333')
        self.gophish = None
        
        if self.api_key:
            try:
                from gophish import Gophish
                self.gophish = Gophish(self.api_key, self.host, verify=not config.get('ignore_ssl', True))
                log.info(f"[GOPHISH] Connected to {self.host}")
            except ImportError:
                log.warning("[GOPHISH] gophish library not installed. Run: pip install gophish")
            except Exception as e:
                log.error(f"[GOPHISH] Connection failed: {e}")
    
    def run_campaign(self, config_path):
        """Run a full campaign from JSON config"""
        with open(config_path) as f:
            cfg = json.load(f)
        
        if not self.gophish:
            log.error("[GOPHISH] Not connected. Provide --api-key")
            return
        
        # Create groups
        groups = []
        for group_cfg in cfg.get('groups', []):
            targets = []
            for user in group_cfg.get('targets', []):
                targets.append({'email': user['email'], 'first_name': user.get('first_name', ''), 'last_name': user.get('last_name', '')})
            group = self.gophish.groups.new(group_cfg['name'], targets)
            groups.append(group.id)
            log.info(f"[GOPHISH] Created group: {group.name} (ID: {group.id})")
        
        # Create template
        template_cfg = cfg.get('template', {})
        template = self.gophish.templates.new(
            name=template_cfg['name'],
            subject=template_cfg['subject'],
            html=template_cfg['html'],
            attach=template_cfg.get('attachments', [])
        )
        log.info(f"[GOPHISH] Created template: {template.name} (ID: {template.id})")
        
        # Create landing page
        page_cfg = cfg.get('landing_page', {})
        page = self.gophish.pages.new(
            name=page_cfg['name'],
            html=page_cfg['html'],
            capture_credentials=True,
            capture_passwords=True
        )
        log.info(f"[GOPHISH] Created landing page: {page.name} (ID: {page.id})")
        
        # Create SMTP profile
        smtp_cfg = cfg.get('smtp', {})
        smtp = self.gophish.smtp.new(
            name=smtp_cfg['name'],
            host=smtp_cfg['host'],
            username=smtp_cfg.get('username', ''),
            password=smtp_cfg.get('password', ''),
            from_address=smtp_cfg['from_address']
        )
        log.info(f"[GOPHISH] Created SMTP profile: {smtp.name} (ID: {smtp.id})")
        
        # Create and launch campaign
        campaign = self.gophish.campaigns.new(
            name=cfg['name'],
            template=template,
            page=page,
            smtp=smtp,
            groups=[{'id': g} for g in groups],
            url=cfg['phishing_url'],
            launch_date=cfg.get('launch_date', 'now')
        )
        log.info(f"[GOPHISH] Campaign launched: {campaign.name} (ID: {campaign.id})")
        log.info(f"[GOPHISH] Results URL: {self.host}/campaigns/{campaign.id}")
        
        return campaign
    
    def cmd_create_user(self):
        """Gophish CLI: create user"""
        pass
    
    def cmd_create_group(self):
        """Gophish CLI: create group"""
        pass
    
    def cmd_create_template(self):
        """Gophish CLI: create template"""
        pass
    
    def cmd_create_campaign(self):
        """Gophish CLI: create campaign"""
        pass
    
    def cmd_launch(self):
        """Gophish CLI: launch campaign"""
        pass
    
    def cmd_status(self):
        """Gophish CLI: check campaign status"""
        pass
    
    def cmd_results(self):
        """Gophish CLI: get campaign results"""
        pass