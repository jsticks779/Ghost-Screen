#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="ghost_screen.py"
NAME="ghost-screen"

# ── Self-bootstrap: if piped (no local clone), fetch the repo first ────
if [ ! -f "$DIR/$SCRIPT" ]; then
    REPO="https://github.com/jsticks779/Ghost-Screen.git"
    TMPDIR="$(mktemp -d)"
    echo "==> Downloading Ghost Screen..."
    if command -v git &>/dev/null; then
        git clone --depth=1 "$REPO" "$TMPDIR" 2>/dev/null || {
            curl -fsSL "$REPO/archive/main.tar.gz" | tar -xz -C "$TMPDIR" --strip=1 2>/dev/null || {
                echo "    Failed to download. Install git or curl." >&2
                exit 1
            }
        }
    elif command -v curl &>/dev/null; then
        curl -fsSL "$REPO/archive/main.tar.gz" | tar -xz -C "$TMPDIR" --strip=1 || {
            echo "    Failed to download. Install git or curl." >&2
            exit 1
        }
    else
        echo "    git or curl required to download. Clone manually:" >&2
        echo "    git clone $REPO" >&2
        exit 1
    fi
    cd "$TMPDIR"
    exec bash install.sh
fi

echo "==> Installing Ghost Screen..."

# ── Auto-detect: root vs user install ──────────────────────────────────

if [ "$(id -u)" -eq 0 ]; then
    BIN="/usr/local/bin"
    APP="/usr/local/share/applications"
    AUTOSTART="/etc/xdg/autostart"
    REAL_USER="${SUDO_USER:-$USER}"
    REAL_HOME="$(getent passwd "$REAL_USER" 2>/dev/null | cut -d: -f6 || echo "$HOME")"
    echo "    Running as root — installing system-wide."
else
    BIN="$HOME/.local/bin"
    APP="$HOME/.local/share/applications"
    AUTOSTART="$HOME/.config/autostart"
    REAL_USER="$USER"
    REAL_HOME="$HOME"
fi

CMD="$BIN/$NAME"

# ── Package manager auto-detection ─────────────────────────────────────

PM=""
PM_INSTALL=""
PM_UPDATE=""
if command -v apt-get &>/dev/null; then
    PM="apt"
    PM_INSTALL="apt-get install -y"
    PM_UPDATE="apt-get update"
elif command -v pacman &>/dev/null; then
    PM="pacman"
    PM_INSTALL="pacman -S --noconfirm"
    PM_UPDATE="pacman -Sy"
elif command -v dnf &>/dev/null; then
    PM="dnf"
    PM_INSTALL="dnf install -y"
    PM_UPDATE="dnf check-update"
elif command -v zypper &>/dev/null; then
    PM="zypper"
    PM_INSTALL="zypper install -y"
    PM_UPDATE="zypper refresh"
elif command -v apk &>/dev/null; then
    PM="apk"
    PM_INSTALL="apk add"
    PM_UPDATE="apk update"
elif command -v xbps-install &>/dev/null; then
    PM="xbps"
    PM_INSTALL="xbps-install -S"
    PM_UPDATE="true"
fi

if [ -z "$PM" ]; then
    echo "    No known package manager found. Dependencies must be installed manually."
fi

# ── Install helper (auto sudo if non-root) ─────────────────────────────

pm_install() {
    [ -z "$PM" ] && return 1
    local pkg="$1"
    if [ "$(id -u)" -eq 0 ]; then
        $PM_INSTALL $pkg 2>/dev/null && return 0
    else
        sudo $PM_INSTALL $pkg 2>/dev/null && return 0
    fi
    return 1
}

pm_install_pip() {
    local mod="$1"
    if command -v pip3 &>/dev/null; then
        pip3 install "$mod" 2>/dev/null && return 0
    fi
    if command -v pip &>/dev/null; then
        pip install "$mod" 2>/dev/null && return 0
    fi
    return 1
}

# ── Package name map ───────────────────────────────────────────────────

pkg_gtk3() {
    case "$PM" in
        apt)    echo "python3-gi gir1.2-gtk-3.0" ;;
        pacman) echo "python-gobject gtk3" ;;
        dnf)    echo "python3-gobject gtk3" ;;
        zypper) echo "python3-gobject gtk3" ;;
        apk)    echo "py3-gobject3 gtk+3.0" ;;
        xbps)   echo "python3-gobject gtk3" ;;
        *)      return 1 ;;
    esac
}

