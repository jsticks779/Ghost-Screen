#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin"
APP="$HOME/.local/share/applications"
SCRIPT="ghost_screen.py"
NAME="ghost-screen"

echo "Installing Ghost Screen..."

mkdir -p "$BIN" "$APP"

cp "$DIR/$SCRIPT" "$BIN/$NAME"
chmod +x "$BIN/$NAME"

cat > "$APP/ghost-screen.desktop" << EOF
[Desktop Entry]
Name=Ghost Screen
Comment=Toggle tech ghost desktop overlay
Exec=$BIN/$NAME
Terminal=false
Type=Application
Categories=Utility;
EOF

chmod +x "$APP/ghost-screen.desktop"

echo ""
echo "  Ghost Screen installed!"
echo ""
echo "  USAGE:"
echo "    Run:  $NAME              (toggle on/off)"
echo "    Kill: $NAME --kill       (force stop)"
echo ""
echo "  KEYBOARD SHORTCUT:"
echo "    To set up a shortcut (GNOME):"
echo "      1. Settings -> Keyboard -> Keyboard Shortcuts"
echo "      2. Scroll down, click '+'"
echo "      3. Name: Ghost Screen"
echo "      4. Command: $BIN/$NAME"
echo "      5. Click 'Set Shortcut', press Ctrl+3 (or your choice)"
echo ""
echo "  Other DEs: add custom shortcut running '$BIN/$NAME'"
echo ""

# Try GNOME shortcut
if command -v gsettings &>/dev/null; then
    for i in $(seq 0 99); do
        KEY_PATH="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom${i}/"
        if ! gsettings get org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${KEY_PATH} name &>/dev/null; then
            gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${KEY_PATH} name "Ghost Screen" 2>/dev/null || break
            gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${KEY_PATH} command "$BIN/$NAME" 2>/dev/null || break
            gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${KEY_PATH} binding "<Primary>3" 2>/dev/null || break

            CURRENT=$(gsettings get org.gnome.settings-daemon.plugins.media-keys custom-keybindings 2>/dev/null || echo "@as []")
            if [ "$CURRENT" = "@as []" ] || [ "$CURRENT" = "[]" ]; then
                gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['${KEY_PATH}']" 2>/dev/null || break
            else
                NEW=$(echo "$CURRENT" | sed "s/\]/, '${KEY_PATH}'\]/" 2>/dev/null) || break
                gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "$NEW" 2>/dev/null || break
            fi
            echo "  Ctrl+3 shortcut registered (GNOME)."
            break
        fi
    done
fi
