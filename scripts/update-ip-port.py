import json
import os
import random
import subprocess

def generate_private_key():
    """Generate a new private key for WireGuard."""
    try:
        return subprocess.check_output(["wg", "genkey"]).decode("utf-8").strip()
    except Exception as e:
        print(f"❌ Error generating private key: {e}")
        return "[private_key]"

def generate_random_port():
    """Generate a random port within the allowed range."""
    return random.randint(1024, 65535)

def get_best_ipv6():
    """Retrieve the best available IPv6 dynamically."""
    try:
        ipv6 = subprocess.check_output(["curl", "-s", "https://api64.ipify.org"]).decode("utf-8").strip()
        return ipv6 if ":" in ipv6 else None
    except Exception as e:
        print(f"⚠️ Error fetching IPv6: {e}")
        return None

def load_config():
    """Load the Hiddify configuration file and validate its contents."""
    config_path = 'hiddify-config.json'
    if not os.path.exists(config_path) or os.stat(config_path).st_size == 0:
        print("⚠️ hiddify-config.json not found or empty. Creating a default configuration...")
        return {"route": {}, "outbounds": []}

    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("❌ Error: hiddify-config.json is invalid. Resetting...")
        return {"route": {}, "outbounds": []}

def update_wireguard_config(config, ipv6, port):
    """Update or add WireGuard settings with dynamic server and server_port."""

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
        config['outbounds'].append(wireguard_default)

    return config

def save_config(config):
    """Save the updated configuration file."""
    with open('hiddify-config.json', 'w') as file:
        json.dump(config, file, indent=2)

def main():
    ipv6 = get_best_ipv6()
    if not ipv6:
        print("❌ No valid IPv6 found. Exiting.")
        return

    port = generate_random_port()
    config = load_config()
    updated_config = update_wireguard_config(config, ipv6, port)
    save_config(updated_config)
    print(f"✅ WireGuard updated: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()
