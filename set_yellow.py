"""Set Govee to yellow with proper sequencing."""
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

        # Power on
        await client.write_gatt_char(WRITE_UUID, build_frame(0x01, [0x01]), response=False)
        await asyncio.sleep(1)

        # Brightness max
        await client.write_gatt_char(WRITE_UUID, build_frame(0x04, [0xFF]), response=False)
        await asyncio.sleep(1)

        # Set YELLOW (255, 255, 0) - send 3 times to be sure
        for i in range(3):
            pkt = build_frame(0x05, [0x02, 0xFF, 0xFF, 0x00])
            print(f"  Yellow attempt {i+1}: {pkt.hex()}")
            await client.write_gatt_char(WRITE_UUID, pkt, response=False)
            await asyncio.sleep(1)

        print("Done! Should be yellow now.")

asyncio.run(main())
