import subprocess
import platform
import time
from concurrent.futures import ThreadPoolExecutor


def ping_ip(ip):
    # -n for windows -c for linux and other os
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]

    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1
        )

        # returns 0 for success
        if result.returncode == 0:
            return f"[+] ONLINE: {ip}"
        else:
            return None

    except subprocess.TimeoutExpired:
        return None


if __name__ == "__main__":
    print(ping_ip("172.31.201.112"))
