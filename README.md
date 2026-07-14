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

- Linux with X11 (default on most distros)
- Python 3 with **tkinter** (usually pre-installed; try `python3 -m tkinter`)
- `~/.local/bin` in your `PATH` (add it: `export PATH="$HOME/.local/bin:$PATH"`)

> **Wayland note**: transparency effects are limited on Wayland. Log out and
> select the "Ubuntu on Xorg" session if things don't render correctly.

## Installation

```bash
git clone https://github.com/jsticks779/Ghost-Screen.git
cd Ghost-Screen
chmod +x install.sh
./install.sh
```

Or install manually:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications
cp ghost_screen.py ~/.local/bin/ghost-screen
chmod +x ~/.local/bin/ghost-screen
```

## Setting Up a Keyboard Shortcut

### GNOME (Ubuntu default)

The `install.sh` script tries to register **Ctrl+3** automatically. If it fails,
or you want a different key:

1. **Settings → Keyboard → Keyboard Shortcuts**
2. Scroll to the bottom → click **+**
3. **Name**: `Ghost Screen` • **Command**: `~/.local/bin/ghost-screen`
4. **Set Shortcut** → press your preferred key combination

### KDE

**System Settings → Shortcuts → Custom Shortcuts → Edit → New → Global Shortcut → Command/URL**

Set trigger to your key combination and action to `~/.local/bin/ghost-screen`.

## Usage

```bash
ghost-screen            # toggle on/off
ghost-screen --kill     # force stop
ghost-screen --version  # show version
```

Click anywhere on the overlay or press **Escape** to dismiss.

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
chmod +x uninstall.sh
./uninstall.sh
```

Or manually:

```bash
ghost-screen --kill
rm -f ~/.local/bin/ghost-screen
rm -f ~/.local/share/applications/ghost-screen.desktop
```

Remove the keyboard shortcut in **Settings → Keyboard → Shortcuts** if you set one.

## How It Works

`ghost_screen.py` creates a full-screen, transparent tkinter window over your
desktop. A **PID file** (`/tmp/ghost_screen.pid`) tracks whether the ghost is
already displayed — running the script again kills the existing instance
(toggle behavior). The ghost floats, rotates, pulses, and drifts particles at
~30 FPS. Click, Escape, or the shortcut dismisses it.

## License

MIT
