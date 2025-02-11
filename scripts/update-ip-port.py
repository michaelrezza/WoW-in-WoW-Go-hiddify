import json
import os
import random
import subprocess

def generate_private_key():
    """Generate a new private key for WireGuard"""
    try:
        return subprocess.check_output(["wg", "genkey"]).decode("utf-8").strip()
    except Exception as e:
        print(f"❌ Error generating private key: {e}")
        return "[private_key]"

def generate_random_port():
    """Generate a random port within the allowed range"""
    return random.randint(1024, 65535)

def get_ipv6():
    """Retrieve the best IPv6 from WARP or system"""
    try:
        ipv6 = subprocess.check_output(["wg", "show", "warp", "endpoints"]).decode().split(":")[0].strip()
        if ipv6:
            return ipv6
    except Exception as e:
        print(f"⚠️ Failed to get WARP IPv6: {e}")
    
    # Fallback method
    return os.getenv('BEST_IPV6', '2606:4700:d0::1')

def load_config():
    """Load the configuration file"""
    if not os.path.exists('hiddify-config.json') or os.stat('hiddify-config.json').st_size == 0:
        print("⚠️ Config file not found. Creating default...")
        return {"route": {}, "outbounds": []}
    try:
        with open('hiddify-config.json', 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("❌ Invalid JSON. Resetting...")
        return {"route": {}, "outbounds": []}

def update_wireguard_config(config, ipv6, port):
    """Update WireGuard config dynamically"""
    
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
        wireguard_default["tag"] = "IP-> Main"
        config['outbounds'].append(wireguard_default)

    return config

def save_config(config):
    """Save updated config"""
    with open('hiddify-config.json', 'w') as file:
        json.dump(config, file, indent=2)

def main():
    ipv6 = get_ipv6()
    port = generate_random_port()
    config = load_config()
    updated_config = update_wireguard_config(config, ipv6, port)
    save_config(updated_config)
    print(f"✅ Updated: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()
