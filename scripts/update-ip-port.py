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

def start_warp():
    """Start the first WARP tunnel"""
    try:
        subprocess.run(["warp-cli", "disconnect"], check=False)
        subprocess.run(["warp-cli", "connect"], check=True)
        print("✅ WARP-1 started.")
    except Exception as e:
        print(f"❌ Failed to start WARP-1: {e}")

def start_warp_in_warp():
    """Start the second WARP instance inside the first"""
    try:
        subprocess.run(["warp-cli", "disconnect"], check=False)
        subprocess.run(["warp-cli", "connect", "--mode", "proxy"], check=True)
        print("✅ WARP-in-WARP started.")
    except Exception as e:
        print(f"❌ Failed to start WARP-in-WARP: {e}")

def get_warp_ipv6():
    """Retrieve the IPv6 of the second WARP tunnel"""
    try:
        result = subprocess.check_output(["wg", "show", "warp0", "endpoints"]).decode().strip()
        ipv6 = result.split(":")[0] if ":" in result else None
        if ipv6:
            print(f"✅ Retrieved WARP-in-WARP IPv6: {ipv6}")
            return ipv6
    except Exception as e:
        print(f"⚠️ Failed to retrieve WARP-in-WARP IPv6: {e}")
    
    # If no IPv6 is found, raise an error to prevent fallback
    raise ValueError("❌ No valid IPv6 found. Ensure WARP-in-WARP is connected correctly.")

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
            outbound['local_address'][1] = ipv6  # Update IPv6
            outbound['server_port'] = port  # Update port
            outbound['server'] = ipv6  # Set IPv6 as the server
            outbound['private_key'] = generate_private_key()  # Replace private key
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
    start_warp()  # Start WARP-1
    start_warp_in_warp()  # Start WARP-2 inside WARP-1
    ipv6 = get_warp_ipv6()  # Get IPv6 from WARP-in-WARP
    port = generate_random_port()
    config = load_config()
    updated_config = update_wireguard_config(config, ipv6, port)
    save_config(updated_config)
    print(f"✅ Updated: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()
