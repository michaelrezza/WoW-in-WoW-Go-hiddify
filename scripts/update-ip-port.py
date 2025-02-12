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
        print(f"Error generating private key: {e}")
        return None

def generate_random_port():
    """Generate a random port within the allowed range"""
    return random.randint(1024, 65535)

def get_best_ipv6():
    """Retrieve the best IPv6 address"""
    try:
        result = subprocess.check_output(["curl", "-s", "https://ipv6.icanhazip.com"]).decode("utf-8").strip()
        return result
    except Exception as e:
        print(f"Error retrieving IPv6 address: {e}")
        return None

def load_config():
    """Load the existing configuration file"""
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} not found.")
        return None
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error: Invalid {CONFIG_FILE}.")
        return None

def update_wireguard_config(config, ipv6, port, private_key):
    """Update WireGuard settings with new IPv6, port, and private key"""
    if not config or "outbounds" not in config:
        print("Invalid configuration format.")
        return None

    for outbound in config["outbounds"]:
        if outbound.get("type") == "wireguard":
            outbound["local_address"] = ["172.16.0.2/32", ipv6]
            outbound["private_key"] = private_key
            outbound["server"] = ipv6
            outbound["server_port"] = port

    return config

def save_config(config):
    """Save the updated configuration file"""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=2)

def main():
    ipv6 = get_best_ipv6()
    port = generate_random_port()
    private_key = generate_private_key()

    if not ipv6 or not private_key:
        print("Failed to retrieve necessary information.")
        return

    config = load_config()
    if not config:
        return

    updated_config = update_wireguard_config(config, ipv6, port, private_key)
    if updated_config:
        save_config(updated_config)
        print(f"Updated WireGuard configuration: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()