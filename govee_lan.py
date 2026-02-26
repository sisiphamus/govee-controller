"""
Govee LAN API controller - more reliable than BLE for color control.
Govee devices on the same LAN respond to UDP multicast commands.
"""
import socket
import json
import time

GOVEE_MULTICAST = "239.255.255.250"
GOVEE_PORT = 4001
GOVEE_CMD_PORT = 4003

def scan_devices(timeout=5):
    """Scan for Govee devices on LAN."""
    msg = json.dumps({"msg": {"cmd": "scan", "data": {"account_topic": "reserve"}}})

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    sock.sendto(msg.encode(), (GOVEE_MULTICAST, GOVEE_PORT))

    devices = []
    try:
        while True:
            data, addr = sock.recvfrom(4096)
            device = json.loads(data.decode())
            devices.append((device, addr))
            print(f"Found device: {json.dumps(device, indent=2)} from {addr}")
    except socket.timeout:
        pass

    sock.close()
    return devices

def set_color(ip, device_model, r, g, b):
    """Set device color via LAN API."""
    msg = json.dumps({
        "msg": {
            "cmd": "colorwc",
            "data": {
                "color": {"r": r, "g": g, "b": b},
                "colorTemInKelvin": 0
            }
        }
    })

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg.encode(), (ip, GOVEE_CMD_PORT))
    sock.close()
    print(f"Sent color ({r}, {g}, {b}) to {ip}")

def turn_on(ip):
    """Turn device on via LAN API."""
    msg = json.dumps({
        "msg": {
            "cmd": "turn",
            "data": {"value": 1}
        }
    })
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg.encode(), (ip, GOVEE_CMD_PORT))
    sock.close()
    print(f"Sent ON to {ip}")

def set_brightness(ip, brightness):
    """Set brightness (0-100) via LAN API."""
    msg = json.dumps({
        "msg": {
            "cmd": "brightness",
            "data": {"value": brightness}
        }
    })
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg.encode(), (ip, GOVEE_CMD_PORT))
    sock.close()
    print(f"Sent brightness {brightness} to {ip}")

if __name__ == "__main__":
    print("Scanning for Govee devices on LAN...")
    devices = scan_devices(timeout=5)

    if not devices:
        print("No devices found on LAN. Trying direct broadcast...")
        # Try broadcast on common subnets
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5)
        msg = json.dumps({"msg": {"cmd": "scan", "data": {"account_topic": "reserve"}}})
        sock.sendto(msg.encode(), ("255.255.255.255", GOVEE_PORT))
        try:
            while True:
                data, addr = sock.recvfrom(4096)
                device = json.loads(data.decode())
                devices.append((device, addr))
                print(f"Found device: {json.dumps(device, indent=2)} from {addr}")
        except socket.timeout:
            pass
        sock.close()

    if devices:
        device_data, addr = devices[0]
        ip = addr[0]
        print(f"\nUsing device at {ip}")

        turn_on(ip)
        time.sleep(0.5)
        set_brightness(ip, 100)
        time.sleep(0.5)
        set_color(ip, "H6008", 0, 255, 0)  # Pure green
        print("Done! Light should be green.")
    else:
        print("\nNo Govee devices found on LAN.")
        print("The H6008 may not support LAN API, falling back to BLE approach.")
