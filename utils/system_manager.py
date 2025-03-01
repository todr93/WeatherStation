import subprocess


def add_wifi_nmcli(ssid, password):
    try:
        command = [
            "nmcli", "device", "wifi", "connect", ssid, "password", password
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Successfully connected to {ssid}")
        else:
            print(f"Failed to connect: {result.stderr}")
    
    except Exception as e:
        print(f"Error: {e}")

# Usage
add_wifi_nmcli("Your_SSID", "Your_Password")