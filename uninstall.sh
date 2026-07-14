#!/usr/bin/env bash
set -e

BIN="$HOME/.local/bin"
APP="$HOME/.local/share/applications"
AUTOSTART="$HOME/.config/autostart"
NAME="ghost-screen"
CMD="$BIN/$NAME"

echo "==> Uninstalling Ghost Screen..."

"$CMD" --kill 2>/dev/null || true

rm -f "$CMD"
rm -f "$APP/ghost-screen.desktop"
rm -f "$AUTOSTART/xbindkeys.desktop"

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

echo ""
echo "  Ghost Screen uninstalled!"
echo ""
