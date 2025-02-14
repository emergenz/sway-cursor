#!/usr/bin/env python3
import time, math, subprocess, select, os, fcntl
from evdev import InputDevice, ecodes, list_devices

# Map movement keys: h (left), j (down), k (up), l (right)
KEY_MAP = {
    ecodes.KEY_H: (-1, 0),
    ecodes.KEY_J: (0, 1),
    ecodes.KEY_K: (0, -1),
    ecodes.KEY_L: (1, 0),
}
# Define modifier keys; adjust these if your mod is different.
MOD_KEYS = {ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA}  # assumed mod
CTRL_KEYS = {ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL}

# Find all devices with key capabilities.
devices = [InputDevice(path) for path in list_devices()]
kbd_devices = []
for dev in devices:
    caps = dev.capabilities()
    if ecodes.EV_KEY in caps:
        kbd_devices.append(dev)
        try:
            dev.set_nonblocking(True)
        except AttributeError:
            fd = dev.fd
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

# Track key states.
keys = {code: False for code in list(KEY_MAP.keys()) + list(MOD_KEYS) + list(CTRL_KEYS)}

# Acceleration parameters.
base_speed = 10.0  # pixels per second
accel = 5000.0  # pixels per second^2
dt_loop = 0.01  # seconds per update

accum_x = 0.0
accum_y = 0.0
hold_time = 0.0
last = time.monotonic()

while True:
    now = time.monotonic()
    dt = now - last
    last = now

    # Poll devices for key events.
    r, _, _ = select.select(kbd_devices, [], [], 0)
    for dev in r:
        try:
            for event in dev.read():
                if event.type == ecodes.EV_KEY:
                    keys[event.code] = event.value != 0
        except Exception:
            continue

    # Only run when both modifiers are pressed.
    if not (
        any(keys.get(k, False) for k in MOD_KEYS)
        and any(keys.get(k, False) for k in CTRL_KEYS)
    ):
        hold_time = 0.0
        accum_x = accum_y = 0.0
        time.sleep(dt_loop)
        continue

    # Sum movement contributions.
    dx = dy = 0
    for k, vec in KEY_MAP.items():
        if keys.get(k, False):
            dx += vec[0]
            dy += vec[1]

    if dx == 0 and dy == 0:
        hold_time = 0.0
        accum_x = accum_y = 0.0
        time.sleep(dt_loop)
        continue

    # Normalize so diagonal movement isn’t faster.
    mag = math.hypot(dx, dy)
    nx, ny = dx / mag, dy / mag

    hold_time += dt
    speed = base_speed + accel * hold_time  # current speed in pixels/sec
    dist = speed * dt  # pixels to move this frame
    move_x = nx * dist
    move_y = ny * dist

    # Accumulate fractional movement.
    accum_x += move_x
    accum_y += move_y
    int_x = int(round(accum_x))
    int_y = int(round(accum_y))
    if int_x or int_y:
        subprocess.run(
            ["swaymsg", "--", "seat", "-", "cursor", "move", str(int_x), str(int_y)]
        )
        accum_x -= int_x
        accum_y -= int_y

    time.sleep(dt_loop)
