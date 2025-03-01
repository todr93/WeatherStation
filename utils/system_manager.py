import subprocess


def add_wifi_nmcli(ssid, password):
    try:
        command_list = [
            "sudo", "nmcli", "device", "rescan"
        ]
        command_add = [
            "nmcli", "device", "wifi", "connect", ssid, "password", password
        ]
        subprocess.run(command_list)
        result = subprocess.run(command_add, capture_output=True, text=True)

        if result.returncode == 0:
            return result.returncode, ""
        else:
            return result.returncode, result.stderr
    
    except Exception as e:
        return -1, e
