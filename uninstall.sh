#!/usr/bin/env bash
set -e

BIN="$HOME/.local/bin"
APP="$HOME/.local/share/applications"
NAME="ghost-screen"
CMD="$BIN/$NAME"

echo "==> Uninstalling Ghost Screen..."

"$CMD" --kill 2>/dev/null || true

rm -f "$CMD"
rm -f "$APP/ghost-screen.desktop"

# Remove GNOME shortcut if present
if command -v gsettings &>/dev/null; then
    python3 -c "
import subprocess as sp
schema = 'org.gnome.settings-daemon.plugins.media-keys'
target_cmd = '$CMD'
changed = False

cur_list = sp.run(['gsettings', 'get', schema, 'custom-keybindings'], capture_output=True, text=True).stdout.strip()
if cur_list in ('@as []', '[]'):
    exit(0)

# Parse paths
paths = []
raw = cur_list.strip()
if raw.startswith('[') and raw.endswith(']'):
    import ast
    try:
        paths = ast.literal_eval(raw)
    except:
        pass

new_paths = []
for p in paths:
    cmd = sp.run(['gsettings', 'get', f'{schema}.custom-keybinding:{p}', 'command'], capture_output=True, text=True).stdout.strip().strip(\"'\")
    if cmd == target_cmd:
        # Remove this binding
        sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', 'name'])
        sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', 'command'])
        sp.run(['gsettings', 'reset', f'{schema}.custom-keybinding:{p}', 'binding'])
        changed = True
    else:
        new_paths.append(p)

if changed:
    if new_paths:
        sp.run(['gsettings', 'set', schema, 'custom-keybindings', str(new_paths)])
    else:
        sp.run(['gsettings', 'set', schema, 'custom-keybindings', '@as []'])
print('Shortcut cleaned up.' if changed else 'No shortcut found.')
"
fi

echo ""
echo "  Ghost Screen uninstalled!"
echo ""
