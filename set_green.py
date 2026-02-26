"""Send power on, brightness 100, and green color in sequence with delays."""
import asyncio
from govee_ble import cmd_power_on, cmd_brightness, cmd_color, DEVICE_ADDRESS, WRITE_UUID
from bleak import BleakClient

async def main():
    async with BleakClient(DEVICE_ADDRESS, timeout=15.0) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return

        print("Connected. Sending power ON...")
        await client.write_gatt_char(WRITE_UUID, cmd_power_on(), response=False)
        await asyncio.sleep(1)

        print("Setting brightness to 100%...")
        await client.write_gatt_char(WRITE_UUID, cmd_brightness(100), response=False)
        await asyncio.sleep(1)

        print("Setting color to GREEN (0, 255, 0)...")
        await client.write_gatt_char(WRITE_UUID, cmd_color(0, 255, 0), response=False)
        await asyncio.sleep(0.5)

        # Send color again to be sure
        print("Re-sending green...")
        await client.write_gatt_char(WRITE_UUID, cmd_color(0, 255, 0), response=False)
        await asyncio.sleep(0.5)

        print("Done! Light should be green.")

asyncio.run(main())
