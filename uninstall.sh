#!/usr/bin/env bash
set -e

BIN="$HOME/.local/bin"
APP="$HOME/.local/share/applications"
NAME="ghost-screen"

echo "Uninstalling Ghost Screen..."

"$BIN/$NAME" --kill 2>/dev/null || true

rm -f "$BIN/$NAME"
rm -f "$APP/ghost-screen.desktop"

echo "  Ghost Screen uninstalled!"
echo "  (Remove the keyboard shortcut manually if you set one)"
