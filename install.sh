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

    if ! python3 -c "import gi; gi.require_version('Gtk','3.0'); gi.require_version('Gdk','3.0'); from gi.repository import Gtk, Gdk" 2>/dev/null; then
        echo "    GTK3 GI not found (required for Wayland). Installing..."
        if command -v apt-get &>/dev/null; then
            sudo apt-get install -y python3-gi gir1.2-gtk-3.0 2>/dev/null || echo "    Could not install GTK3 — try: sudo apt-get install python3-gi gir1.2-gtk-3.0"
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm python-gobject gtk3 2>/dev/null || echo "    Could not install GTK3 — try: sudo pacman -S python-gobject gtk3"
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3-gobject gtk3 2>/dev/null || echo "    Could not install GTK3 — try: sudo dnf install python3-gobject gtk3"
        else
            echo "    Unknown package manager. Install python3-gi and gir1.2-gtk-3.0 manually."
        fi
    fi

    if ! python3 -c "from PIL import Image" 2>/dev/null; then
        echo "    Pillow not found (required for Wayland transparency). Installing..."
        if command -v apt-get &>/dev/null; then
            apt-cache show python3-pil &>/dev/null && sudo apt-get install -y python3-pil 2>/dev/null || echo "    python3-pil not in repos. Try: pip install Pillow"
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm python-pillow 2>/dev/null || echo "    Could not install python-pillow. Try: pip install Pillow"
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3-pillow 2>/dev/null || echo "    Could not install python3-pillow. Try: pip install Pillow"
        else
            echo "    Unknown package manager. Install python3-pil or run: pip install Pillow"
        fi
    fi

else

    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo "    python3-tk not found (required for X11). Installing..."
        if command -v apt-get &>/dev/null; then
            sudo apt-get install -y python3-tk 2>/dev/null || echo "    Could not install python3-tk"
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm tk 2>/dev/null || echo "    Could not install tk"
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3-tkinter 2>/dev/null || echo "    Could not install python3-tkinter"
        else
            echo "    Unknown package manager. Install python3-tk manually."
        fi
    fi

fi

# ── Detect display server ────────────────────────────────────────────

echo "    Display server: ${XDG_SESSION_TYPE:-x11}"

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

# ── Detect desktop environment ────────────────────────────────────────

detect_de() {
    local de="${XDG_CURRENT_DESKTOP,,}"
    if echo "$de" | grep -q "gnome"; then echo "gnome"; return 0; fi
    if echo "$de" | grep -q "kde\|plasma"; then echo "kde"; return 0; fi
    if echo "$de" | grep -q "xfce"; then echo "xfce"; return 0; fi
    if echo "$de" | grep -q "sway"; then echo "sway"; return 0; fi
    if echo "$de" | grep -q "hyprland"; then echo "hyprland"; return 0; fi
    if echo "$de" | grep -q "river"; then echo "river"; return 0; fi
    if echo "$de" | grep -q "cosmic"; then echo "cosmic"; return 0; fi
    if echo "$de" | grep -q "budgie\|cinnamon\|mate"; then
        if command -v gsettings &>/dev/null; then echo "gnome"; return 0; fi
    fi
    return 1
}

DE=$(detect_de || true)

# ── Shortcut setup ────────────────────────────────────────────────────

SHORTCUT_OK=""
SHORTCUT_MSG=""

