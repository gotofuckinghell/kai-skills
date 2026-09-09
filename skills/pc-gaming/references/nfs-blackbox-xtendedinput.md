# NFS Black Box XtendedInput — Keybinding Configuration

Applies to: NFS Most Wanted (2005), Carbon, ProStreet, Undercover

## The Problem

In-game control remapping menu freezes when clicking an action — the modal input listener never receives a valid key event and blocks forever. Game engine keeps running (music, animations) but the UI layer is stuck.

## Root Cause

The game enters a blocking `GetKeyPress()` loop with no timeout, no cancel handler. Escape doesn't work because the listener is waiting for a specific DirectInput/XInput event and ignores everything else. Known bug in all Black Box PC ports.

## Solution: Bypass In-Game Menu — Edit Config Directly

Install **NFS-XtendedInput** plugin (`dinput8.dll` + `NFS_XtendedInput.asi` in game folder). It takes over all input handling and reads keybinds from `.ini` files in `scripts/`.

### File Locations

| File | Purpose |
|------|---------|
| `scripts/NFS_XtendedInput.ini` | Plugin settings (keyboard mode, omni mode, deadzones) |
| `scripts/NFS_XtendedInput.default.ini` | Default bindings, used as fallback on profile reset |
| `scripts/XtendedInputMaps/<profile_id>/NFS_XtendedInput.usermap.ini` | **Your actual keybinds** — edit this |

Profile ID is internal (e.g., `123`). Look for existing subdirectories in `XtendedInputMaps/`.

### Widescreen Fix Interaction

ThirteenAG's Widescreen Fix also has input tweaks (`NFSCarbon.WidescreenFix.ini`):
```ini
ImproveGamepadSupport = 0   ; Set to 0 to disable XInput gamepad icons/input
ExpandControllerOptions = 0  ; Keep 0 — toggling to 1 crashes existing profiles
```

### Key Naming Convention (EventsKB section)

Three key formats in `[EventsKB]`:

| Format | Examples | When |
|--------|----------|------|
| `VK_CODE` | `VK_UP`, `VK_DOWN`, `VK_LEFT`, `VK_RIGHT`, `VK_SPACE`, `VK_RETURN`, `VK_ESCAPE`, `VK_LSHIFT`, `VK_RSHIFT`, `VK_LCONTROL`, `VK_RCONTROL`, `VK_MENU`, `VK_TAB`, `VK_BACK`, `VK_SUBTRACT` | Arrow keys, modifiers, special keys |
| `LETTER` | `W`, `A`, `S`, `D`, `R`, `X`, `C`, `L`, `P`, `T`, `B`, `M`, `F`, `I`, `J`, `K` | Letter keys (uppercase) |
| `NUMBER` | `0`, `1`, `2`, `3`, `5`, `9` | Number row (not NumPad) |

Reference for VK codes: http://cherrytree.at/misc/vk.htm (decimal values)

### Complete Action List — NFS Carbon

```
[EventsKB]

; --- Menu / Frontend ---
FRONTENDACTION_UP = VK_UP
FRONTENDACTION_DOWN = VK_DOWN
FRONTENDACTION_LEFT = VK_LEFT
FRONTENDACTION_RIGHT = VK_RIGHT
FRONTENDACTION_ACCEPT = VK_RETURN
FRONTENDACTION_CANCEL = VK_ESCAPE
FRONTENDACTION_RUP = W              ; right-stick up in menus
FRONTENDACTION_RDOWN = S
FRONTENDACTION_RLEFT = A
FRONTENDACTION_RRIGHT = D
FRONTENDACTION_BUTTON0 = 5         ; extra menu buttons
FRONTENDACTION_BUTTON1 = 3
FRONTENDACTION_BUTTON2 = T
FRONTENDACTION_BUTTON3 = R
FRONTENDACTION_BUTTON4 = 2
FRONTENDACTION_BUTTON5 = 1
FRONTENDACTION_LTRIGGER = 9
FRONTENDACTION_RTRIGGER = 0
FRONTENDACTION_START = VK_SPACE

; --- Driving ---
GAMEACTION_GAS = VK_UP
GAMEACTION_BRAKE = VK_DOWN
GAMEACTION_STEERLEFT = VK_LEFT
GAMEACTION_STEERRIGHT = VK_RIGHT
GAMEACTION_TURNLEFT = VK_LEFT       ; duplicate of steer
GAMEACTION_TURNRIGHT = VK_RIGHT
GAMEACTION_HANDBRAKE = VK_SPACE
GAMEACTION_NOS = VK_MENU            ; Alt
GAMEACTION_GAMEBREAKER = X          ; Speedbreaker
GAMEACTION_SHIFTUP = VK_LSHIFT
GAMEACTION_SHIFTDOWN = VK_LCONTROL
GAMEACTION_RESET = R                ; reset car position

; --- Crew Commands (hold Right Ctrl + direction) ---
GAMEACTION_CREWAGGRESSIVE = VK_RCONTROL
GAMEACTION_CREWDEFENSIVE = VK_RCONTROL
GAMEACTION_CREWDEFAULT = VK_RCONTROL
GAMEACTION_CREWSPEED = VK_RCONTROL

; --- HUD ---
HUDACTION_PAUSEREQUEST = VK_ESCAPE
HUDACTION_ENGAGE_EVENT = VK_RETURN
HUDACTION_PAD_LEFT = M
HUDACTION_PAD_RIGHT = VK_TAB
HUDACTION_PAD_DOWN = B
HUDACTION_SKIPNIS = VK_RETURN        ; skip cutscene

; --- Camera ---
CAMERAACTION_CHANGE = C
CAMERAACTION_LOOKBACK = L
CAMERAACTION_PULLBACK = P

; --- Debug Camera ---
CAMERAACTION_DEBUG = VK_SUBTRACT
DEBUGACTION_DROPCAR = 5
DEBUGACTION_MOVE_FORWARD = W
DEBUGACTION_MOVE_BACK = S
DEBUGACTION_MOVE_LEFT = A
DEBUGACTION_MOVE_RIGHT = D
DEBUGACTION_MOVE_UP = VK_SPACE
DEBUGACTION_MOVE_DOWN = VK_LCONTROL
DEBUGACTION_LOOK_UP = K
DEBUGACTION_LOOK_DOWN = I
DEBUGACTION_LOOK_LEFT = J
DEBUGACTION_LOOK_RIGHT = L
DEBUGACTION_TURBO = VK_LSHIFT
DEBUGACTION_SUPER_TURBO = F
```

### Key Settings in NFS_XtendedInput.ini

```ini
[Input]
KeyboardReadingMode = 1       ; 0=async unbuffered, 1=buffered (recommended)
XInputOmniMode = 0            ; 0=one XInput port, 1=reads all 4 ports
PassConnStatus = 0            ; set to 0 to disable controller-connect detection
FirstControlDevice = 0        ; 0=Keyboard, 1=Controller
```

### Workflow

1. Disable `ImproveGamepadSupport` in WidescreenFix.ini (set to 0).
2. Set `FirstControlDevice = 0` in NFS_XtendedInput.ini.
3. Edit `usermap.ini` directly with desired binds.
4. Launch game — no need to touch in-game control menu.

Changes take effect immediately on next launch. No in-game menu interaction needed.