import json
import os
import random
import subprocess
import requests

def generate_private_key():
    """Generate a new private key for WireGuard"""
    try:
        key = subprocess.check_output(["wg", "genkey"]).decode("utf-8").strip()
        return key
    except Exception as e:
        print(f"❌ Error generating private key: {e}")
        return "[private_key]"

def generate_random_port():
    """Generate a random port within the allowed range"""
    return random.randint(1024, 65535)

def get_best_ipv6():
    """Retrieve a new IPv6 address using WARP-in-WARP"""
    try:
        subprocess.run(["warp-cli", "disconnect"], check=True)  # قطع اتصال اولیه
        subprocess.run(["warp-cli", "connect"], check=True)  # اتصال دوباره
        ipv6 = requests.get("https://api64.ipify.org").text.strip()
        print(f"✅ First WARP IPv6: {ipv6}")
        
        subprocess.run(["warp-cli", "disconnect"], check=True)  # قطع مجدد
        subprocess.run(["warp-cli", "connect"], check=True)  # اتصال دوم برای WARP-in-WARP
        warp_in_warp_ipv6 = requests.get("https://api64.ipify.org").text.strip()
        print(f"✅ WARP-in-WARP IPv6: {warp_in_warp_ipv6}")
        
        return warp_in_warp_ipv6
    except requests.RequestException as e:
        print(f"❌ Error retrieving IPv6: {e}")
        return "2606:4700:d0::1"

def load_config():
    """Load the configuration file and validate its contents"""
    if not os.path.exists('hiddify-config.json') or os.stat('hiddify-config.json').st_size == 0:
        print("⚠️ hiddify-config.json not found or is empty. Creating a default configuration...")
        return {"route": {}, "outbounds": []}
    try:
        with open('hiddify-config.json', 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("❌ Error: hiddify-config.json is invalid. Resetting...")
        return {"route": {}, "outbounds": []}

def update_wireguard_config(config, ipv6, port):
    """Update or add WireGuard settings with dynamic server and server_port"""
    
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
        {
            "tag": "IP-> Your IP address",
            **wireguard_default
        },
        {
            "tag": "IP-> Main",
            "detour": "IP-> Your IP address",
            **wireguard_default
        }
    ]

    return config

def save_config(config):
    """Save the updated configuration file"""
    with open('hiddify-config.json', 'w') as file:
        json.dump(config, file, indent=2)

def main():
    ipv6 = get_best_ipv6()
    port = generate_random_port()
    config = load_config()
    updated_config = update_wireguard_config(config, ipv6, port)
    save_config(updated_config)
    print(f"✅ WireGuard settings updated: IPv6 -> {ipv6}, Port -> {port}, Private key replaced.")

if __name__ == "__main__":
    main()
