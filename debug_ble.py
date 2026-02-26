"""Debug: list all services/characteristics and try reading state."""
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

received = []

def notification_handler(sender, data):
    print(f"  NOTIFY from {sender}: {data.hex()}")
    received.append(data)

async def main():
    async with BleakClient(DEVICE_ADDRESS, timeout=15.0) as client:
        print("Connected!")
        print("\n--- ALL SERVICES & CHARACTERISTICS ---")
        for service in client.services:
            print(f"\nService: {service.uuid}")
            for char in service.characteristics:
                print(f"  Char: {char.uuid}")
                print(f"    Props: {char.properties}")
                for desc in char.descriptors:
                    print(f"    Desc: {desc.uuid}")

        # Subscribe to notifications
        print("\n--- SUBSCRIBING TO NOTIFICATIONS ---")
        try:
            await client.start_notify(NOTIFY_UUID, notification_handler)
            print(f"Subscribed to {NOTIFY_UUID}")
        except Exception as e:
            print(f"Could not subscribe to notify: {e}")
            # Try the write UUID for reading
            try:
                val = await client.read_gatt_char(WRITE_UUID)
                print(f"Read from write char: {val.hex()}")
            except Exception as e2:
                print(f"Could not read write char: {e2}")

        # Send power ON and wait for response
        print("\n--- SENDING POWER ON ---")
        pkt = build_frame(0x01, [0x01])
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(2)

        # Send a query/status request (command 0xAA is sometimes used)
        print("\n--- SENDING STATUS QUERY ---")
        for query_cmd in [0xAA, 0x81, 0x31]:
            pkt = build_frame(query_cmd, [0x01])
            print(f"  Query cmd 0x{query_cmd:02x}: {pkt.hex()}")
            await client.write_gatt_char(WRITE_UUID, pkt, response=False)
            await asyncio.sleep(1)

        # Now send yellow
        print("\n--- SENDING YELLOW ---")
        pkt = build_frame(0x05, [0x02, 0xFF, 0xFF, 0x00])
        print(f"  Yellow: {pkt.hex()}")
        await client.write_gatt_char(WRITE_UUID, pkt, response=False)
        await asyncio.sleep(2)

        print(f"\nTotal notifications received: {len(received)}")

asyncio.run(main())
