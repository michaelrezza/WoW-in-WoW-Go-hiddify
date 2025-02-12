import json
import os
import re
import subprocess

CONFIG_FILE = 'hiddify-config.json'
IPV6_SCAN_OUTPUT = 'ipv6_scan.txt'

def generate_private_key():
    """Generate a new WireGuard private key"""
    try:
        return subprocess.check_output(["wg", "genkey"]).decode("utf-8").strip()
    except Exception as e:
        print(f"❌ Error generating private key: {e}")
        return "[private_key]"

def extract_ipv6_port():
    """Extract IPv6 and port from the scanner output file"""
    if not os.path.exists(IPV6_SCAN_OUTPUT):
        print(f"❌ {IPV6_SCAN_OUTPUT} not found.")
        return None, None

    with open(IPV6_SCAN_OUTPUT, 'r') as file:
        for line in file:
            match = re.search(r"\[([a-fA-F0-9:]+)\]:(\d+)", line)
            if match:
                return match.group(1), int(match.group(2))
    
    print("❌ No valid IPv6:port found.")
    return None, None

def load_config():
    """Load hiddify-config.json"""
    if not os.path.exists(CONFIG_FILE) or os.stat(CONFIG_FILE).st_size == 0:
        print("⚠️ Config file missing or empty. Creating default config...")
        return {"route": {}, "outbounds": []}

    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in config. Resetting...")
        return {"route": {}, "outbounds": []}

def update_wireguard_config(config, ipv6, port):
    """Update WireGuard settings dynamically"""
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

    updated = False
    for outbound in config.get('outbounds', []):
        if outbound.get('type') == 'wireguard':
            outbound['local_address'][1] = ipv6
            outbound['server_port'] = port
            outbound['server'] = ipv6
            outbound['private_key'] = generate_private_key()
            updated = True

    if not updated:
        wireguard_default["tag"] = "WARP-in-WARP"
        config['outbounds'].append(wireguard_default)

    return config

def save_config(config):
    """Save updated configuration"""
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=2)

def main():
    ipv6, port = extract_ipv6_port()
    if not ipv6 or not port:
        print("❌ Failed to get IPv6 and port.")
        return

    config = load_config()
    updated_config = update_wireguard_config(config, ipv6, port)
    save_config(updated_config)

    print(f"✅ Updated: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()
