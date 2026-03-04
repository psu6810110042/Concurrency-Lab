import subprocess
import platform
import time
import socket
import paramiko
import ipaddress

# using threads
from concurrent.futures import ThreadPoolExecutor


TARGET_USER = "user"
TARGET_PASS = "1234"

TARGET_PORT = 22
TIMEOUT = 2

online_ips = []

# ผมไม่อยากโดน ban จาก wifi
networks_to_scan = [
    # "172.30.91.0/24",
    # "172.30.90.0/24",
    # "172.30.89.0/24",
    "192.168.65.0/24",
    # "192.168.1.0/24"
]

ips_to_scan = []
ips_with_ssh_open = []

for net_string in networks_to_scan:
    network = ipaddress.IPv4Network(net_string, strict=False)

    for ip in network.hosts():
        ips_to_scan.append(str(ip))

print(f"Total IPs queued for scanning: {len(ips_to_scan)}")


# --- HELPER FUNCTIONS ---
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


# function the scan IPs for open ssh ports
def scan_ip(ip):
    # Create a new network socket to test ip
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)

        # returns 0 for success
        result = s.connect_ex((ip, TARGET_PORT))

        if result == 0:
            ips_with_ssh_open.append(ip)
            return f"[+] SUCCESS: {ip} is ONLINE and Port {TARGET_PORT} is OPEN!"
        else:
            return None


# function to check if ssh credentials work
def check_ssh_login(ip):
    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            ip,
            port=TARGET_PORT,
            username=TARGET_USER,
            password=TARGET_PASS,
            timeout=3,
            auth_timeout=3,
        )

        stdin, stdout, stderr = client.exec_command("hostname")
        hostname = stdout.read().decode().strip()

        client.close()
        return f"[***] FOUND IT! Successfully logged into {ip} (Hostname: {hostname})"

    except paramiko.AuthenticationException:
        return f"[-] Auth failed for {ip} (Wrong credentials)"
    except Exception as e:
        return f"[-] SSH failed for {ip}: {str(e)}"
    finally:
        client.close()


# --- SEQUENTIAL FUNCTIONS ---
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


# sequential scanning
def run_sequential_scan(ips):
    print("\n--- Starting Sequential Scan ---")
    start_time = time.perf_counter()

    for ip in ips:
        result = scan_ip(ip)
        if result:
            print(result)

    end_time = time.perf_counter()
    print(f"Sequential Scan took: {end_time - start_time:.2f} seconds")


# --- THREADING FUNCTIONS ---
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


def run_threaded_ssh_search(ips_with_open_ports):
    print(
        f"\n--- Starting Authenticated SSH Search on {len(ips_with_open_ports)} IPs ---"
    )
    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_ssh_login, ips_with_open_ports)

        for result in results:
            if result:
                print(result)

    end_time = time.perf_counter()
    print(f"SSH Search took: {end_time - start_time:.2f} seconds")


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
    run_sequential_ping(ips_to_scan)

    # --- SCANNING FOR OPEN SSH PORTS
    if online_ips:
        print(f"Found {len(online_ips)} IP(s)!")
        run_sequential_scan(online_ips)
        run_threaded_scan(online_ips)

        # --- CHECK IF SSH CREDENTIALS MATCH ---
        run_threaded_ssh_search(ips_with_ssh_open)