pkg_pillow() {
    case "$PM" in
        apt)    echo "python3-pil" ;;
        pacman) echo "python-pillow" ;;
        dnf)    echo "python3-pillow" ;;
        zypper) echo "python3-Pillow" ;;
        apk)    echo "py3-pillow" ;;
        xbps)   echo "python3-Pillow" ;;
        *)      return 1 ;;
    esac
}

pkg_tk() {
    case "$PM" in
        apt)    echo "python3-tk" ;;
        pacman) echo "tk" ;;
        dnf)    echo "python3-tkinter" ;;
        zypper) echo "python3-tk" ;;
        apk)    echo "tk" ;;
        xbps)   echo "python3-tkinter" ;;
        *)      return 1 ;;
    esac
}

# ── Dependencies ──────────────────────────────────────────────────────

display_type="${XDG_SESSION_TYPE:-x11}"

if [ "$display_type" = "wayland" ]; then

    if ! python3 -c "import gi; gi.require_version('Gtk','3.0'); gi.require_version('Gdk','3.0'); from gi.repository import Gtk, Gdk" 2>/dev/null; then
        gtk3_pkg=$(pkg_gtk3)
        if [ -n "$gtk3_pkg" ]; then
            echo "    Installing GTK3 ($gtk3_pkg)..."
            pm_install "$gtk3_pkg" || echo "    Could not install GTK3. Run: sudo $PM_INSTALL $gtk3_pkg"
        else
            echo "    GTK3 required for Wayland. Install python3-gi + gir1.2-gtk-3.0 manually."
        fi
    fi

    if ! python3 -c "from PIL import Image" 2>/dev/null; then
        pil_pkg=$(pkg_pillow)
        if [ -n "$pil_pkg" ]; then
            echo "    Installing Pillow ($pil_pkg)..."
            pm_install "$pil_pkg" || {
                echo "    System package failed, trying pip..."
                pm_install_pip "Pillow" || echo "    Could not install Pillow. Run: pip3 install Pillow"
            }
        else
            echo "    Trying pip for Pillow..."
            pm_install_pip "Pillow" || echo "    Could not install Pillow. Run: pip3 install Pillow"
        fi
    fi

else

    if ! python3 -c "import tkinter" 2>/dev/null; then
        tk_pkg=$(pkg_tk)
        if [ -n "$tk_pkg" ]; then
            echo "    Installing tkinter ($tk_pkg)..."
            pm_install "$tk_pkg" || echo "    Could not install tkinter. Run: sudo $PM_INSTALL $tk_pkg"
        else
            echo "    tkinter required for X11. Install python3-tk manually."
        fi
    fi

fi

# ── Build dependencies (for wl_inhibit.so + ghost-touch-inhibit) ──────

if [ "$display_type" = "wayland" ]; then
    case "$PM" in
        apt)
            if ! command -v gcc &>/dev/null; then
                echo "    Installing gcc..."
                pm_install "build-essential" 2>/dev/null || true
            fi
            if ! command -v wayland-scanner &>/dev/null; then
                echo "    Installing wayland-scanner..."
                pm_install "libwayland-dev" 2>/dev/null || true
            fi
            if ! command -v pkg-config &>/dev/null; then
                echo "    Installing pkg-config..."
                pm_install "pkg-config" 2>/dev/null || true
            fi
            if [ ! -f /usr/share/wayland-protocols/unstable/keyboard-shortcuts-inhibit/keyboard-shortcuts-inhibit-unstable-v1.xml ]; then
                echo "    Installing wayland-protocols..."
                pm_install "wayland-protocols" 2>/dev/null || true
            fi
            ;;
        pacman)
            command -v gcc &>/dev/null || pm_install "base-devel" 2>/dev/null || true
            command -v wayland-scanner &>/dev/null || pm_install "wayland" 2>/dev/null || true
            ;;
        dnf)
            command -v gcc &>/dev/null || pm_install "gcc" 2>/dev/null || true
            command -v wayland-scanner &>/dev/null || pm_install "wayland-devel" 2>/dev/null || true
            ;;
        zypper)
            command -v gcc &>/dev/null || pm_install "gcc" 2>/dev/null || true
            command -v wayland-scanner &>/dev/null || pm_install "libwayland-devel" 2>/dev/null || true
            ;;
    esac
fi

echo "    Display server: $display_type"

