import json
import os
import random
import subprocess

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
    """Retrieve the best IPv6 from the environment variable or use the default"""
    return os.getenv('BEST_IPV6', '2606:4700:d0::1')

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
    """Update or add WireGuard settings"""
    
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
    
    found_main = False
    found_ip = False

    for outbound in config.get('outbounds', []):
        if outbound.get('type') == 'wireguard':
            outbound['local_address'][1] = ipv6  # Update IPv6
            outbound['server_port'] = port  # Update port
            outbound['server'] = ipv6  # Set IPv6 as the server
            outbound['private_key'] = generate_private_key()  # Replace private key
            if outbound.get('tag') == "IP-> Your IP address":
                found_ip = True
            if outbound.get('tag') == "IP-> Main":
                found_main = True

    if not found_ip:
        wireguard_ip = wireguard_default.copy()
        wireguard_ip["tag"] = "IP-> Your IP address"
        config['outbounds'].append(wireguard_ip)
    
    if not found_main:
        wireguard_main = wireguard_default.copy()
        wireguard_main["tag"] = "IP-> Main"
        wireguard_main["detour"] = "IP-> Your IP address"
        config['outbounds'].append(wireguard_main)

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
