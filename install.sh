#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin"
APP="$HOME/.local/share/applications"
AUTOSTART="$HOME/.config/autostart"
SCRIPT="ghost_screen.py"
NAME="ghost-screen"
CMD="$BIN/$NAME"

echo "==> Installing Ghost Screen..."

# ── Dependencies ──────────────────────────────────────────────────────
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    if ! python3 -c "import gi; gi.require_version('Gtk','3.0'); gi.require_version('cairo','1.0'); from gi.repository import Gtk, cairo" 2>/dev/null; then
        echo "    GTK3 not found (required for Wayland). Installing..."
        if command -v apt-get &>/dev/null; then
            sudo apt-get install -y python3-gi gir1.2-gtk-3.0 || echo "    Could not install GTK3"
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm python-gobject gtk3 || echo "    Could not install GTK3"
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3-gobject gtk3 || echo "    Could not install GTK3"
        fi
    fi
else
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo "    python3-tk not found. Attempting to install..."
        if command -v apt-get &>/dev/null; then
            sudo apt-get install -y python3-tk || echo "    Could not install python3-tk"
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm tk || echo "    Could not install tk"
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3-tkinter || echo "    Could not install python3-tkinter"
        fi
    fi
fi

# ── Install files ─────────────────────────────────────────────────────
mkdir -p "$BIN" "$APP" "$AUTOSTART"
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

# ── Wayland check ─────────────────────────────────────────────────────
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    echo "    Wayland detected — using GTK3 backend for transparency."
fi

# ── Try each desktop environment ──────────────────────────────────────
SHORTCUT_OK=""

setup_xbindkeys() {
    if ! command -v xbindkeys &>/dev/null; then
        if command -v apt-get &>/dev/null; then
            sudo apt-get install -y xbindkeys 2>/dev/null || return 1
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm xbindkeys 2>/dev/null || return 1
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y xbindkeys 2>/dev/null || return 1
        else
            return 1
        fi
    fi

    cat > "$HOME/.xbindkeysrc" << XEOF
"$CMD"
    Control+3
XEOF

    cat > "$AUTOSTART/xbindkeys.desktop" << XEOF
[Desktop Entry]
Type=Application
Name=xbindkeys
Comment=Global keyboard shortcuts (Ghost Screen)
Exec=xbindkeys
Terminal=false
XEOF

    xbindkeys 2>/dev/null || true
    return 0
}

setup_gnome() {
    command -v gsettings &>/dev/null || return 1
    python3 -c "
import subprocess as sp, ast
schema = 'org.gnome.settings-daemon.plugins.media-keys'
target = '$CMD'

cur = sp.run(['gsettings', 'get', schema, 'custom-keybindings'], capture_output=True, text=True).stdout.strip()
existing = ast.literal_eval(cur) if cur.startswith('[') else []

# Remove duplicates, keep only first match
found = False
keep = []
for p in existing:
    cmd = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{p}', 'command'], capture_output=True, text=True).stdout.strip().strip(\"'\")
    if cmd == target:
        if found:
            sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', 'name'])
            sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', 'command'])
            sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', 'binding'])
            continue
        found = True
    keep.append(p)

if found:
    sp.run(['gsettings', 'set', schema, 'custom-keybindings', str(keep)])
    exit(0)

# Register new
for i in range(100):
    path = f'/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{i}/'
    r = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{path}', 'name'], capture_output=True, text=True)
    if r.stdout.strip() in (\"''\", '@as []', '') or r.returncode != 0:
        sp.run(['gsettings', 'set', f'{schema}.custom-keybinding:{path}', 'name', 'Ghost Screen'])
        sp.run(['gsettings', 'set', f'{schema}.custom-keybinding:{path}', 'command', target])
        sp.run(['gsettings', 'set', f'{schema}.custom-keybinding:{path}', 'binding', '<Primary>3'])
        keep.append(path)
        sp.run(['gsettings', 'set', schema, 'custom-keybindings', str(keep)])
        exit(0)
exit(1)
" && return 0 || return 1
}

setup_xfce() {
    command -v xfconf-query &>/dev/null || return 1
    xfconf-query -c xfce4-keyboard-shortcuts -n -t string -p "/commands/custom/<Primary>3" -s "$CMD" 2>/dev/null && return 0
    # fallback: try older format
    xfconf-query -c xfce4-keyboard-shortcuts -n -t string -p "/commands/custom/Control-3" -s "$CMD" 2>/dev/null && return 0
    return 1
}

setup_kde() {
    if command -v kwriteconfig5 &>/dev/null; then
        kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group "Ghost Screen" --key "Ghost Screen" "_launch $CMD" 2>/dev/null
        kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group "Ghost Screen" --key "Ghost Screen" "Ctrl+3" 2>/dev/null
        qdbus org.kde.kglobalaccel /kglobalaccel org.kde.KGlobalAccel.reloadConfig 2>/dev/null || true
        return 0
    fi
    return 1
}

# Try in order
if setup_gnome; then
    SHORTCUT_OK=1
    echo "    Ctrl+3 shortcut set (GNOME)."
elif setup_xfce; then
    SHORTCUT_OK=1
    echo "    Ctrl+3 shortcut set (XFCE)."
elif setup_kde; then
    SHORTCUT_OK=1
    echo "    Ctrl+3 shortcut set (KDE Plasma)."
elif setup_xbindkeys; then
    SHORTCUT_OK=1
    echo "    Ctrl+3 shortcut set (xbindkeys universal fallback)."
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
    echo "  Could not auto-set shortcut for your desktop environment."
    echo "  Set it manually: Settings -> Keyboard -> Shortcuts -> +"
    echo "    Name: Ghost Screen,  Command: $CMD,  Shortcut: Ctrl+3"
fi
echo "  Kill: $NAME --kill"
echo ""
