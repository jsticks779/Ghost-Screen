# Ghost Screen

An animated tech ghost overlay for your Linux desktop. Toggle it on/off with a
keyboard shortcut for a cyberpunk holographic screensaver effect.

## Features

- Full-screen animated tech ghost with rotating geometric core
- Circuit trace patterns, floating particles, scan lines, HUD brackets
- Toggle on/off — single command or keyboard shortcut
- Click anywhere or press Escape to dismiss
- Customizable colors, opacity, speed, and particle count
- Dark semi-transparent overlay over your desktop

## Requirements

- **Linux** with X11 (default on most distros — Wayland has limited transparency)
- **Python 3** — tkinter is auto-installed if missing

> **Wayland note**: log out and select "Ubuntu on Xorg" at login if transparency
> doesn't render correctly.

## Installation (one command — fully automatic)

```bash
git clone https://github.com/jsticks779/Ghost-Screen.git
cd Ghost-Screen
./install.sh
```

What `install.sh` does automatically:
- Installs `python3-tk` if missing
- Copies `ghost_screen.py` to `~/.local/bin/ghost-screen`
- Creates a desktop entry (shows in app menu)
- **Registers Ctrl+3 as a system-wide shortcut** (GNOME)
- Adds `~/.local/bin` to your `PATH` in `~/.bashrc`

After running it, **Ctrl+3** works immediately — no Settings menu needed.

### Manual installation (if you prefer)

```bash
mkdir -p ~/.local/bin ~/.local/share/applications
cp ghost_screen.py ~/.local/bin/ghost-screen
chmod +x ~/.local/bin/ghost-screen
```

Then set a keyboard shortcut in your DE's settings (see below).

## Keyboard Shortcut

### Ctrl+3 is set automatically on GNOME (Ubuntu default)

The install script registers it via `gsettings`. It persists across reboots.

### Manual setup (for other desktop environments)

| DE | Steps |
|----|-------|
| **KDE** | System Settings → Shortcuts → Custom Shortcuts → Edit → New → Global Shortcut → Command/URL → set to `~/.local/bin/ghost-screen` |
| **XFCE** | Settings → Keyboard → Application Shortcuts → Add → `~/.local/bin/ghost-screen` |
| **i3/Sway** | Add `bindsym Ctrl+3 exec ~/.local/bin/ghost-screen` to config |
| **Any** | Use your DE's "Custom Shortcut" feature with command `~/.local/bin/ghost-screen` |

## Usage

```bash
ghost-screen            # toggle on/off
ghost-screen --kill     # force stop
ghost-screen --version  # show version
```

The **only** way to dismiss the ghost is pressing your shortcut again (toggle off).

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

| Option         | Description                    | Default |
|----------------|--------------------------------|---------|
| `opacity`      | Window opacity (0–1)          | 0.88    |
| `frame_delay`  | ms per frame (lower = faster) | 33      |
| `particle_count`| Number of particles           | 60      |
| `ghost_scale`  | Ghost size (fraction of screen)| 0.28   |
| `float_amplitude`| Float motion (pixels)        | 30      |
| `rotation_speed`| Core rotation speed           | 0.02    |

## Uninstall

```bash
cd Ghost-Screen
./uninstall.sh
```

This removes the binary, desktop entry, and **also cleans up the Ctrl+3 shortcut**.

Or do it manually:

```bash
ghost-screen --kill
rm -f ~/.local/bin/ghost-screen
rm -f ~/.local/share/applications/ghost-screen.desktop
```

Remove the keyboard shortcut in **Settings → Keyboard → Shortcuts** if `uninstall.sh` didn't catch it.

## How It Works

`ghost_screen.py` creates a full-screen, transparent tkinter window over your
desktop. A **PID file** (`/tmp/ghost_screen.pid`) tracks whether the ghost is
already displayed — running the script again kills the existing instance
(toggle behavior). The ghost floats, rotates, pulses, and drifts particles at
~30 FPS. Only the shortcut toggles it off — no click or Escape.

## License

MIT
