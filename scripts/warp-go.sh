#!/bin/bash

set -e  # Stop script on error

# Install dependencies
sudo apt update
sudo apt install -y wireguard-tools curl jq fping

# Download and install WARP-GO
INSTALL_SCRIPT="install-warp.sh"
WARP_REPO="https://raw.githubusercontent.com/Ptechgithub/warp/main/endip/install.sh"

if [[ ! -f "$INSTALL_SCRIPT" ]]; then
  echo "⚠️ WARP install script not found! Downloading..."
  wget -O "$INSTALL_SCRIPT" "$WARP_REPO"
fi

chmod +x "$INSTALL_SCRIPT"
sudo ./"$INSTALL_SCRIPT"

# Check if WARP-CLI is installed
if ! command -v warp-cli &> /dev/null; then
  echo "❌ warp-cli installation failed!"
  exit 1
fi

# Setup WARP in WARP mode
warp-cli register || echo "⚠️ Already registered"
warp-cli set-mode warp+doh
warp-cli connect

warp-cli register || echo "⚠️ Already registered"
warp-cli set-mode warp+doh
warp-cli connect

echo "✅ WARP in WARP is successfully configured!"