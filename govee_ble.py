"""
Govee H6008 BLE Controller
Controls Govee LED lights via Bluetooth Low Energy.

Usage:
    python govee_ble.py on
    python govee_ble.py off
    python govee_ble.py color 255 0 0        # RGB red
    python govee_ble.py color 0 255 0        # RGB green
    python govee_ble.py brightness 50        # 0-100
    python govee_ble.py scan                 # Find Govee devices

Requires: pip install bleak
"""

import asyncio
import sys
from bleak import BleakClient, BleakScanner

# Your Govee H6008
DEVICE_ADDRESS = "98:17:3C:21:E3:3F"
DEVICE_NAME = "ihoment_H6008_E33F"

# Govee BLE UUIDs
WRITE_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"
NOTIFY_UUID = "00010203-0405-0607-0809-0a0b0c0d2b10"


def build_packet(cmd: int, payload: list[int]) -> bytearray:
    """Build a 20-byte Govee BLE command packet with XOR checksum."""
    packet = bytearray(20)
    packet[0] = 0x33
    packet[1] = cmd
    for i, b in enumerate(payload):
        packet[2 + i] = b
    xor = 0
    for b in packet[:-1]:
        xor ^= b
    packet[-1] = xor
    return packet


def cmd_power_on():
    return build_packet(0x01, [0x01])

def cmd_power_off():
    return build_packet(0x01, [0x00])

def cmd_brightness(percent: int):
    return build_packet(0x04, [max(0, min(100, percent))])

def cmd_color(r: int, g: int, b: int):
    return build_packet(0x05, [0x02, r & 0xFF, g & 0xFF, b & 0xFF])

def cmd_color_temp(kelvin: int):
    """Set color temperature. Range varies by device, typically 2000-9000K."""
    return build_packet(0x05, [0x02, 0xFF, 0xFF, 0xFF, 0x01, (kelvin >> 8) & 0xFF, kelvin & 0xFF])


async def send_command(packet: bytearray, address: str = DEVICE_ADDRESS):
    """Connect to the Govee device and send a single command."""
    async with BleakClient(address, timeout=10.0) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return False
        await client.write_gatt_char(WRITE_UUID, packet, response=False)
        return True


async def scan_govee():
    """Scan for nearby Govee BLE devices."""
    print("Scanning for Govee BLE devices (10 seconds)...")
    devices = await BleakScanner.discover(timeout=10.0, return_adv=True)
    found = []
    for address, (device, adv_data) in devices.items():
        name = device.name or adv_data.local_name or ""
        if any(x in name.lower() for x in ["govee", "ihoment", "h6", "h7"]):
            found.append((name, device.address, adv_data.rssi))
            print(f"  Found: {name} | {device.address} | RSSI: {adv_data.rssi}")
    if not found:
        print("  No Govee devices found nearby.")
    return found


NAMED_COLORS = {
    "red":     (255, 0, 0),
    "green":   (0, 255, 0),
    "blue":    (0, 0, 255),
    "white":   (255, 255, 255),
    "warm":    (255, 180, 80),
    "purple":  (128, 0, 255),
    "cyan":    (0, 255, 255),
    "yellow":  (255, 255, 0),
    "orange":  (255, 100, 0),
    "pink":    (255, 50, 150),
}


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    action = sys.argv[1].lower()

    if action == "scan":
        await scan_govee()
        return

    if action == "on":
        pkt = cmd_power_on()
        print("Turning ON...")
    elif action == "off":
        pkt = cmd_power_off()
        print("Turning OFF...")
    elif action == "brightness" and len(sys.argv) >= 3:
        val = int(sys.argv[2])
        pkt = cmd_brightness(val)
        print(f"Setting brightness to {val}%...")
    elif action == "color" and len(sys.argv) >= 3:
        if sys.argv[2].lower() in NAMED_COLORS:
            r, g, b = NAMED_COLORS[sys.argv[2].lower()]
        elif len(sys.argv) >= 5:
            r, g, b = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        else:
            print("Usage: govee_ble.py color <r> <g> <b>  OR  govee_ble.py color <name>")
            print(f"Named colors: {', '.join(NAMED_COLORS.keys())}")
            return
        pkt = cmd_color(r, g, b)
        print(f"Setting color to ({r}, {g}, {b})...")
    else:
        print(f"Unknown command: {action}")
        print(__doc__)
        return

    ok = await send_command(pkt)
    if ok:
        print("Done.")
    else:
        print("Failed to send command.")


if __name__ == "__main__":
    asyncio.run(main())
