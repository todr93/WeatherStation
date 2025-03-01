import subprocess


def add_wifi_nmcli(ssid, password):
    try:
        command = [
            "nmcli", "device", "wifi", "connect", ssid, "password", password
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return result.returncode, ""
        else:
            return result.returncode, result.stderr
    
    except Exception as e:
        return -1, e
