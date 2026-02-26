"""
Channel mapping test: send pure red, wait, take note, then pure blue.
Based on evidence:
  - Sent (0, 255, 0) green → bulb showed BLUE  → my G maps to device B
  - Sent (255, 0, 0) red → bulb showed GREEN   → my R maps to device G
  - Therefore: my B likely maps to device R

Channel map: send(R,G,B) → device shows (B, R, G)
  i.e. my R→deviceG, my G→deviceB, my B→deviceR

To get YELLOW on device (R=255, G=255, B=0):
  deviceR=255 → need my B=255
  deviceG=255 → need my R=255
  deviceB=0   → need my G=0
  → send (255, 0, 255) i.e. magenta in standard RGB
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
        print("Connected!")

        await client.write_gatt_char(WRITE_UUID, build_frame(0x01, [0x01]), response=False)
        await asyncio.sleep(1)
        await client.write_gatt_char(WRITE_UUID, build_frame(0x04, [0xFF]), response=False)
        await asyncio.sleep(1)

        # Send "magenta" (255, 0, 255) which should map to YELLOW on device
        r, g, b = 255, 0, 255
        pkt = build_frame(0x05, [0x02, r, g, b])
        print(f"Sending ({r},{g},{b}) -> should show as YELLOW on device")
        print(f"Packet: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(1)

        # Send again
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(0.5)

        print("Done!")

asyncio.run(main())
