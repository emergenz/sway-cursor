# sway-cursor

[![License](https://img.shields.io/github/license/emergenz/sway-cursor)](https://github.com/emergenz/sway-cursor/blob/main/LICENSE)
`sway-cursor` enables you to control the mouse cursor with your keyboard. `sway-cursor` internally uses the sway-native way of controlling the cursor. `sway-cursor` exists because configuring keyboard-driven mouse movement directly inside of your sway config leads to unsatisfying behaviour. Most importantly, there is no 'pointer acceleration' and no straightforward way of getting there via simple scripts. `sway-cursor` is a simple python daemon that simply lets you control the mouse cursor with your keyboard and behaves as you would expect: Pointer-acceleration is natively supported, holding two adjacent directions moves the cursor diagonally, and the cursor movement is *totally smooth*™.

## Installation
Simply clone the repository, install the sole dependency, and run the script in the background.

```bash
git clone https://github.com/emergenz/sway-cursor
pip3 install evdev
python3 sway_cursor.py
```

I recommend executing the script at the end of your sway config for convenience:
```
exec_always --no-startup-id python3 <PATH_TO_THIS_REPO>/sway_cursor.py &
```
## Configuration
The bindings are configured in the python script itself. Yes, this is not the default way of configuring bindings in sway, but after careful consideration, I decided that this was the lesser evil.

```python
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
```

Additionally, you have to shadow the same keybindings in your sway config with dummy commands such that sway does not pass those bindings down to applications.
```
bindsym $mod+Ctrl+k seat - cursor move 0 0
bindsym $mod+Ctrl+j seat - cursor move 0 0
bindsym $mod+Ctrl+h seat - cursor move 0 0
bindsym $mod+Ctrl+l seat - cursor move 0 0
```
