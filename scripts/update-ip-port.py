import os
import json
import random
import subprocess

CONFIG_FILE = "hiddify-config.json"
CONFIG_TEMPLATE_FILE = "config-template.json"  # نام فایل تمپلیت را تعریف کنید

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
    """Retrieve the best IPv6 from the scanner output"""
    try:
        result = subprocess.check_output(["bash", "./scripts/warp-go.sh", "2"]).decode("utf-8").strip()
        if not result:
            raise ValueError("warp-go.sh returned empty result.")
        ipv6, port_str = result.replace("[", "").replace("]", "").split(":")
        port = int(port_str)
        return ipv6, port
    except Exception as e:
        print(f"❌ Error retrieving IPv6 from warp-go.sh: {e}")
        print("⚠️ Fallback to default IPv6 and random port.")
        return "2606:4700:d0::1", generate_random_port() # Default fallback

def load_config():
    """Load and validate the configuration file, or create from template if missing/empty"""
    if not os.path.exists(CONFIG_FILE) or os.stat(CONFIG_FILE).st_size == 0:
        print(f"⚠️ {CONFIG_FILE} not found or empty. Creating from {CONFIG_TEMPLATE_FILE}...")
        if not os.path.exists(CONFIG_TEMPLATE_FILE):
            raise FileNotFoundError(f"❌ Error: {CONFIG_TEMPLATE_FILE} not found. Ensure it exists in the repository.")
        with open(CONFIG_TEMPLATE_FILE, 'r') as template_file:
            config = json.load(template_file)
        save_config(config) # Save the template as the initial config
        return config

    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid {CONFIG_FILE}. Resetting to template...")
        with open(CONFIG_TEMPLATE_FILE, 'r') as template_file: # Load template to reset
            config = json.load(template_file)
        save_config(config) # Save the template as the reset config
        return config

def update_wireguard_config(config, ipv6, port):
    """Update WireGuard settings with new IPv6 and port, create if not exists based on template"""
    wireguard_template = {
        "type": "wireguard",
        "tag": "IP-> Your IP address", # Tag را از تمپلیت اصلی بردارید یا ثابت نگه دارید
        "local_address": ["172.16.0.2/32", ipv6],
        "private_key": generate_private_key(),
        "server": ipv6, # IPv6 را به عنوان server استفاده کنید
        "server_port": port,
        "peer_public_key": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=",
        "reserved": ["reserved"],
        "mtu": 1280,
        "fake_packets": "5-10"
    }

    updated = False
    for outbound in config.get("outbounds", []):
        if outbound.get("type") == "wireguard" and outbound.get("tag") == "IP-> Your IP address": #  تگ را هم چک کنید
            outbound.update(wireguard_template)
            updated = True
            break # اگر پیدا شد، حلقه را تمام کنید

    if not updated:
        print("⚠️ WireGuard outbound with tag 'IP-> Your IP address' not found. Creating a new one.")
        config["outbounds"].append(wireguard_template) # اضافه کردن به outbounds اگر پیدا نشد

    # به‌روزرسانی بخش 'IP-> Main' (اگر وجود داشته باشد و نیاز به تغییر IP داشته باشد)
    for outbound in config.get("outbounds", []):
        if outbound.get("type") == "wireguard" and outbound.get("tag") == "IP-> Main":
            outbound["server"] = ipv6 # فقط IP سرور را به‌روز کنید، پورت و کلید را ثابت نگه دارید
            print("✅ Updated 'IP-> Main' server IP to new IPv6.")
            break # اگر پیدا شد، حلقه را تمام کنید

    return config


def save_config(config):
    """Save the updated configuration file"""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=2)

def ensure_permissions():
    """Ensure correct permissions for the config file"""
    if os.path.exists(CONFIG_FILE):
        os.chmod(CONFIG_FILE, 0o644) # Set correct read/write permissions
        print("✅ Permissions for hiddify-config.json set correctly.")

def main():
    ipv6, port = get_best_ipv6()
    config = load_config()
    updated_config = update_wireguard_config(config, ipv6, port)
    save_config(updated_config)
    ensure_permissions()
    print(f"✅ WireGuard configuration updated successfully: IPv6 -> {ipv6}, Port -> {port}")

if __name__ == "__main__":
    main()
