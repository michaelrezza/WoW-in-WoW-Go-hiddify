import json
import os
import random
import socket

def generate_random_port():
    """Generate a random port within the appropriate range."""
    return random.randint(1024, 65535)

def get_ipv6():
    """Automatically retrieve the best available IPv6 address."""
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.connect(("2001:4860:4860::8888", 80))  # Test connection to Google DNS
        ipv6 = sock.getsockname()[0]
        sock.close()
        return ipv6
    except Exception:
        return os.getenv('BEST_IPV6', '2606:4700:d0::1')  # Default fallback

# Get the best IPv6 and a random port
best_ipv6 = get_ipv6()
random_port = generate_random_port()

# Check if the configuration file exists and is valid
config_path = 'hiddify-config.json'
if not os.path.exists(config_path) or os.stat(config_path).st_size == 0:
    print("⚠️ Configuration file not found or empty. Creating a default config...")
    config = {"outbounds": []}
else:
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON file. Resetting...")
        config = {"outbounds": []}

# Ensure 'outbounds' key exists
if 'outbounds' not in config or not isinstance(config['outbounds'], list):
    print("⚠️ 'outbounds' key is missing or invalid. Resetting...")
    config['outbounds'] = []

# Update configuration with new IPv6 and port
for outbound in config['outbounds']:
    if outbound.get('type') == 'wireguard':
        # Update IPv6
        if isinstance(outbound.get('local_address'), list) and len(outbound['local_address']) > 1:
            outbound['local_address'][1] = best_ipv6
        else:
            print(f"⚠️ Skipping {outbound} due to missing or invalid 'local_address'")
        
        # Update IP address and port
        outbound['server'] = best_ipv6
        outbound['server_port'] = random_port

# Save updated configuration
with open(config_path, 'w') as file:
    json.dump(config, file, indent=2)

print(f"✅ Configuration updated:\n  🔹 IPv6: {best_ipv6}\n  🔹 Port: {random_port}")
