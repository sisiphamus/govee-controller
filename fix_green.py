"""
The light went blue when we sent G=255. Channels are likely swapped.
Try different channel orderings to find the correct one for green.
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

        # Power on + brightness
        await client.write_gatt_char(WRITE_UUID, build_packet(0x01, [0x01]), response=False)
        await asyncio.sleep(0.5)
        await client.write_gatt_char(WRITE_UUID, build_packet(0x04, [0x64]), response=False)
        await asyncio.sleep(0.5)

        # Since (0,255,0) gave blue, G and B are likely swapped.
        # To get green, send B=255 instead: (0, 0, 255)
        # Try this with the standard format
        print("Attempt: standard format with swapped channels (0, 0, 255)")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x05, [0x02, 0, 0, 255]), response=False)
        await asyncio.sleep(2)

        print("Done.")

asyncio.run(main())
