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

# ── Wayland check ────────────────────────────────────────────────────
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    echo ""
    echo "  WARNING: You are on Wayland. Transparent overlays don't work here."
    echo "  To fix: Log out → click gear icon → select 'Ubuntu on Xorg' → log in"
    echo "  Then Ctrl+3 will work."
fi

# ── Auto-setup Ctrl+3 shortcut (GNOME) ───────────────────────────────
SHORTCUT_OK=""

if command -v gsettings &>/dev/null; then
    RESULT=$(python3 -c "
import subprocess as sp, ast
schema = 'org.gnome.settings-daemon.plugins.media-keys'
target_cmd = '$CMD'

# Check if already registered
cur = sp.run(['gsettings', 'get', schema, 'custom-keybindings'], capture_output=True, text=True).stdout.strip()
if cur.startswith('['):
    try:
        existing = ast.literal_eval(cur)
        for p in existing:
            cmd = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{p}', 'command'], capture_output=True, text=True).stdout.strip().strip(\"'\")
            if cmd == target_cmd:
                print('ALREADY_EXISTS')
                exit(0)
    except:
        pass

# Find free slot
for i in range(100):
    path = f'/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{i}/'
    r = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{path}', 'name'], capture_output=True, text=True)
    n = r.stdout.strip()
    if n in (\"''\", '@as []', '') or r.returncode != 0:
        sp.run(['gsettings', 'set', f'{schema}.custom-keybinding:{path}', 'name', 'Ghost Screen'])
        sp.run(['gsettings', 'set', f'{schema}.custom-keybinding:{path}', 'command', target_cmd])
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
    elif [ "$RESULT" = "ALREADY_EXISTS" ]; then
        SHORTCUT_OK=1
        echo "    Ctrl+3 shortcut already registered (skipped duplicate)."
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
