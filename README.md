<p align="center">
  <img src="logo.svg" alt="GHOSTSCREEN" width="580">
</p>

<p align="center">
  An animated tech ghost overlay for <strong>Linux & Windows</strong>.<br>
  Toggle on/off with <kbd>Ctrl</kbd>+<kbd>3</kbd> for a cyberpunk holographic screensaver effect.
</p>

## Features

- Full-screen animated tech ghost with rotating geometric core
- Circuit trace patterns, floating particles, scan lines, HUD brackets
- **Cross-platform** — Linux (X11, Wayland) + Windows
- **Works on every Linux compositor** — GNOME, KDE, XFCE, Sway, Hyprland, River, COSMIC, Deepin, LXQt
- **Full input blocking** while active — keyboard, mouse, touch — on every platform
- **Blocks sleep + screen blanking** — toggle off to allow sleep
- Survives sleep/wake — window auto-restarts on all backends
- Customizable colors, opacity, speed, and particle count

## Installation

### Linux

```bash
# Recommended — one command
curl -fsSL https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/install.sh | bash

# Or via npm
npm install -g ghost-screen

# Or via git
git clone https://github.com/jsticks779/Ghost-Screen.git
cd Ghost-Screen
./install.sh
```

> You'll be prompted for `sudo` — needed for system packages and input blocking. Takes ~20 seconds.

### Windows

Open **PowerShell as Administrator** and paste:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force; iex ((New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/install.ps1'))
```

Or from **Command Prompt**:

```cmd
powershell -Command "iex ((New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/install.ps1'))"
```

Or install manually:

```powershell
curl -fsSL -o ghost_screen.py https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/ghost_screen.py
python ghost_screen.py
```

---

| Platform | Backend | Required Packages |
|----------|---------|-------------------|
| Linux X11 | `tkinter` | `python3-tk` |
| Linux Wayland | GTK3 + Pillow | `python3-gi`, `gir1.2-gtk-3.0`, `python3-pil` |
| Windows | tkinter + ctypes | Built into Python — no extra dependencies |

After installing, press **Ctrl+3** to toggle the ghost on/off.

## Usage

```
ghost-screen                         toggle on/off
ghost-screen --kill                  force stop
ghost-screen --version               show version
ghost-screen --check                 verify dependencies
ghost-screen --shortcut "COMBO"      change keyboard shortcut
ghost-screen --autostart enable      launch on login
ghost-screen --autostart disable     remove from autostart
ghost-screen --autostart status      check autostart status
ghost-screen --idle 10               screensaver mode (activate after 10min idle)
```

The **only** way to dismiss the ghost is pressing your shortcut again.

### Sleep behavior

While active, sleep + screen blanking are blocked automatically:

- **Windows**: `SetThreadExecutionState(ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)` — no dependencies needed
- **Linux**: multi-backend — logind D-Bus → GNOME Session Manager → freedesktop PowerManagement → `systemd-inhibit` CLI

All locks release on toggle-off or `--kill`.

## Keyboard Shortcut

**Ctrl+3** is registered automatically during install. To change it:

```bash
ghost-screen --shortcut "Ctrl+Shift+G"
ghost-screen --shortcut "Super+F1"
```

The change persists across reboots. Works on GNOME, KDE, XFCE, Sway, Hyprland, River, Deepin, LXQt.

### Manual setup per desktop

| Desktop | Steps |
|---------|-------|
| **GNOME** | Settings → Keyboard → Shortcuts → + → Name: `Ghost Screen` → Command: `~/.local/bin/ghost-screen` → Ctrl+3 |
| **KDE** | System Settings → Shortcuts → Custom Shortcuts → Edit → New → Global Shortcut → Command/URL → `~/.local/bin/ghost-screen` |
| **XFCE** | Settings → Keyboard → Application Shortcuts → Add → `~/.local/bin/ghost-screen` |
| **Sway** | `bindsym Ctrl+3 exec ~/.local/bin/ghost-screen` |
| **Hyprland** | `bind = Ctrl, 3, exec, ~/.local/bin/ghost-screen` |
| **River** | `riverctl map normal Ctrl 3 spawn "~/.local/bin/ghost-screen" &` |
| **Windows** | Shortcut is handled internally via a low-level keyboard hook (`WH_KEYBOARD_LL`) — no desktop setup needed |

## Customization

Create `ghost_screen.json` next to the script or in `~/.config/ghost-screen/`:

```json
{
  "opacity": 0.85,
  "frame_delay": 33,
  "particle_count": 80,
  "ghost_scale": 0.30,
  "colors": {
    "primary": "#00fff7",
    "secondary": "#ff0088",
    "accent": "#4488ff",
    "particle": "#aa44ff",
    "ghost_fill": "#08081a",
    "ghost_outline": "#00fff7",
    "bg": "#050510",
    "grid": "#151530",
    "glow": "#00fff7"
  }
}
```

| Option | Description | Default |
|--------|-------------|---------|
| `opacity` | Window opacity (0–1) | 0.88 |
| `frame_delay` | ms per frame (lower = faster) | 33 |
| `particle_count` | Number of particles | 60 |
| `ghost_scale` | Ghost size (fraction of screen) | 0.28 |
| `float_amplitude` | Float motion (pixels) | 30 |
| `rotation_speed` | Core rotation speed | 0.02 |

## Uninstall

### Linux

```bash
curl -fsSL https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/uninstall.sh | bash
npm uninstall -g ghost-screen   # if installed via npm
```

### Windows

```powershell
Remove-Item -Recurse "$env:LOCALAPPDATA\GhostScreen"
```

## How It Works

`ghost_screen.py` auto-detects your platform and picks the right backend:

| Platform | Backend | Window | Input Blocking | Sleep Lock |
|----------|---------|--------|----------------|------------|
| **Windows** | `tkinter` + `ctypes` | Fullscreen overlay with `overrideredirect` | `WH_KEYBOARD_LL` / `WH_MOUSE_LL` hooks | `SetThreadExecutionState` |
| **Linux (Wayland)** | GTK3 + Pillow | RGBA visual → GdkPixbuf | `zwp_keyboard_shortcuts_inhibit` + seat grab + kernel sysfs | D-Bus logind → systemd-inhibit |
| **Linux (X11)** | `tkinter` | Fullscreen `-alpha` canvas | `grab_set_global()` | D-Bus logind → systemd-inhibit |

All backends render the same cyberpunk ghost animation:

1. **Ghost silhouette** — polygon outline with circuit trace paths
2. **Rotating core** — octagonal geometric center with pulsing eyes
3. **Particles** — floating embers with twinkle effect
4. **HUD overlay** — corner brackets, scan lines, animated grid
5. **Vignette** — dark edges for depth

A **PID file** (`/tmp/ghost_screen.pid` on Linux, `$env:TEMP\ghost_screen.pid` on Windows) tracks whether the ghost is running — invoking the command again toggles it off. Only the toggle shortcut dismisses it — no click, no Escape.

## License

MIT
