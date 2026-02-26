"""
Clean, single-format approach matching govee_btled exactly.
First set to red (to verify the command works), pause, then set to green.
"""
import asyncio
from bleak import BleakClient

DEVICE_ADDRESS = "98:17:3C:21:E3:3F"
WRITE_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"

def build_govee_frame(cmd: int, payload: list[int]) -> bytes:
    """Exact match of govee_btled's _send method."""
    frame = bytes([0x33, cmd & 0xFF]) + bytes(payload)
    # Pad to 19 bytes
    frame += bytes([0] * (19 - len(frame)))
    # XOR checksum
    checksum = 0
    for b in frame:
        checksum ^= b
    frame += bytes([checksum & 0xFF])
    return frame

async def main():
    async with BleakClient(DEVICE_ADDRESS, timeout=15.0) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return

        print(f"Connected! Services:")
        for service in client.services:
            for char in service.characteristics:
                if "2b11" in str(char.uuid):
                    print(f"  {char.uuid} props={char.properties}")

        # Power ON
        pkt = build_govee_frame(0x01, [0x01])
        print(f"\nPower ON: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(1)

        # Brightness 100% (0xFF = max in govee_btled format)
        pkt = build_govee_frame(0x04, [0xFF])
        print(f"Brightness 100%: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(1)

        # Set RED first as a test (Manual mode = 0x02, R=255, G=0, B=0)
        pkt = build_govee_frame(0x05, [0x02, 0xFF, 0x00, 0x00])
        print(f"Set RED: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(5)
        print("  (light should be RED now - waiting 5s)")

        # Now set GREEN (Manual mode = 0x02, R=0, G=255, B=0)
        pkt = build_govee_frame(0x05, [0x02, 0x00, 0xFF, 0x00])
        print(f"Set GREEN: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(1)

        print("Done! Light should now be GREEN.")

asyncio.run(main())
