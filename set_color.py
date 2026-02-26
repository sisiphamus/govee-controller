"""
Reusable Govee color setter. Usage:
    python set_color.py R G B
    python set_color.py 255 255 0   # yellow
"""
import asyncio
import sys
from bleak import BleakClient

DEVICE_ADDRESS = "98:17:3C:21:E3:3F"
WRITE_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"

def build_frame(cmd: int, payload: list[int]) -> bytes:
    frame = bytes([0x33, cmd & 0xFF]) + bytes(payload)
    frame += bytes([0] * (19 - len(frame)))
    checksum = 0
    for b in frame:
        checksum ^= b
    frame += bytes([checksum & 0xFF])
    return frame

async def set_color(r, g, b):
    async with BleakClient(DEVICE_ADDRESS, timeout=15.0) as client:
        await client.write_gatt_char(WRITE_UUID, build_frame(0x01, [0x01]), response=False)
        await asyncio.sleep(0.5)
        await client.write_gatt_char(WRITE_UUID, build_frame(0x04, [0xFF]), response=False)
        await asyncio.sleep(0.5)
        pkt = build_frame(0x05, [0x02, r, g, b])
        print(f"Setting color to ({r}, {g}, {b}) | packet: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(0.5)
        print("Done!")

if __name__ == "__main__":
    r, g, b = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    asyncio.run(set_color(r, g, b))
