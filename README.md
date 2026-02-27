# Govee Controller

Python scripts for controlling Govee H6008 smart LED lights over Bluetooth Low Energy and LAN.

I wanted to control my desk light programmatically. Govee's app is fine for tapping colors manually, but I needed scriptable control, specific RGB values, brightness levels, and the ability to trigger changes from other automation. So I reverse-engineered the protocols.

## How It Works

### BLE (Bluetooth Low Energy)
The `govee_ble.py` script communicates directly with the light using the `bleak` library. The protocol uses 20-byte packets: `0x33` header, command byte, payload, XOR checksum. Supports power on/off, RGB color, brightness (0-100%), color temperature, and named color presets.

### LAN (UDP Multicast)
The `govee_lan.py` script uses UDP multicast to `239.255.255.250:4001` with JSON-formatted commands. Faster and more reliable than BLE when both the light and your machine are on the same network. Not all Govee models support this, so BLE is the fallback.

## Scripts

| Script | Purpose |
|--------|---------|
| `govee_ble.py` | Full BLE controller with all commands |
| `govee_lan.py` | LAN API controller via UDP multicast |
| `set_color.py` | Quick script: power on, max brightness, set RGB |
| `set_green.py` / `set_yellow.py` | One-shot color presets |
| `clean_green.py` | Debug script: sets red first (to confirm comms work), waits 5s, then green |
| `map_channels.py` | Maps out available BLE characteristics |
| `debug_ble.py` | BLE connection diagnostics |

## Tech

Python, `bleak` (BLE), `asyncio`, `socket` (UDP multicast)

## Hardware

Built for the Govee H6008 LED light, but the BLE protocol is shared across many Govee models. The hardcoded device address in the scripts (`98:17:3C:21:E3:3F`) is my specific light. Change it to yours.
