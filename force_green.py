"""
Try multiple known Govee color packet formats to force green.
Different H6xxx models use slightly different byte layouts.
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

        # 1) Power on
        print("1) Power ON")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x01, [0x01]), response=False)
        await asyncio.sleep(1.0)

        # 2) Brightness 100%
        print("2) Brightness 100%")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x04, [0x64]), response=False)
        await asyncio.sleep(0.5)

        # 3) Try format A: 0x33 0x05 0x02 R G B (original)
        print("3) Color format A: [0x02, 0, 255, 0]")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x05, [0x02, 0, 255, 0]), response=False)
        await asyncio.sleep(1.5)

        # 4) Try format B: some models use 0x0D for color control
        print("4) Color format B: cmd=0x05, [0x02, 0x00, 0, 255, 0]")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x05, [0x02, 0x00, 0, 255, 0]), response=False)
        await asyncio.sleep(1.5)

        # 5) Try format C: some H6008 use 0x05 0x02 with trailing mode bytes
        print("5) Color format C: [0x02, 0, 255, 0, 0x00, 0xFF, 0xAE]")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x05, [0x02, 0, 255, 0, 0x00, 0xFF, 0xAE]), response=False)
        await asyncio.sleep(1.5)

        # 6) Try format D: some use 0x05 0x01 for manual color mode
        print("6) Color format D: [0x01, 0, 255, 0]")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x05, [0x01, 0, 255, 0]), response=False)
        await asyncio.sleep(1.5)

        # 7) Try sending a scene/mode reset first, then color
        # Some devices need cmd 0x05 subcommand 0x15 or 0x04 to switch modes
        print("7) Mode switch attempt: cmd=0x05 [0x04, 0, 255, 0]")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x05, [0x04, 0, 255, 0]), response=False)
        await asyncio.sleep(1.5)

        # 8) Some newer Govee use cmd 0x33 0x0B for color
        print("8) Alt cmd 0x0B: [0x02, 0, 255, 0]")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x0B, [0x02, 0, 255, 0]), response=False)
        await asyncio.sleep(1.5)

        # 9) Resend the standard format one more time
        print("9) Final: standard [0x02, 0, 255, 0]")
        await client.write_gatt_char(WRITE_UUID, build_packet(0x05, [0x02, 0, 255, 0]), response=False)
        await asyncio.sleep(0.5)

        print("\nDone - tried all known formats. Check if light changed at any point.")

asyncio.run(main())
