import json
import os
import random
import subprocess
import requests

def install_warp():
    """Automatically install WARP CLI if missing"""
    try:
        subprocess.run(["warp-cli", "--version"], check=True)
        print("✅ WARP CLI is already installed.")
    except subprocess.CalledProcessError:
        print("🚀 Installing WARP CLI...")
        os.system("""
            sudo apt-get update
            sudo apt-get install -y cloudflare-warp || \
            (curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo tee /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg > /dev/null && \
            echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ focal main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list && \
            sudo apt-get update && \
            sudo apt-get install -y cloudflare-warp)
            sudo systemctl enable warp-svc
            sudo systemctl start warp-svc
        """)

def generate_private_key():
    """Generate a WireGuard private key"""
    try:
        return subprocess.check_output(["wg", "genkey"]).decode().strip()
    except Exception as e:
        print(f"❌ Error generating private key: {e}")
        return "[private_key]"

def generate_random_port():
    """Generate a random port"""
    return random.randint(1024, 65535)

def get_warp_ipv6():
    """Automatically retrieve a new IPv6 from WARP-in-WARP"""
    try:
        subprocess.run(["warp-cli", "disconnect"], check=True)
        subprocess.run(["warp-cli", "connect"], check=True)
        ipv6 = requests.get("https://api64.ipify.org").text.strip()
        print(f"✅ First WARP IPv6: {ipv6}")

        subprocess.run(["warp-cli", "disconnect"], check=True)
        subprocess.run(["warp-cli", "connect"], check=True)
        warp_in_warp_ipv6 = requests.get("https://api64.ipify.org").text.strip()
        print(f"✅ WARP-in-WARP IPv6: {warp_in_warp_ipv6}")

        return warp_in_warp_ipv6
    except requests.RequestException as e:
        print(f"❌ Error getting IPv6: {e}")
        return "2606:4700:d0::1"

def load_config():
    """Load and validate hiddify-config.json"""
    if not os.path.exists('hiddify-config.json') or os.stat('hiddify-config.json').st_size == 0:
        print("⚠️ Creating default configuration...")
        return {"route": {}, "outbounds": []}
    try:
        with open('hiddify-config.json', 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("❌ Invalid JSON! Resetting...")
        return {"route": {}, "outbounds": []}

def update_wireguard_config(config, ipv6, port):
    """Update WireGuard configuration dynamically"""
    wireguard_default = {
        "type": "wireguard",
        "local_address": ["172.16.0.2/32", ipv6],
        "private_key": generate_private_key(),
        "server": ipv6,
        "server_port": port,
        "peer_public_key": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=",
        "reserved": ["reserved"],
        "mtu": 1280,
        "fake_packets": "5-10"
    }
    
    config['outbounds'] = [
        {"tag": "IP-> Your IP address", **wireguard_default},
        {"tag": "IP-> Main", "detour": "IP-> Your IP address", **wireguard_default}
    ]

    return config

def save_config(config):
    """Save updated configuration"""
    with open('hiddify-config.json', 'w') as file:
        json.dump(config, file, indent=2)

def main():
    install_warp()
    ipv6 = get_warp_ipv6()
    port = generate_random_port()
    config = load_config()
    updated_config = update_wireguard_config(config, ipv6, port)
    save_config(updated_config)
    print(f"✅ WireGuard updated: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()