setup_gnome() {
    command -v gsettings &>/dev/null || return 1
    python3 -c "
import subprocess as sp, ast
schema = 'org.gnome.settings-daemon.plugins.media-keys'
target = '$CMD'

cur = sp.run(['gsettings', 'get', schema, 'custom-keybindings'], capture_output=True, text=True).stdout.strip()
existing = ast.literal_eval(cur) if cur.startswith('[') else []

found = False
keep = []
for p in existing:
    cmd = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{p}', 'command'], capture_output=True, text=True).stdout.strip().strip(\"'\")
    if cmd == target:
        if found:
            for k in ['name', 'command', 'binding']:
                sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', k])
            continue
        found = True
    keep.append(p)

if found:
    sp.run(['gsettings', 'set', schema, 'custom-keybindings', str(keep)])
    exit(0)

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

setup_kde() {
    command -v kwriteconfig5 &>/dev/null || return 1
    kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group "Ghost Screen" --key "Ghost Screen" "_launch $CMD" 2>/dev/null
    kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group "Ghost Screen" --key "Ghost Screen" "Ctrl+3" 2>/dev/null
    qdbus org.kde.kglobalaccel /kglobalaccel org.kde.KGlobalAccel.reloadConfig 2>/dev/null || true
    return 0
}

setup_xfce() {
    command -v xfconf-query &>/dev/null || return 1
    xfconf-query -c xfce4-keyboard-shortcuts -n -t string -p "/commands/custom/<Primary>3" -s "$CMD" 2>/dev/null && return 0
    xfconf-query -c xfce4-keyboard-shortcuts -n -t string -p "/commands/custom/Control-3" -s "$CMD" 2>/dev/null && return 0
    return 1
}

setup_sway() {
    local cfg="$HOME/.config/sway/config"
    if [ ! -f "$cfg" ]; then
        # also check the legacy location
        cfg="$HOME/.config/i3/config"
        [ -f "$cfg" ] || return 1
    fi
    grep -q "ghost-screen" "$cfg" && return 0
    cat >> "$cfg" << EOF

# Added by Ghost Screen installer — Ctrl+3 toggles ghost overlay
bindsym Ctrl+3 exec $CMD
EOF
    SHORTCUT_MSG="Reload Sway: swaymsg reload"
    return 0
}

setup_hyprland() {
    local cfg="$HOME/.config/hypr/hyprland.conf"
    [ -f "$cfg" ] || return 1
    grep -q "ghost-screen" "$cfg" && return 0
    cat >> "$cfg" << EOF

# Added by Ghost Screen installer — Ctrl+3 toggles ghost overlay
bind = Ctrl, 3, exec, $CMD
EOF
    SHORTCUT_MSG="Reload Hyprland: hyprctl reload"
    return 0
}

setup_river() {
    local cfg="$HOME/.config/river/init"
    [ -f "$cfg" ] || return 1
    grep -q "ghost-screen" "$cfg" && return 0
    cat >> "$cfg" << EOF

# Added by Ghost Screen installer — Ctrl+3 toggles ghost overlay
riverctl map normal Ctrl 3 spawn "$CMD" &
EOF
    SHORTCUT_MSG="Restart River to activate"
    return 0
}

setup_cosmic() {
    # COSMIC DE uses its own shortcut system
    local cfg="$HOME/.config/cosmic/shortcuts.ron"
    [ -f "$cfg" ] || return 1
    grep -q "ghost-screen" "$cfg" && return 0
    echo "    COSMIC detected — shortcut must be set manually:"
    echo "    Settings -> Keyboard -> Keyboard Shortcuts -> +"
    echo "      Name: Ghost Screen,  Command: $CMD,  Shortcut: Ctrl+3"
    return 1  # return 1 so we don't mark as handled — user manual
}

setup_xbindkeys() {
    if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
        echo "    xbindkeys does not work on native Wayland. Skipping."
        return 1
    fi
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

# ── Try shortcut setup ────────────────────────────────────────────────

case "$DE" in
    gnome)
        if setup_gnome; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (GNOME)."
        fi
        ;;
    kde)
        if setup_kde; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (KDE Plasma).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        fi
        ;;
    xfce)
        if setup_xfce; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (XFCE)."
        fi
        ;;
    sway)
        if setup_sway; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (Sway).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        fi
        ;;
    hyprland)
        if setup_hyprland; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (Hyprland).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        fi
        ;;
    river)
        if setup_river; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (River).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        fi
        ;;
    cosmic)
        if setup_cosmic; then
            SHORTCUT_OK=1
        fi
        ;;
    *)
        # Fallback: try each in order
        if setup_gnome; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (GNOME/gsettings)."
        elif setup_kde; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (KDE/kwriteconfig5)."
        elif setup_xfce; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (XFCE/xfconf)."
        elif setup_sway; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (Sway).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        elif setup_hyprland; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (Hyprland).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        elif setup_river; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (River).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        elif setup_xbindkeys; then
            SHORTCUT_OK=1
            echo "    Ctrl+3 shortcut set (xbindkeys fallback)."
        fi
        ;;
esac

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
    [ -n "$SHORTCUT_MSG" ] && echo "  $SHORTCUT_MSG"
else
    echo "  Could not set shortcut automatically."
    echo "  Set it manually: Settings -> Keyboard -> Shortcuts -> +"
    echo "    Name: Ghost Screen,  Command: $CMD,  Shortcut: Ctrl+3"
fi
echo "  Kill: $CMD --kill"
echo "  Check: $CMD --check"
echo ""
