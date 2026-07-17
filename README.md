<p align="center">
  <img src="logo.svg" alt="GHOSTSCREEN" width="580">
</p>

An animated tech ghost overlay for **any Linux desktop**. Toggle it on/off with
Ctrl+3 for a cyberpunk holographic screensaver effect.

## Features

- Full-screen animated tech ghost with rotating geometric core
- Circuit trace patterns, floating particles, scan lines, HUD brackets
- Toggle on/off — same shortcut or command
- **Works on every Linux compositor** — X11, Wayland (GNOME/KDE/Sway/Hyprland/River/COSMIC/Deepin/LXQt)
- **Auto-transparent on Wayland** — composited with Pillow + GdkPixbuf (no Cairo GI needed)
- **Survives sleep/wake** — window auto-restarts after suspend on both backends
- **Blocks PC sleep + screen blanking** while ghost is active — toggle off to allow sleep
- Auto-darkens on X11 with tkinter (also works on XWayland as a fallback)
- Customizable colors, opacity, speed, and particle count
- Dark semi-transparent overlay over your desktop
- **Full input blocking** while ghost is active — keyboard, mouse, touchpad, touchscreen — on **every Linux compositor**

## Requirements

- **Linux desktop** — X11 and Wayland are the only two display servers; auto-detected
- **Python 3** — deps installed automatically by `install.sh`

| Display | Backend          | Required Packages                       |
|---------|------------------|-----------------------------------------|
| X11     | tkinter          | `python3-tk`                            |
| Wayland | GTK3 + Pillow    | `python3-gi`, `gir1.2-gtk-3.0`, `python3-pil` |
| Wayland (inhibitor) | C shared library | `gcc`, `pkg-config`, `wayland-scanner` (auto-built by install.sh) |

## Installation (one command — fully automatic)

```bash
git clone https://github.com/jsticks779/Ghost-Screen.git
cd Ghost-Screen
./install.sh
```

**You'll be prompted for `sudo`** — the script needs it to install system
packages and set up the SUID helper for input blocking. Full install takes
~20 seconds.

The install script auto-detects **everything**:

| What | How it's detected |
|------|-------------------|
| **Root vs user** | Installs to `/usr/local/bin` (root) or `~/.local/bin` (user) |
| **Package manager** | `apt` / `pacman` / `dnf` / `zypper` / `apk` / `xbps` |
| **Display server** | `XDG_SESSION_TYPE` — X11 or Wayland |
| **Desktop environment** | `XDG_CURRENT_DESKTOP` — GNOME, KDE, XFCE, Sway, Hyprland, River, Deepin, LXQt |
| **Shell config** | Adds `PATH` to `.bashrc`, `.zshrc`, `.profile` |
| **Pillow fallback** | If system package missing → tries `pip3 install Pillow` |

### Shortcut auto-registration:

| Desktop       | Method |
|---------------|--------|
| **GNOME** / Budgie / Cinnamon / MATE | `gsettings` |
| **KDE Plasma** | `kwriteconfig5` + `qdbus` |
| **XFCE** | `xfconf-query` |
| **Sway** | Appends to `~/.config/sway/config` |
| **Hyprland** | Appends to `~/.config/hypr/hyprland.conf` |
| **River** | Appends to `~/.config/river/init` |
| **COSMIC** | Detected; `--shortcut` not yet supported (set manually) |
| **Deepin** | `gsettings` |
| **LXQt** | Appends to `~/.config/lxqt/globalkeyshortcuts.conf` |
| **Other X11** | `xbindkeys` universal fallback |
| **Other Wayland** | Best-effort; manual setup if needed |

After running it, **Ctrl+3** works immediately — no Settings menu needed.

> **Note:** Manual install is **not recommended** — the C helpers (`wl_inhibit.so`,
> `ghost-touch-inhibit`) must be compiled and SUID must be set, else keyboard
> shortcuts and touch input won't be blocked. Always use `./install.sh`.

## Usage

```bash
ghost-screen                    # toggle on/off
ghost-screen --kill             # force stop
ghost-screen --version          # show version
ghost-screen --check            # verify dependencies
ghost-screen --shortcut "COMBO" # change keyboard shortcut
```

The **only** way to dismiss the ghost is pressing your shortcut again (toggle off).

### Sleep / suspend behavior

While the ghost is active, **PC sleep + screen blanking are blocked**
automatically. A multi-backend inhibitor tries every available protocol:

- **logind** (D-Bus): system suspend — works on any systemd/elogind Linux
- **GNOME Session Manager**: screen blanking, lock, and suspend
- **freedesktop PowerManagement**: screen blanking and idle suspend
  (KDE, XFCE, MATE, LXQt)
- **systemd-inhibit CLI**: fallback on all systemd systems

The ghost survives suspend/resume on both backends — if the window is
destroyed during sleep, the process detects it and recreates it.

## Keyboard Shortcut

### Ctrl+3 is set automatically — any desktop

The install script detects your environment and registers **Ctrl+3** without
you lifting a finger. It persists across reboots.

### Manual setup (if needed)