# ── Install files ─────────────────────────────────────────────────────

mkdir -p "$BIN" "$APP" "$AUTOSTART"
cp "$DIR/$SCRIPT" "$CMD"
chmod +x "$CMD"

# Build and install Wayland shortcut inhibitor (C shared library)
if command -v gcc &>/dev/null && command -v wayland-scanner &>/dev/null && [ -f "$DIR/wl_inhibit.c" ]; then
    echo "    Building Wayland shortcut inhibitor..."
    XML="$DIR/keyboard-shortcuts-inhibit-unstable-v1.xml"
    [ -f "$XML" ] || XML=""
    # Fall back to system wayland-protocols
    if [ -z "$XML" ]; then
        for d in /usr/share/wayland-protocols /usr/local/share/wayland-protocols; do
            f="$d/unstable/keyboard-shortcuts-inhibit/keyboard-shortcuts-inhibit-unstable-v1.xml"
            [ -f "$f" ] && { XML="$f"; break; }
        done
    fi
    if [ -n "$XML" ]; then
        wayland-scanner client-header "$XML" "$DIR/zwp_ksh_client.h" 2>/dev/null && \
        wayland-scanner private-code "$XML" "$DIR/wl_ksh_code.c" 2>/dev/null && \
        gcc -shared -fPIC -o "$DIR/wl_inhibit.so" \
            "$DIR/wl_inhibit.c" "$DIR/wl_ksh_code.c" \
            $(pkg-config --cflags --libs gtk+-3.0 wayland-client 2>/dev/null) 2>/dev/null && \
        echo "    wl_inhibit.so built OK" || \
        echo "    wl_inhibit.so build skipped (see above for details)"
    else
        echo "    wayland-protocols XML not found — skipping .so build"
    fi
fi

if [ -f "$DIR/wl_inhibit.so" ]; then
    cp "$DIR/wl_inhibit.so" "$BIN/wl_inhibit.so"
    chmod +x "$BIN/wl_inhibit.so"
fi

# Build and install touchscreen inhibitor (SUID helper)
if command -v gcc &>/dev/null && [ -f "$DIR/ghost_touch_inhibit.c" ]; then
    echo "    Building touchscreen inhibitor..."
    gcc -O2 -o "$DIR/ghost-touch-inhibit" "$DIR/ghost_touch_inhibit.c" -Wall 2>/dev/null && \
    echo "    ghost-touch-inhibit built OK"
    if [ -f "$DIR/ghost-touch-inhibit" ]; then
        # Remove old root-owned file first, then copy new one
        [ -f "$BIN/ghost-touch-inhibit" ] && sudo rm -f "$BIN/ghost-touch-inhibit" 2>/dev/null || true
        cp "$DIR/ghost-touch-inhibit" "$BIN/ghost-touch-inhibit" 2>/dev/null && \
        chmod +x "$BIN/ghost-touch-inhibit"
        # Set SUID root so non-root user can inhibit touchscreen devices
        if [ "$(id -u)" -eq 0 ]; then
            chown root:root "$BIN/ghost-touch-inhibit"
            chmod u+s "$BIN/ghost-touch-inhibit"
            echo "    ghost-touch-inhibit SUID set"
        else
            sudo chown root:root "$BIN/ghost-touch-inhibit" 2>/dev/null && \
            sudo chmod u+s "$BIN/ghost-touch-inhibit" 2>/dev/null && \
            echo "    ghost-touch-inhibit SUID set" || \
            echo "    ghost-touch-inhibit SUID not set (run install.sh with sudo for touchscreen blocking)"
        fi
    fi
fi

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

# ── Desktop environment detection ─────────────────────────────────────

detect_de() {
    local de="${XDG_CURRENT_DESKTOP,,}"
    echo "$de" | grep -q "gnome\|unity\|budgie\|cinnamon\|mate" && { command -v gsettings &>/dev/null && echo "gnome"; return 0; }
    echo "$de" | grep -q "kde\|plasma" && { echo "kde"; return 0; }
    echo "$de" | grep -q "xfce" && { echo "xfce"; return 0; }
    echo "$de" | grep -q "sway" && { echo "sway"; return 0; }
    echo "$de" | grep -q "hyprland" && { echo "hyprland"; return 0; }
    echo "$de" | grep -q "river" && { echo "river"; return 0; }
    echo "$de" | grep -q "cosmic" && { echo "cosmic"; return 0; }
    echo "$de" | grep -q "deepin\|dde" && { echo "deepin"; return 0; }
    echo "$de" | grep -q "lxqt\|lumina" && { echo "lxqt"; return 0; }
    return 1
}

