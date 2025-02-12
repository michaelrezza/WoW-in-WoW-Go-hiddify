import os
import json
import random
import subprocess

CONFIG_TEMPLATE = "config-template.json"
CONFIG_FILE = "hiddify-config.json"

def generate_private_key():
    """Generate a new WireGuard private key"""
    try:
        return subprocess.check_output(["wg", "genkey"]).decode("utf-8").strip()
    except Exception as e:
        print(f"❌ Error generating private key: {e}")
        return "REPLACE_WITH_VALID_PRIVATE_KEY"

def generate_random_port():
    """Generate a random port within the allowed range"""
    return random.randint(1024, 65535)

def get_best_ipv6():
    """Retrieve the best IPv6 from the scanner output"""
    if not os.path.exists("./scripts/warp-go.sh"):
        print("❌ Error: warp-go.sh not found!")
        return "2606:4700:d0::1", generate_random_port()
    
    try:
        result = subprocess.check_output(["bash", "./scripts/warp-go.sh", "2"]).decode("utf-8").strip()
        ipv6, port = result.replace("[", "").replace("]", "").split(":")
        return ipv6, int(port) if port.isdigit() else generate_random_port()
    except Exception as e:
        print(f"❌ Error retrieving IPv6: {e}")
        return "2606:4700:d0::1", generate_random_port()

def load_config_template():
    """Load the configuration template"""
    if not os.path.exists(CONFIG_TEMPLATE):
        print(f"❌ Error: {CONFIG_TEMPLATE} not found!")
        return None
    
    try:
        with open(CONFIG_TEMPLATE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("❌ Error: Invalid config-template.json format.")
        return None

def update_config(template, ipv6, port, private_key):
    """Update the WireGuard settings dynamically"""
    for outbound in template.get("outbounds", []):
        if outbound.get("type") == "wireguard":
            outbound["local_address"][1] = ipv6
            outbound["private_key"] = private_key
            outbound["server"] = ipv6
            outbound["server_port"] = port
    return template

def save_config(config):
    """Save the updated configuration file"""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=2)

def ensure_permissions():
    """Ensure correct permissions for the config file"""
    if os.path.exists(CONFIG_FILE):
        os.chmod(CONFIG_FILE, 0o644)
        print("✅ Permissions for hiddify-config.json set correctly.")

def main():
    ipv6, port = get_best_ipv6()
    private_key = generate_private_key()
    
    config_template = load_config_template()
    if config_template:
        updated_config = update_config(config_template, ipv6, port, private_key)
        save_config(updated_config)
        ensure_permissions()
        print(f"✅ Updated WireGuard: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()