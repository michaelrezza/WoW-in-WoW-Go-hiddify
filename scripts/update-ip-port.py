import json
import os
import random

def generate_random_port():
    return random.randint(1024, 65535)

# Retrieve the best IPv6
best_ipv6 = os.getenv('BEST_IPV6', '2606:4700:d0::1')

# Ensure hiddify-config.json exists and is not empty
if not os.path.exists('hiddify-config.json') or os.stat('hiddify-config.json').st_size == 0:
    print("⚠️ hiddify-config.json not found or empty. Creating default config...")
    with open('hiddify-config.json', 'w') as file:
        json.dump({"outbounds": []}, file, indent=2)

# Read Hiddify configuration
try:
    with open('hiddify-config.json', 'r') as file:
        config = json.load(file)
except json.JSONDecodeError:
    print("❌ Error: hiddify-config.json is not a valid JSON file. Resetting...")
    config = {"outbounds": []}

# Ensure 'outbounds' key exists
if 'outbounds' not in config or not isinstance(config['outbounds'], list):
    print("⚠️ 'outbounds' key not found or invalid. Resetting...")
    config['outbounds'] = []

# Update configuration with the best IPv6 and a new port
for outbound in config['outbounds']:
    if outbound.get('type') == 'wireguard':
        if isinstance(outbound.get('local_address'), list) and len(outbound['local_address']) > 1:
            outbound['local_address'][1] = best_ipv6
        else:
            print(f"⚠️ Skipping outbound {outbound} due to missing or invalid 'local_address'")
        outbound['server_port'] = generate_random_port()

# Save updated configuration
with open('hiddify-config.json', 'w') as file:
    json.dump(config, file, indent=2)

print(f"✅ Updated to Fastest IPv6: {best_ipv6}")