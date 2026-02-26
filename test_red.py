"""
Send pure red (255, 0, 0) to test if the standard format is actually taking effect.
If it stays blue, the standard format isn't working and blue is from a previous command.
"""
import asyncio
from bleak import BleakClient

DEVICE_ADDRESS = "98:17:3C:21:E3:3F"
WRITE_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"

def build_packet(cmd: int, payload: list[int]) -> bytearray:
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

async def main():
    async with BleakClient(DEVICE_ADDRESS, timeout=15.0) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return

        print("Connected!")

        # Power on
        await client.write_gatt_char(WRITE_UUID, build_packet(0x01, [0x01]), response=False)
        await asyncio.sleep(0.5)

        # Try RED with every plausible format to see which one the device responds to
        formats = [
            ("A: cmd=0x05 [0x02, 255, 0, 0]", 0x05, [0x02, 255, 0, 0]),
            ("B: cmd=0x05 [0x01, 255, 0, 0]", 0x05, [0x01, 255, 0, 0]),
            ("C: cmd=0x05 [0x04, 255, 0, 0]", 0x05, [0x04, 255, 0, 0]),
            ("D: cmd=0x0B [0x02, 255, 0, 0]", 0x0B, [0x02, 255, 0, 0]),
            ("E: cmd=0x05 [0x02, 0x00, 255, 0, 0]", 0x05, [0x02, 0x00, 255, 0, 0]),
            ("F: cmd=0x05 [0x0D, 0x02, 255, 0, 0]", 0x05, [0x0D, 0x02, 255, 0, 0]),
        ]

        for name, cmd, payload in formats:
            print(f"Sending {name}")
            pkt = build_packet(cmd, payload)
            print(f"  Packet: {pkt.hex()}")
            await client.write_gatt_char(WRITE_UUID, pkt, response=False)
            await asyncio.sleep(3)

        print("Done. Check if color changed to red at any point.")

asyncio.run(main())
