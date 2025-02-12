import os
import json
import random
import subprocess

CONFIG_TEMPLATE = "config-template.json"
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

def load_template():
    """Load the configuration template"""
    with open(CONFIG_TEMPLATE, "r") as file:
        return json.load(file)

def update_config(template, ipv6, port):
    """Update the template with new values"""
    private_key = generate_private_key()

    for outbound in template["outbounds"]:
        if outbound["type"] == "wireguard":
            outbound["private_key"] = private_key
            outbound["server"] = ipv6
            outbound["server_port"] = port
            outbound["local_address"][1] = ipv6

    return template

def save_config(config):
    """Save the updated configuration file"""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=2)

def ensure_permissions():
    """Ensure correct permissions for the config file"""
    os.chmod(CONFIG_FILE, 0o644)
    print("✅ Permissions for hiddify-config.json set correctly.")

def main():
    ipv6, port = get_best_ipv6()
    config_template = load_template()
    updated_config = update_config(config_template, ipv6, port)
    save_config(updated_config)
    ensure_permissions()
    print(f"✅ WireGuard updated: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()