DE=$(detect_de || true)
[ -n "$DE" ] && echo "    Desktop: $DE"

# ── Shortcut setup ────────────────────────────────────────────────────

SHORTCUT_OK=""
SHORTCUT_MSG=""

setup_gnome() {
    command -v gsettings &>/dev/null || return 1

    # Root: try to run gsettings via dbus for the real user
    if [ "$(id -u)" -eq 0 ]; then
        local bus="unix:path=/run/user/$(id -u "$REAL_USER")/bus"
        python3 << PYEOF 2>/dev/null || return 1
import subprocess as sp, ast, os
os.environ["DBUS_SESSION_BUS_ADDRESS"] = "$bus"
schema = "org.gnome.settings-daemon.plugins.media-keys"
target = "$CMD"
try:
    cur = sp.run(["gsettings", "get", schema, "custom-keybindings"], capture_output=True, text=True, timeout=10).stdout.strip()
except:
    exit(1)
existing = ast.literal_eval(cur) if cur.startswith("[") else []
found = False
keep = []
for p in existing:
    cmd = sp.run(["gsettings", "get", f"{schema}.custom-keybinding:{p}", "command"], capture_output=True, text=True, timeout=10).stdout.strip().strip("'")
    if cmd == target:
        if found:
            for k in ["name", "command", "binding"]:
                sp.run(["gsettings", "reset", f"{schema}.custom-keybinding:{p}", k], timeout=10)
            continue
        found = True
    keep.append(p)
if found:
    sp.run(["gsettings", "set", schema, "custom-keybindings", str(keep)], timeout=10)
    exit(0)
for i in range(100):
    path = f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{i}/"
    r = sp.run(["gsettings", "get", f"{schema}.custom-keybinding:{path}", "name"], capture_output=True, text=True, timeout=10)
    if r.stdout.strip() in ("''", "@as []", "") or r.returncode != 0:
        sp.run(["gsettings", "set", f"{schema}.custom-keybinding:{path}", "name", "Ghost Screen"], timeout=10)
        sp.run(["gsettings", "set", f"{schema}.custom-keybinding:{path}", "command", target], timeout=10)
        sp.run(["gsettings", "set", f"{schema}.custom-keybinding:{path}", "binding", "<Primary>3"], timeout=10)
        keep.append(path)
        sp.run(["gsettings", "set", schema, "custom-keybindings", str(keep)], timeout=10)
        exit(0)
exit(1)
PYEOF
        return $?
    fi

    # Normal user
    python3 << PYEOF 2>/dev/null || return 1
import subprocess as sp, ast
schema = "org.gnome.settings-daemon.plugins.media-keys"
target = "$CMD"
try:
    cur = sp.run(["gsettings", "get", schema, "custom-keybindings"], capture_output=True, text=True, timeout=10).stdout.strip()
except:
    exit(1)
existing = ast.literal_eval(cur) if cur.startswith("[") else []
found = False
keep = []
for p in existing:
    cmd = sp.run(["gsettings", "get", f"{schema}.custom-keybinding:{p}", "command"], capture_output=True, text=True, timeout=10).stdout.strip().strip("'")
    if cmd == target:
        if found:
            for k in ["name", "command", "binding"]:
                sp.run(["gsettings", "reset", f"{schema}.custom-keybinding:{p}", k], timeout=10)
            continue
        found = True
    keep.append(p)
if found:
    sp.run(["gsettings", "set", schema, "custom-keybindings", str(keep)], timeout=10)
    exit(0)
for i in range(100):
    path = f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{i}/"
    r = sp.run(["gsettings", "get", f"{schema}.custom-keybinding:{path}", "name"], capture_output=True, text=True, timeout=10)
    if r.stdout.strip() in ("''", "@as []", "") or r.returncode != 0:
        sp.run(["gsettings", "set", f"{schema}.custom-keybinding:{path}", "name", "Ghost Screen"], timeout=10)
        sp.run(["gsettings", "set", f"{schema}.custom-keybinding:{path}", "command", target], timeout=10)
        sp.run(["gsettings", "set", f"{schema}.custom-keybinding:{path}", "binding", "<Primary>3"], timeout=10)
        keep.append(path)
        sp.run(["gsettings", "set", schema, "custom-keybindings", str(keep)], timeout=10)
        exit(0)
exit(1)
PYEOF
}

