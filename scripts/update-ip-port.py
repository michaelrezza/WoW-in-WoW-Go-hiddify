import json
import subprocess
import re

def get_ipv6_and_port():
    """Run the script to get IPv6 and port."""
    try:
        # Download the script and run it to get IPv6 and port
        script_url = "https://raw.githubusercontent.com/Ptechgithub/warp/main/endip/install.sh"
        script_output = subprocess.check_output(["bash", "-c", f"curl -s {script_url} | bash"]).decode("utf-8")
        
        # Search for IPv6 and port in the script's output
        match = re.search(r'(\[[a-fA-F0-9:]+\])(:\d+)', script_output)
        if match:
            ipv6 = match.group(1)
            port = match.group(2)[1:]  # Removing the colon
            return ipv6, port
        else:
            print("No valid IPv6 and port found.")
            return "2001:db8::1", "50286"  # Fallback values if no valid IPv6 is found
    except Exception as e:
        print(f"Error executing script: {e}")
        return "2001:db8::1", "50286"  # Fallback values

def update_config(ipv6, port):
    """Update the WireGuard settings in hiddify-config.json."""
    config_path = 'hiddify-config.json'
    
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        
        # Update the local address and server in the WireGuard settings
        for outbound in config['outbounds']:
            if outbound['type'] == 'wireguard':
                if 'IP-> Your IP address' in outbound['tag']:
                    outbound['local_address'][1] = ipv6  # Update IPv6 address
                    outbound['server'] = ipv6  # Update server
                    outbound['server_port'] = int(port)  # Update port

                if 'IP-> Main' in outbound['tag']:
                    outbound['local_address'][1] = ipv6  # Update IPv6 address
                    outbound['server'] = ipv6  # Update server
                    outbound['server_port'] = int(port)  # Update port

        with open(config_path, 'w') as file:
            json.dump(config, file, indent=2)
        
        print(f"Configuration updated with new IPv6: {ipv6} and Port: {port}")
    except Exception as e:
        print(f"Error updating config: {e}")

if __name__ == "__main__":
    # Get the new IPv6 and port from the script
    new_ipv6, new_port = get_ipv6_and_port()
    
    # Update the configuration file
    update_config(new_ipv6, new_port)
