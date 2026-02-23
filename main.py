import subprocess
import platform
import time
import socket
import ipaddress

# using threads
from concurrent.futures import ThreadPoolExecutor


TARGET_PORT = 22
TIMEOUT = 2

online_ips = []

networks_to_scan = [
    "172.30.81.0/24",
    "192.168.65.0/24",
]

ips_to_scan = []

for net_string in networks_to_scan:
    network = ipaddress.IPv4Network(net_string, strict=False)

    for ip in network.hosts():
        ips_to_scan.append(str(ip))

print(f"Total IPs queued for scanning: {len(ips_to_scan)}")


# function for pinging devices
def ping_ip(ip):
    # -n for windows -c for linux and other os
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = [
        "ping",
        param,
        "1",
        "-w",
        "1000",
        ip,
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT,
            text=True,
        )

        if "TTL=" in result.stdout.upper():
            online_ips.append(ip)
            return f"[+] ONLINE: {ip}"
        else:
            return None

    except subprocess.TimeoutExpired:
        return None


def scan_ip(ip):
    # Create a new network socket to test ip
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)

        # returns 0 for success
        result = s.connect_ex((ip, TARGET_PORT))

        if result == 0:
            return f"[+] SUCCESS: {ip} is ONLINE and Port {TARGET_PORT} is OPEN!"
        else:
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


def run_sequential_scan(ips):
    print("\n--- Starting Sequential Scan ---")
    start_time = time.perf_counter()

    for ip in ips:
        result = scan_ip(ip)
        if result:
            print(result)

    end_time = time.perf_counter()
    print(f"Sequential Scan took: {end_time - start_time:.2f} seconds")


def run_threaded_scan(ips):
    print("\n--- Starting Threaded Scan ---")
    start_time = time.perf_counter()

    # 100 threads
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(scan_ip, ips)

        for result in results:
            if result:
                print(result)

    end_time = time.perf_counter()
    print(f"Threaded Scan took: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    # --- TESTING FOR KNOWN IPS ---

    # testing ping function
    # using PSU wifi
    # print(ping_ip("172.31.201.112"))

    # testing ssh scan function
    # testing vm (ssh is open) to see if the function works
    # print(scan_ip("192.168.65.133"))

    # --- PINGING TO GET IPS ---

    run_threaded_ping(ips_to_scan)
    # run_sequential_ping(ips_to_scan)

    # --- SCANNING FOR OPEN SSH PORTS
    if online_ips:
        print(f"Found {len(online_ips)} IP(s)!")
        # run_sequential_scan(online_ips)
        run_threaded_scan(online_ips)
