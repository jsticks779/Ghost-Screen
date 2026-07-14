#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin"
APP="$HOME/.local/share/applications"
SCRIPT="ghost_screen.py"
NAME="ghost-screen"
CMD="$BIN/$NAME"

echo "==> Installing Ghost Screen..."

# ── Dependencies ──────────────────────────────────────────────────────
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "    python3-tk not found. Attempting to install..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3-tk || echo "    sudo failed — install python3-tk manually: sudo apt-get install python3-tk"
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm tk || echo "    sudo failed — install tk manually: sudo pacman -S tk"
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-tkinter || echo "    sudo failed — install manually: sudo dnf install python3-tkinter"
    else
        echo "    Please install python3-tk manually for your distro."
    fi
fi

# ── Install files ─────────────────────────────────────────────────────
mkdir -p "$BIN" "$APP"
cp "$DIR/$SCRIPT" "$CMD"
chmod +x "$CMD"

cat > "$APP/ghost-screen.desktop" << EOF
[Desktop Entry]
Name=Ghost Screen
Comment=Toggle tech ghost desktop overlay
Exec=$CMD
Terminal=false
Type=Application
Categories=Utility;
EOF
chmod +x "$APP/ghost-screen.desktop"

# ── Auto-setup Ctrl+3 shortcut (GNOME) ───────────────────────────────
SHORTCUT_OK=""

if command -v gsettings &>/dev/null; then
    RESULT=$(python3 -c "
import subprocess as sp
schema = 'org.gnome.settings-daemon.plugins.media-keys'
for i in range(100):
    path = f'/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{i}/'
    r = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{path}', 'name'], capture_output=True, text=True)
    n = r.stdout.strip()
    if n in (\"''\", '@as []', '') or r.returncode != 0:
        sp.run(['gsettings', 'set', f'{schema}.custom-keybinding:{path}', 'name', 'Ghost Screen'])
        sp.run(['gsettings', 'set', f'{schema}.custom-keybinding:{path}', 'command', '$CMD'])
        sp.run(['gsettings', 'set', f'{schema}.custom-keybinding:{path}', 'binding', '<Primary>3'])
        cur = sp.run(['gsettings', 'get', schema, 'custom-keybindings'], capture_output=True, text=True).stdout.strip()
        if cur in ('@as []', '[]'):
            sp.run(['gsettings', 'set', schema, 'custom-keybindings', f\"['{path}']\"])
        else:
            sp.run(['gsettings', 'set', schema, 'custom-keybindings', cur[:-1] + f\", '{path}']\"])
        print('OK')
        exit(0)
print('NO_SLOT')
" 2>&1)
    if [ "$RESULT" = "OK" ]; then
        SHORTCUT_OK=1
    fi
fi

# ── PATH check ────────────────────────────────────────────────────────
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$BIN" 2>/dev/null; then
    LINE='export PATH="$HOME/.local/bin:$PATH"'
    if ! grep -qxF "$LINE" "$HOME/.bashrc" 2>/dev/null; then
        echo "$LINE" >> "$HOME/.bashrc"
        echo "    Added $BIN to PATH in ~/.bashrc"
    fi
fi

# ── Done ──────────────────────────────────────────────────────────────
echo ""
echo "  Ghost Screen installed!"
echo ""

if [ -n "$SHORTCUT_OK" ]; then
    echo "  Press  Ctrl+3  to toggle the ghost on/off"
else
    echo "  Run: $NAME  (or set a keyboard shortcut in Settings)"
fi
echo "  Kill: $NAME --kill"
echo ""
