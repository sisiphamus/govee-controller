# govee-controller

Reverse-engineered protocol control for Govee H6008 LED lights, because tapping colors in an app is fine until you want your lights to change programmatically.

The BLE protocol speaks in 20-byte packets: `0x33` header, a command byte that tells the light what you want (power, color, brightness, color temp, scene presets), your payload, and an XOR checksum across the whole thing. `govee_ble.py` handles all of this over Bluetooth using the `bleak` library. `govee_lan.py` does the same job over the local network -- UDP multicast to `239.255.255.250:4001` carrying JSON commands -- which is noticeably faster when your machine is on the same subnet.

Then there are the single-purpose scripts, and honestly this is where it gets practical. `set_green.py`, `set_yellow.py`, `set_color.py` -- these exist because when Pepper needs to signal something with the room lighting, it doesn't need to understand Govee's protocol. It just needs to run a script.

`map_channels.py` figures out which BLE characteristics actually accept write commands. `debug_ble.py` is for when things go sideways, which with BLE is more often than anyone admits.

The MAC address `98:17:3C:21:E3:3F` is hardcoded because this controls one specific light in one specific room. If you're adapting this, that's the first thing you'll change.