setup_kde() {
    command -v kwriteconfig5 &>/dev/null || return 1
    local user="$REAL_USER"
    local home="$REAL_HOME"
    if [ "$(id -u)" -eq 0 ]; then
        su - "$user" -c "kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group 'Ghost Screen' --key 'Ghost Screen' '_launch $CMD'" 2>/dev/null
        su - "$user" -c "kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group 'Ghost Screen' --key 'Ghost Screen' 'Ctrl+3'" 2>/dev/null
    else
        kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group "Ghost Screen" --key "Ghost Screen" "_launch $CMD" 2>/dev/null
        kwriteconfig5 --file ~/.config/kglobalshortcutsrc --group "Ghost Screen" --key "Ghost Screen" "Ctrl+3" 2>/dev/null
    fi
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
    local cfg="$REAL_HOME/.config/sway/config"
    [ -f "$cfg" ] || cfg="$REAL_HOME/.config/i3/config"
    [ -f "$cfg" ] || return 1
    grep -q "ghost-screen" "$cfg" && return 0
    cat >> "$cfg" << EOF

# Added by Ghost Screen installer — Ctrl+3 toggles ghost overlay
bindsym Ctrl+3 exec $CMD
EOF
    SHORTCUT_MSG="Reload Sway: swaymsg reload"
    return 0
}

setup_hyprland() {
    local cfg="$REAL_HOME/.config/hypr/hyprland.conf"
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
    local cfg="$REAL_HOME/.config/river/init"
    [ -f "$cfg" ] || return 1
    grep -q "ghost-screen" "$cfg" && return 0
    cat >> "$cfg" << EOF

# Added by Ghost Screen installer — Ctrl+3 toggles ghost overlay
riverctl map normal Ctrl 3 spawn "$CMD" &
EOF
    SHORTCUT_MSG="Restart River to activate"
    return 0
}

setup_deepin() {
    command -v gsettings &>/dev/null || return 1
    # Deepin uses same gsettings as GNOME
    setup_gnome
}

setup_lxqt() {
    command -v lxqt-config-session &>/dev/null || return 1
    local cfg="$REAL_HOME/.config/lxqt/globalkeyshortcuts.conf"
    [ -f "$cfg" ] || return 1
    grep -q "ghost-screen" "$cfg" && return 0
    cat >> "$cfg" << EOF

[Ghost Screen]
Comment=
Exec=$CMD
Shortcut=Ctrl+3
EOF
    return 0
}

setup_xbindkeys() {
    if [ "$display_type" = "wayland" ]; then
        echo "    xbindkeys does not work on native Wayland — skipping."
        return 1
    fi
    if ! command -v xbindkeys &>/dev/null; then
        echo "    Installing xbindkeys..."
        pm_install xbindkeys 2>/dev/null || return 1
    fi

    cat > "$REAL_HOME/.xbindkeysrc" << XEOF
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
    gnome)  setup_gnome && SHORTCUT_OK=1 && echo "    Ctrl+3 shortcut set (GNOME)." ;;
    kde)    setup_kde && SHORTCUT_OK=1 && echo "    Ctrl+3 shortcut set (KDE Plasma).${SHORTCUT_MSG:+ $SHORTCUT_MSG}" ;;
    xfce)   setup_xfce && SHORTCUT_OK=1 && echo "    Ctrl+3 shortcut set (XFCE)." ;;
    sway)   setup_sway && SHORTCUT_OK=1 && echo "    Ctrl+3 shortcut set (Sway).${SHORTCUT_MSG:+ $SHORTCUT_MSG}" ;;
    hyprland) setup_hyprland && SHORTCUT_OK=1 && echo "    Ctrl+3 shortcut set (Hyprland).${SHORTCUT_MSG:+ $SHORTCUT_MSG}" ;;
    river)  setup_river && SHORTCUT_OK=1 && echo "    Ctrl+3 shortcut set (River).${SHORTCUT_MSG:+ $SHORTCUT_MSG}" ;;
    deepin) setup_deepin && SHORTCUT_OK=1 && echo "    Ctrl+3 shortcut set (Deepin)." ;;
    lxqt)   setup_lxqt && SHORTCUT_OK=1 && echo "    Ctrl+3 shortcut set (LXQt)." ;;
    *)
        if setup_gnome; then
            SHORTCUT_OK=1; echo "    Ctrl+3 shortcut set (GNOME/gsettings)."
        elif setup_kde; then
            SHORTCUT_OK=1; echo "    Ctrl+3 shortcut set (KDE/kwriteconfig5)."
        elif setup_xfce; then
            SHORTCUT_OK=1; echo "    Ctrl+3 shortcut set (XFCE/xfconf)."
        elif setup_sway; then
            SHORTCUT_OK=1; echo "    Ctrl+3 shortcut set (Sway).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        elif setup_hyprland; then
            SHORTCUT_OK=1; echo "    Ctrl+3 shortcut set (Hyprland).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        elif setup_river; then
            SHORTCUT_OK=1; echo "    Ctrl+3 shortcut set (River).${SHORTCUT_MSG:+ $SHORTCUT_MSG}"
        elif setup_deepin; then
            SHORTCUT_OK=1; echo "    Ctrl+3 shortcut set (Deepin)."
        elif setup_xbindkeys; then
            SHORTCUT_OK=1; echo "    Ctrl+3 shortcut set (xbindkeys fallback)."
        fi
        ;;
