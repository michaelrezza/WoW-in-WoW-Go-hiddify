import json
import os
import random

def generate_random_port():
    return random.randint(1024, 65535)

# Get the fastest IPv6 or default value
best_ipv6 = os.getenv('BEST_IPV6', '2606:4700:d0::1')

# Check and read `hiddify-config.json`
config_file = 'hiddify-config.json'

if not os.path.exists(config_file) or os.stat(config_file).st_size == 0:
    print("❌ Error: `hiddify-config.json` is missing or empty! Creating a new one...")
    default_config = {"outbounds": []}
    with open(config_file, 'w') as file:
        json.dump(default_config, file, indent=2)

with open(config_file, 'r') as file:
    try:
        config = json.load(file)
    except json.JSONDecodeError:
        print("❌ Error: `hiddify-config.json` is invalid! Resetting to default...")
        config = {"outbounds": []}
        with open(config_file, 'w') as file:
            json.dump(config, file, indent=2)

# Update IPv6 and assign a new random port
for outbound in config.get('outbounds', []):
    if outbound.get('type') == 'wireguard':
        outbound['local_address'][1] = best_ipv6
        outbound['server_port'] = generate_random_port()

# Save the updated configuration
with open(config_file, 'w') as file:
    json.dump(config, file, indent=2)

print(f"✅ Updated to Fastest IPv6: {best_ipv6}")