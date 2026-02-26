"""
Replicate clean_green.py's exact working pattern but end with yellow.
That script: power on -> brightness -> RED (5s wait) -> GREEN
This script: power on -> brightness -> RED (5s wait) -> YELLOW
"""
import asyncio
from bleak import BleakClient

DEVICE_ADDRESS = "98:17:3C:21:E3:3F"
WRITE_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"

def build_frame(cmd, payload):
    frame = bytes([0x33, cmd & 0xFF]) + bytes(payload)
    frame += bytes([0] * (19 - len(frame)))
    checksum = 0
    for b in frame:
        checksum ^= b
    frame += bytes([checksum & 0xFF])
    return frame

async def main():
    async with BleakClient(DEVICE_ADDRESS, timeout=15.0) as client:
        if not client.is_connected:
            print("Failed to connect")
            return

        print("Connected!")

        # Power ON
        pkt = build_frame(0x01, [0x01])
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(1)
        print("Power ON sent")

        # Brightness max
        pkt = build_frame(0x04, [0xFF])
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(1)
        print("Brightness sent")

        # Set RED first (exactly like clean_green.py)
        pkt = build_frame(0x05, [0x02, 0xFF, 0x00, 0x00])
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        print("RED sent, waiting 5s...")
        await asyncio.sleep(5)

        # Now set YELLOW (R=255, G=255, B=0)
        pkt = build_frame(0x05, [0x02, 0xFF, 0xFF, 0x00])
        print(f"YELLOW packet: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(1)
        print("YELLOW sent!")

asyncio.run(main())
