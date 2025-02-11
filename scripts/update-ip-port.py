import json
import os
import random

def generate_random_port():
    return random.randint(1024, 65535)

# Get the best IPv6 from an environment variable or use a default value
best_ipv6 = os.getenv('BEST_IPV6', '2606:4700:d0::1')

# Load Hiddify configuration
try:
    with open('hiddify-config.json', 'r') as file:
        config = json.load(file)
except (json.JSONDecodeError, FileNotFoundError):
    print("❌ Error: `hiddify-config.json` is invalid or missing!")
    exit(1)

# Update WireGuard settings
updated = False
for outbound in config.get('outbounds', []):
    if outbound.get('type') == 'wireguard':
        if isinstance(outbound.get('local_address'), list) and len(outbound['local_address']) > 1:
            outbound['local_address'][1] = best_ipv6
            updated = True
        else:
            print(f"⚠️ Skipping WireGuard outbound {outbound.get('tag', '')} due to missing 'local_address'.")

        outbound['server_port'] = generate_random_port()
        updated = True

# Save changes only if an update was made
if updated:
    with open('hiddify-config.json', 'w') as file:
        json.dump(config, file, indent=2)
    print(f"✅ Update completed! Fastest IPv6: {best_ipv6}")
else:
    print("⚠️ No valid changes were made.")