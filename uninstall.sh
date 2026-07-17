#!/usr/bin/env bash
set -e

NAME="ghost-screen"

echo "==> Uninstalling Ghost Screen..."

# Try all possible install locations
for CMD in "$HOME/.local/bin/$NAME" "/usr/local/bin/$NAME"; do
    [ -f "$CMD" ] || continue
    "$CMD" --kill 2>/dev/null || true
    rm -f "$CMD"
    echo "    Removed $CMD"
done

rm -f "$HOME/.local/share/applications/$NAME.desktop"
rm -f "$HOME/.config/autostart/xbindkeys.desktop"
rm -f "$HOME/.config/autostart/$NAME.desktop"
rm -f "/usr/local/share/applications/$NAME.desktop" 2>/dev/null || true

# Determine which binary was installed
for BIN in "$HOME/.local/bin/$NAME" "/usr/local/bin/$NAME"; do
    [ -x "$BIN" ] && { CMD="$BIN"; break; }
done

# ── Read saved shortcut config ────────────────────────────────────────

SCONFIG="$HOME/.config/ghost-screen/shortcut.json"
if [ -f "$SCONFIG" ]; then
    SAVED_DE=$(python3 -c "import json; print(json.load(open('$SCONFIG')).get('de',''))" 2>/dev/null)
    SAVED_SHORTCUT=$(python3 -c "import json; print(json.load(open('$SCONFIG')).get('shortcut',''))" 2>/dev/null)
fi
rm -f "$SCONFIG" 2>/dev/null || true
rmdir "$HOME/.config/ghost-screen" 2>/dev/null || true

# ── Targeted cleanup by DE ────────────────────────────────────────────

case "${SAVED_DE}" in
    gnome|deepin)
        if command -v gsettings &>/dev/null; then
            python3 -c "
import subprocess as sp, ast
schema = 'org.gnome.settings-daemon.plugins.media-keys'
target = '$CMD'
try:
    cur = sp.run(['gsettings', 'get', schema, 'custom-keybindings'], capture_output=True, text=True, timeout=10).stdout.strip()
except:
    exit(0)
if not cur.startswith('['):
    exit(0)
paths = ast.literal_eval(cur)
remaining = []
for p in paths:
    cmd = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{p}', 'command'], capture_output=True, text=True, timeout=5).stdout.strip().strip(\"'\")
    if cmd == target:
        for k in ['name', 'command', 'binding']:
            sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', k], timeout=5)
        print(f'    Removed GNOME/Deepin shortcut {p}')
    else:
        remaining.append(p)
sp.run(['gsettings', 'set', schema, 'custom-keybindings', str(remaining)], timeout=5)
" 2>/dev/null || true
        fi
        ;;
    kde)
        if command -v kwriteconfig5 &>/dev/null; then
            kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group "Ghost Screen" --key "Ghost Screen" "" 2>/dev/null || true
            echo "    Removed KDE shortcut"
        fi
        ;;
    xfce)
        command -v xfconf-query &>/dev/null && \
            xfconf-query -c xfce4-keyboard-shortcuts -r -p "/commands/custom/<Primary>3" 2>/dev/null && \
            echo "    Removed XFCE shortcut" || true
        ;;
    sway|hyprland|river)
        de="$SAVED_DE"
        for cfg in "$HOME/.config/sway/config" "$HOME/.config/hypr/hyprland.conf" "$HOME/.config/river/init" "$HOME/.config/i3/config"; do
            [ -f "$cfg" ] || continue
            if grep -q "$CMD" "$cfg" 2>/dev/null || grep -q "Ghost Screen installer" "$cfg" 2>/dev/null; then
                sed -i '/Ghost Screen/d' "$cfg" 2>/dev/null || true
                sed -i "/$(echo "$CMD" | sed 's|/|\\/|g')/d" "$cfg" 2>/dev/null || true
                echo "    Cleaned $cfg"
            fi
        done
        ;;
    lxqt)
        cfg="$HOME/.config/lxqt/globalkeyshortcuts.conf"
        [ -f "$cfg" ] && sed -i '/\[Ghost Screen\]/,/^\[/d' "$cfg" 2>/dev/null && echo "    Removed LXQt shortcut" || true
        ;;
    x11|xbindkeys)
        if [ -f "$HOME/.xbindkeysrc" ] && grep -q "$CMD" "$HOME/.xbindkeysrc" 2>/dev/null; then
            rm -f "$HOME/.xbindkeysrc"
            pkill xbindkeys 2>/dev/null || true
            echo "    Removed xbindkeys shortcut"
        fi
        ;;
    *)
        # Fallback: try all DEs
        if command -v gsettings &>/dev/null; then
            python3 -c "
import subprocess as sp, ast
schema = 'org.gnome.settings-daemon.plugins.media-keys'
target = '$CMD'
try:
    cur = sp.run(['gsettings', 'get', schema, 'custom-keybindings'], capture_output=True, text=True, timeout=10).stdout.strip()
except:
    exit(0)
if not cur.startswith('['):
    exit(0)
paths = ast.literal_eval(cur)
remaining = []
for p in paths:
    cmd = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{p}', 'command'], capture_output=True, text=True, timeout=5).stdout.strip().strip(\"'\")
    if cmd == target:
        for k in ['name', 'command', 'binding']:
            sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', k], timeout=5)
    else:
        remaining.append(p)
sp.run(['gsettings', 'set', schema, 'custom-keybindings', str(remaining)], timeout=5)
" 2>/dev/null || true
        fi
        command -v kwriteconfig5 &>/dev/null && kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group "Ghost Screen" --key "Ghost Screen" "" 2>/dev/null || true
        command -v xfconf-query &>/dev/null && xfconf-query -c xfce4-keyboard-shortcuts -r -p "/commands/custom/<Primary>3" 2>/dev/null || true
        for cfg in "$HOME/.config/sway/config" "$HOME/.config/hypr/hyprland.conf" "$HOME/.config/river/init"; do
            [ -f "$cfg" ] || continue
            [ -f "$cfg" ] && sed -i '/Ghost Screen/d' "$cfg" 2>/dev/null || true
            [ -f "$cfg" ] && sed -i "/$(echo "$CMD" | sed 's|/|\\/|g')/d" "$cfg" 2>/dev/null || true
        done
        [ -f "$HOME/.xbindkeysrc" ] && grep -q "$CMD" "$HOME/.xbindkeysrc" 2>/dev/null && rm -f "$HOME/.xbindkeysrc" && pkill xbindkeys 2>/dev/null || true
        ;;
esac

echo ""
echo "  Ghost Screen uninstalled!"
echo ""
