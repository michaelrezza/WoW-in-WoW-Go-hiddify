import json
import os
import random

def generate_random_port():
    return random.randint(1024, 65535)

# Retrieve the best IPv6
best_ipv6 = os.getenv('BEST_IPV6', '2606:4700:d0::1')

# Read Hiddify configuration
with open('hiddify-config.json', 'r') as file:
    config = json.load(file)

# Update configuration with the best IPv6 and a new port
for outbound in config['outbounds']:
    if outbound['type'] == 'wireguard':
        outbound['local_address'][1] = best_ipv6
        outbound['server_port'] = generate_random_port()

# Save updated configuration
with open('hiddify-config.json', 'w') as file:
    json.dump(config, file, indent=2)

print(f"✅ Updated to Fastest IPv6: {best_ipv6}")