esac

# ── Save shortcut config (for --shortcut command) ─────────────────────

if [ -n "$SHORTCUT_OK" ]; then
    CONFIG_DIR="$REAL_HOME/.config/ghost-screen"
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_DIR/shortcut.json" << EOF
{"shortcut": "Ctrl+3", "de": "${DE:-x11}"}
EOF
fi

# ── PATH setup (for non-root installs) ────────────────────────────────

if [ "$(id -u)" -ne 0 ]; then
    # Check and add to all shell configs
    PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
    for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile" "$HOME/.bash_profile" "$HOME/.zshenv"; do
        [ -f "$rc" ] || continue
        if ! grep -qsF "$BIN" "$rc" 2>/dev/null; then
            echo "$PATH_LINE" >> "$rc"
            echo "    Added $BIN to PATH in $(basename "$rc")"
        fi
    done
fi

# ── Done ──────────────────────────────────────────────────────────────

echo ""
# Render logo.svg in terminal with true-color cyan
python3 - "$DIR/logo.svg" 2>/dev/null << 'PYEOF' || echo "  Ghost Screen"
import xml.etree.ElementTree as ET, sys
C = '\033[38;2;0;255;247m'; R = '\033[0m'
try:
    t = ET.parse(sys.argv[1])
    r = t.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    letters = {}
    for g in r.findall('.//svg:g', ns):
        gid = g.get('id', '')
        if gid.startswith('l') and gid[1:].isdigit():
            pts = [(int(float(a.get('x', 0))), int(float(a.get('y', 0)))) for a in g.findall('svg:rect', ns)]
            if pts: letters[int(gid[1:])] = pts
    def render(idx):
        pts = letters[idx]
        mx = min(p[0] for p in pts); Mx = max(p[0] for p in pts) + 10
        my = min(p[1] for p in pts); My = max(p[1] for p in pts) + 10
        g = [[0] * ((Mx - mx) // 10) for _ in range((My - my) // 10)]
        for x, y in pts: g[(y - my) // 10][(x - mx) // 10] = 1
        return [''.join('█' if g[r_][c_] else ' ' for c_ in range(len(g[0]))) for r_ in range(len(g))] + [' ' * len(g[0])] * (7 - len(g))
    grids = [render(i) for i in sorted(letters)]
    gid = [0, 1, 2, 3, 4]; sid = [5, 6, 7, 8, 9, 10]
    for row in range(7):
        print(C + ' '.join(grids[i][row] for i in gid) + '  ' + ' '.join(grids[i][row] for i in sid) + R)
except:
    print('  Ghost Screen')
PYEOF
echo "  Ghost Screen installed!"
echo ""
if [ -n "$SHORTCUT_OK" ]; then
  echo "  Press  Ctrl+3  to toggle the ghost on/off"
  [ -n "$SHORTCUT_MSG" ] && echo "  $SHORTCUT_MSG"
else
  echo "  Shortcut not set — do it manually:"
  echo "    Settings -> Keyboard -> Shortcuts -> +"
  echo "    Name: Ghost Screen,  Command: $CMD,  Shortcut: Ctrl+3"
fi
echo "  Kill: $CMD --kill"
echo "  Check: $CMD --check"
echo ""
