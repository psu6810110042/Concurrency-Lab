import subprocess
import platform
import time

# using threads
from concurrent.futures import ThreadPoolExecutor


# function for pinging devices
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


# sequential ping
def run_sequential_ping(ips):
    print(f"\n--- Starting Sequential Ping Scan on {len(ips)} IPs ---")
    start_time = time.perf_counter()

    for ip in ips:
        result = ping_ip(ip)
        if result:
            print(result)

    end_time = time.perf_counter()
    print(f"Sequential Scan took: {end_time - start_time:.2f} seconds")


def run_threaded_ping(ips):
    print(f"\n--- Starting Threaded Ping Scan on {len(ips)} IPs ---")
    start_time = time.perf_counter()

    # 100 threads
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(ping_ip, ips)

        for result in results:
            if result:
                print(result)

    end_time = time.perf_counter()
    print(f"Threaded Scan took: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    # using PSU wifi
    # print(ping_ip("172.31.201.112"))
    BASE_IP = "172.31.201."

    # scan ips from 1-254
    ips_to_scan = [f"{BASE_IP}{i}" for i in range(1, 255)]
    run_threaded_ping(ips_to_scan)
    # run_sequential_ping(ips_to_scan)
