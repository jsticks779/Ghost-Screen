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
rm -f "/usr/local/share/applications/$NAME.desktop" 2>/dev/null || true

# Remove GNOME shortcut
if command -v gsettings &>/dev/null; then
    python3 -c "
import subprocess as sp, ast
schema = 'org.gnome.settings-daemon.plugins.media-keys'
target = '$CMD'

cur = sp.run(['gsettings', 'get', schema, 'custom-keybindings'], capture_output=True, text=True).stdout.strip()
if cur.startswith('['):
    paths = ast.literal_eval(cur)
    remaining = []
    for p in paths:
        cmd = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{p}', 'command'], capture_output=True, text=True).stdout.strip().strip(\"'\")
        if cmd == target:
            sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', 'name'])
            sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', 'command'])
            sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', 'binding'])
            print(f'Removed GNOME shortcut {p}')
        else:
            remaining.append(p)
    sp.run(['gsettings', 'set', schema, 'custom-keybindings', str(remaining)])
" 2>/dev/null || true
fi

# Remove xbindkeys config if it only has our shortcut
if [ -f "$HOME/.xbindkeysrc" ] && grep -q "$CMD" "$HOME/.xbindkeysrc" 2>/dev/null; then
    if [ "$(wc -l < "$HOME/.xbindkeysrc")" -le 3 ]; then
        rm -f "$HOME/.xbindkeysrc"
    else
        grep -v "$CMD" "$HOME/.xbindkeysrc" | grep -v "Control+3" > /tmp/xbindkeysrc.tmp && mv /tmp/xbindkeysrc.tmp "$HOME/.xbindkeysrc"
    fi
    pkill xbindkeys 2>/dev/null || true
    sleep 0.5
    xbindkeys 2>/dev/null || true
fi

# XFCE cleanup (best-effort)
command -v xfconf-query &>/dev/null && xfconf-query -c xfce4-keyboard-shortcuts -r -p "/commands/custom/<Primary>3" 2>/dev/null || true

# KDE cleanup (best-effort)
if command -v kwriteconfig5 &>/dev/null; then
    kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group "Ghost Screen" --key "Ghost Screen" "" 2>/dev/null || true
fi

# wlroots config cleanup (best-effort — just remove our comment block)
for cfg in "$HOME/.config/sway/config" "$HOME/.config/hypr/hyprland.conf" "$HOME/.config/river/init"; do
    [ -f "$cfg" ] || continue
    if grep -q "Ghost Screen installer" "$cfg" 2>/dev/null; then
        sed -i '/^# Added by Ghost Screen/,/^[^#]/d' "$cfg" 2>/dev/null
        # Remove trailing blank lines left behind
        sed -i '/^$/N;/^\n$/D' "$cfg" 2>/dev/null || true
        echo "    Cleaned $cfg"
    fi
done

echo ""
echo "  Ghost Screen uninstalled!"
echo ""
