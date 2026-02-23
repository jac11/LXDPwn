# 📦 LXD Offline Bootstrap & Lab Automation Tool

## Overview

This project is a fully automated **offline LXD deployment and lab
environment setup tool**.

It performs:

-   Compatibility checks
-   snapd verification
-   LXD installation (offline mode)
-   LXD initialization
-   Alpine image import
-   Privileged container launch (lab use)
-   Optional host filesystem mount (lab environments only)

⚠️ **For educational and controlled lab environments only. Do NOT use on
production systems.**

------------------------------------------------------------------------

## Features

-   ✔ Detects if running as root
-   ✔ Detects real invoking user (even under sudo)
-   ✔ Checks snapd installation
-   ✔ Checks LXD snap installation
-   ✔ Checks LXD initialization state
-   ✔ Supports offline installation
-   ✔ Automated image import
-   ✔ Automated container launch
-   ✔ Optional host filesystem mount
-   ✔ Opens interactive shell inside container

------------------------------------------------------------------------

## Requirements

-   Linux system (Debian/Ubuntu recommended)
-   Root privileges
-   snapd installed (or provided offline package)
-   LXD snap packages (offline mode)

------------------------------------------------------------------------

## Execution Flow

Compatibility Check\
↓\
snapd Check\
↓\
LXD Check\
↓\
Download Phase (Offline Mode)\
↓\
Install Phase\
↓\
LXD Initialization\
↓\
Image Import\
↓\
Container Launch\
↓\
Optional Host Mount\
↓\
Shell Access

------------------------------------------------------------------------

## Running the Script

``` bash
sudo python3 autolxd.py
```

Root privileges are required.

------------------------------------------------------------------------

## Offline Mode

If internet access is not available, the script:

1.  Starts local HTTP server\
2.  Downloads required files\
3.  Stores them in:

```{=html}
<!-- -->
```
    /tmp/alpine

Files include:

-   Alpine image tarball
-   snapd package
-   core snap
-   lxd snap
-   assertion files

------------------------------------------------------------------------

## LXD Initialization

The tool runs:

    lxd init --auto

This configures:

-   Default storage backend
-   Default network bridge
-   Default profiles

------------------------------------------------------------------------

## Container Setup

After initialization:

-   Alpine image is imported
-   Privileged container is launched
-   Container name: `alpine-container`

Optional configuration:

    security.privileged=true

------------------------------------------------------------------------

## Host Filesystem Mount (Lab Use Only)

The tool can mount host root filesystem:

    source=/
    path=/mnt/root
    recursive=true

⚠️ This removes container isolation.\
Use only on systems you fully control.

------------------------------------------------------------------------

## Example Output

    [+] LXD initialized successfully.
    [+] Image imported.
    [+] Container started.
    [+] Host filesystem mounted at /mnt/root
    [+] Opening shell inside container...
    ~ # id
    uid=0(root) gid=0(root)

------------------------------------------------------------------------

## Cleanup

Remove container:

``` bash
sudo lxc stop alpine-container --force
sudo lxc delete alpine-container
```

Remove image:

``` bash
sudo lxc image delete alpine-local
```

------------------------------------------------------------------------

## Educational Topics Covered

-   Linux namespaces
-   Mount propagation
-   snap package management
-   LXD architecture
-   Container privilege levels
-   Root vs user group permissions

------------------------------------------------------------------------

## License

Personal lab automation project\
Intended for educational and research purposes only.