| DE/WM                | Steps |
|----------------------|-------|
| **GNOME**            | Settings → Keyboard → Shortcuts → + → Name: `Ghost Screen` → Command: `~/.local/bin/ghost-screen` → Set Shortcut: Ctrl+3 |
| **KDE**              | System Settings → Shortcuts → Custom Shortcuts → Edit → New → Global Shortcut → Command/URL → set to `~/.local/bin/ghost-screen` |
| **XFCE**             | Settings → Keyboard → Application Shortcuts → Add → `~/.local/bin/ghost-screen` |
| **Sway**             | Add `bindsym Ctrl+3 exec ~/.local/bin/ghost-screen` to config |
| **Hyprland**         | Add `bind = Ctrl, 3, exec, ~/.local/bin/ghost-screen` to config |
| **River**            | Add `riverctl map normal Ctrl 3 spawn ~/.local/bin/ghost-screen &` to config |
| **COSMIC**           | Settings → Keyboard → Shortcuts → + → set to `~/.local/bin/ghost-screen` |
| **Deepin**           | Settings → Keyboard → Shortcuts → + → same as GNOME |
| **LXQt**             | Add to `~/.config/lxqt/globalkeyshortcuts.conf` or use GUI |
| **Any**              | Use your DE/WM's custom shortcut feature with command `~/.local/bin/ghost-screen` |

### Change shortcut any time — no reinstall needed

After installing, your shortcut is **Ctrl+3** by default. To pick your own:

```bash
ghost-screen --shortcut "Ctrl+Shift+G"
ghost-screen --shortcut "Super+F1"
ghost-screen --shortcut "Ctrl+Alt+T"
```

**How it works:**

1. Run `ghost-screen --shortcut "Ctrl+Shift+G"`
2. The script detects your desktop environment (GNOME, KDE, XFCE, etc.)
3. It translates `Ctrl+Shift+G` into the format your DE expects
   (e.g. GNOME → `<Control><Shift>g`, Sway → `Ctrl+Shift+g`)
4. It finds your existing Ghost Screen shortcut and updates its key binding
   — or creates a new entry if none exists
5. The new combo is saved to `~/.config/ghost-screen/shortcut.json`

The change is immediate and persists across reboots. No menus, no re-running
the installer. Works on GNOME, KDE, XFCE, Sway, Hyprland, River, Deepin,
LXQt, and falls back to xbindkeys on other X11 desktops.

## Customization

Create a `ghost_screen.json` file next to the script:

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

| Option           | Description                           | Default |
|------------------|---------------------------------------|---------|
| `opacity`        | Window opacity (0–1)                 | 0.88    |
| `frame_delay`    | ms per frame (lower = faster)        | 33      |
| `particle_count` | Number of particles                  | 60      |
| `ghost_scale`    | Ghost size (fraction of screen)      | 0.28    |
| `float_amplitude`| Float motion (pixels)                | 30      |
| `rotation_speed` | Core rotation speed                  | 0.02    |

## Uninstall

```bash
cd Ghost-Screen
./uninstall.sh
```

This removes the binary (from both `/usr/local/bin` and `~/.local/bin`),
desktop entry, **and cleans up the Ctrl+3 shortcut** from all desktop
environments and wlroots configs.

Or do it manually:

```bash
ghost-screen --kill
rm -f ~/.local/bin/ghost-screen
rm -f ~/.local/share/applications/ghost-screen.desktop
```

Remove the keyboard shortcut in **Settings → Keyboard → Shortcuts** if
`uninstall.sh` didn't catch it.

## How It Works

`ghost_screen.py` auto-detects your display server and picks the right backend:

- **Wayland** → GTK3 window with RGBA visual, renders each frame with Pillow,
  converts to `GdkPixbuf`, displays on a `Gtk.Image` — fully transparent
  background with no Cairo GI dependency
- **X11** → tkinter window with `-alpha` for transparency, draws with the
  tkinter canvas API

Both backends **auto-restart the window** if it's destroyed (suspend, screen
lock, display reconfig). The process stays alive until explicitly killed with
`--kill` or the toggle shortcut.

**Input is blocked while the ghost is active.** You cannot click, type,
touch the screen, or interact with anything underneath. The toggle shortcut
is detected internally (no compositor shortcut needed to dismiss).

| Backend | Mechanism | Blocks |
|---------|-----------|--------|
| **Tkinter (X11)** | `grab_set_global()` — X11 global grab | Everything, including WM key bindings |
| **GTK3 (Wayland, keyboard)** | `zwp_keyboard_shortcuts_inhibit_manager_v1` via C `.so` | Super key, Alt+Tab, all compositor keyboard shortcuts |
| **GTK3 (Wayland, touch devices)** | SUID C helper inhibits kernel `input` device (`inhibited` sysfs) | Touchpad + touchscreen gestures, scroll, tap, cursor — **every Linux** |
| **GTK3 (Wayland, client)** | `Gdk.Seat.grab()` seat grab | Mouse clicks, keyboard typing, pointer motion |

On **Wayland**, the ghost uses a multi-layer approach:
1. **C shared library** binds `zwp_keyboard_shortcuts_inhibit_manager_v1` to block compositor keyboard shortcuts
2. **SUID C helper** inhibits all touch input devices at the kernel-level via sysfs (`/sys/class/input/eventN/device/inhibited`) — works on **any Wayland compositor**, not DE-specific
3. **Gdk.Seat.grab** + event handlers capture all client-level input (keyboard, mouse, touch)

A **PID file** (`/tmp/ghost_screen.pid`) tracks whether the ghost is already
displayed — running the script again kills the existing instance (toggle
behavior). The ghost floats, rotates, pulses, and drifts particles at ~30 FPS.
Only the shortcut toggles it off — no click or Escape.

The script acquires a sleep + idle lock while the ghost is active, preventing
the PC from suspending or the screen from blanking. Three backends are tried
in order (logind → GNOME Session → freedesktop PowerManagement), with a
`systemd-inhibit` CLI fallback. All locks are released automatically on
toggle-off or `--kill`.

## License

MIT
