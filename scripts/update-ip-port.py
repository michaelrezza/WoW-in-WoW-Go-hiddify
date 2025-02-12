import os
import json
import random
import subprocess

CONFIG_FILE = "hiddify-config.json"

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
    """Retrieve the best IPv6 from the scanner output"""
    try:
        result = subprocess.check_output(["bash", "./scripts/warp-go.sh", "2"]).decode("utf-8").strip()
        ipv6, port = result.replace("[", "").replace("]", "").split(":")
        return ipv6, int(port)
    except Exception as e:
        print(f"❌ Error retrieving IPv6: {e}")
        return "2606:4700:d0::1", generate_random_port()  # Default fallback

def load_config():
    """Load and validate the configuration file"""
    if not os.path.exists(CONFIG_FILE) or os.stat(CONFIG_FILE).st_size == 0:
        print("⚠️ hiddify-config.json not found or empty. Creating default configuration...")
        return {"route": {}, "outbounds": []}
    
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("❌ Error: Invalid hiddify-config.json. Resetting...")
        return {"route": {}, "outbounds": []}

def update_wireguard_config(config, ipv6, port):
    """Update WireGuard settings with new IPv6 and port"""

    wireguard_template = {
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

    # Check and update existing WireGuard settings
    updated = False
    for outbound in config.get("outbounds", []):
        if outbound.get("type") == "wireguard":
            outbound.update(wireguard_template)
            updated = True

    # Add new entry if not found
    if not updated:
        config["outbounds"].append(wireguard_template)

    return config

def save_config(config):
    """Save the updated configuration file"""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=2)

def ensure_permissions():
    """Ensure correct permissions for the config file"""
    if os.path.exists(CONFIG_FILE):
        os.chmod(CONFIG_FILE, 0o644)  # Set correct read/write permissions
        print("✅ Permissions for hiddify-config.json set correctly.")

def main():
    ipv6, port = get_best_ipv6()
    config = load_config()
    updated_config = update_wireguard_config(config, ipv6, port)
    save_config(updated_config)
    ensure_permissions()
    print(f"✅ WireGuard updated: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()
