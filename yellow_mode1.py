"""
H6008 may use mode 0x01 for RGB color (not 0x02 like H6001).
The device notification responded with 0x01 when we sent 0x02.
Try sending color with mode byte 0x01 instead.
Also try with notification monitoring to see device response.
"""
import asyncio
from bleak import BleakClient

DEVICE_ADDRESS = "98:17:3C:21:E3:3F"
WRITE_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"
NOTIFY_UUID = "00010203-0405-0607-0809-0a0b0c0d2b10"

def build_frame(cmd, payload):
    frame = bytes([0x33, cmd & 0xFF]) + bytes(payload)
    frame += bytes([0] * (19 - len(frame)))
    checksum = 0
    for b in frame:
        checksum ^= b
    frame += bytes([checksum & 0xFF])
    return frame

def notification_handler(sender, data):
    print(f"  <-- Device: {data.hex()}")

async def main():
    async with BleakClient(DEVICE_ADDRESS, timeout=15.0) as client:
        print("Connected!")
        await client.start_notify(NOTIFY_UUID, notification_handler)

        # Power ON
        await client.write_gatt_char(WRITE_UUID, build_frame(0x01, [0x01]), response=False)
        await asyncio.sleep(1)

        # Brightness max
        await client.write_gatt_char(WRITE_UUID, build_frame(0x04, [0xFF]), response=False)
        await asyncio.sleep(1)

        # Try YELLOW with mode 0x01 (what device seems to want)
        pkt = build_frame(0x05, [0x01, 0xFF, 0xFF, 0x00])
        print(f"  --> Mode 0x01 yellow: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(2)

        # Also try with mode 0x02 and the white-mode flag explicitly
        # payload: [mode, R, G, B, white_flag, Rw, Gw, Bw]
        pkt = build_frame(0x05, [0x02, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xFF, 0x00])
        print(f"  --> Mode 0x02 yellow+secondary: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(2)

        # Try with mode 0x15 (some newer models)
        pkt = build_frame(0x05, [0x15, 0x01, 0xFF, 0xFF, 0x00])
        print(f"  --> Mode 0x15 yellow: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(2)

        # Try raw color with cmd 0xA1 (alternative command byte for some models)
        pkt = build_frame(0xA1, [0x02, 0xFF, 0xFF, 0x00])
        print(f"  --> cmd 0xA1 yellow: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(2)

        print("Done - check notifications for device responses")

asyncio.run(main())
