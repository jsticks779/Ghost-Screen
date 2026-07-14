#!/usr/bin/env python3

import math
import random
import os
import sys
import signal
import argparse
import json
import subprocess
import shutil
import atexit

PROJECT = "Ghost Screen"
VERSION = "1.0.0"
PID_FILE = "/tmp/ghost_screen.pid"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ghost_screen.json")

GHOST_POLYGON = [
    (-0.32, -0.48), (-0.24, -0.56), (-0.12, -0.60),
    (0.00, -0.62),  (0.12, -0.60),  (0.24, -0.56),
    (0.32, -0.48),
    (0.42, -0.25),
    (0.42, 0.20),
    (0.37, 0.35), (0.27, 0.20), (0.17, 0.35),
    (0.07, 0.20), (-0.07, 0.35), (-0.17, 0.20),
    (-0.27, 0.35), (-0.37, 0.20),
    (-0.42, 0.20),
    (-0.42, -0.25),
]

CIRCUIT_PATHS = [
    [(-0.20, -0.42), (-0.20, -0.20), (0.00, -0.20)],
    [(0.20, -0.42),  (0.20, -0.15),  (0.08, -0.15), (0.08, 0.00)],
    [(-0.25, -0.10), (-0.25, 0.10),  (-0.10, 0.10), (-0.10, 0.18)],
    [(0.25, -0.05),  (0.25, 0.12),   (0.12, 0.12)],
    [(-0.30, 0.15),  (-0.15, 0.15),  (-0.15, 0.00), (0.00, 0.00)],
    [(-0.08, -0.35), (-0.08, -0.10), (0.12, -0.10)],
    [(0.00, 0.00),   (0.18, 0.00),   (0.18, 0.20)],
    [(0.00, -0.30),  (0.15, -0.30),  (0.15, -0.42)],
    [(-0.12, -0.20), (0.05, -0.20)],
]

DEFAULT_CONFIG = {
    "opacity": 0.88,
    "frame_delay": 33,
    "rotation_speed": 0.02,
    "float_speed": 0.035,
    "float_amplitude": 30,
    "particle_count": 60,
    "ghost_scale": 0.28,
    "colors": {
        "primary": "#00fff7",
        "secondary": "#ff0088",
        "accent": "#4488ff",
        "particle": "#aa44ff",
        "ghost_fill": "#08081a",
        "ghost_outline": "#00fff7",
        "bg": "#050510",
        "grid": "#151530",
        "glow": "#00fff7",
    }
}


def is_running():
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def kill_ghost():
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
    except (OSError, ValueError):
        pass
    try:
        os.remove(PID_FILE)
    except OSError:
        pass
    return True


def hex_to_rgba(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0,
            int(h[4:6], 16) / 255.0, a)


def load_config():
    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
        except Exception:
            pass
    return cfg


def merge_config(cfg):
    merged = DEFAULT_CONFIG.copy()
    for k, v in cfg.items():
        if k == "colors" and isinstance(v, dict):
            merged["colors"].update(v)
        else:
            merged[k] = v
    return merged


# ─── Shortcut management ───────────────────────────────────────────────

SHORTCUT_DIR = os.path.expanduser("~/.config/ghost-screen")
SHORTCUT_FILE = os.path.join(SHORTCUT_DIR, "shortcut.json")

_MOD_MAP = {
    "ctrl": "Ctrl", "control": "Ctrl", "shift": "Shift",
    "alt": "Alt", "super": "Super", "mod4": "Super",
    "mod1": "Alt", "primary": "Ctrl",
}


def parse_shortcut(combo):
    parts = combo.split("+")
    mods = []
    for p in parts[:-1]:
        pn = p.strip().lower()
        mods.append(_MOD_MAP.get(pn, p.strip()))
    key = parts[-1].strip()
    return mods, key


def _combo_to_gnome(mods, key):
    mm = {"Ctrl": "Control", "Alt": "Alt", "Shift": "Shift", "Super": "Super"}
    ms = "".join(f"<{mm.get(m, m)}>" for m in mods)
    return ms + (key.lower() if key.isalpha() else key)


def detect_de():
    de = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if any(x in de for x in ("gnome", "unity", "budgie", "cinnamon", "mate")):
        return "gnome" if shutil.which("gsettings") else None
    if any(x in de for x in ("kde", "plasma")):
        return "kde"
    if "xfce" in de:
        return "xfce"
    if "sway" in de:
        return "sway"
    if "hyprland" in de:
        return "hyprland"
    if "river" in de:
        return "river"
    if "cosmic" in de:
        return "cosmic"
    if any(x in de for x in ("deepin", "dde")):
        return "deepin" if shutil.which("gsettings") else None
    if any(x in de for x in ("lxqt", "lumina")):
        return "lxqt"
    return None


def _get_cmd_path():
    if "/" in sys.argv[0]:
        return os.path.abspath(sys.argv[0])
    w = shutil.which(sys.argv[0])
    return w or sys.argv[0]


def _save_shortcut_config(combo, de):
    os.makedirs(SHORTCUT_DIR, exist_ok=True)
    with open(SHORTCUT_FILE, "w") as f:
        json.dump({"shortcut": combo, "de": de}, f)


def _load_shortcut_config():
    if os.path.exists(SHORTCUT_FILE):
        try:
            with open(SHORTCUT_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _gnome(binding, cmd):
    schema = "org.gnome.settings-daemon.plugins.media-keys"
    try:
        cur = subprocess.run(["gsettings", "get", schema, "custom-keybindings"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception as e:
        return False, f"gsettings failed: {e}"
    import ast
    exist = ast.literal_eval(cur) if cur.startswith("[") else []
    found = None
    for p in exist:
        c = subprocess.run(["gsettings", "get", f"{schema}.custom-keybinding:{p}", "command"],
                           capture_output=True, text=True, timeout=5).stdout.strip().strip("'")
        if c == cmd:
            found = p
            break
    if found:
        subprocess.run(["gsettings", "set", f"{schema}.custom-keybinding:{found}", "binding", binding],
                       timeout=10)
        return True, f"Shortcut updated to {binding}"
    for i in range(100):
        p = f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{i}/"
        r = subprocess.run(["gsettings", "get", f"{schema}.custom-keybinding:{p}", "name"],
                           capture_output=True, text=True, timeout=5)
        if r.stdout.strip() in ("''", "@as []", "") or r.returncode != 0:
            subprocess.run(["gsettings", "set", f"{schema}.custom-keybinding:{p}", "name", "Ghost Screen"],
                           timeout=5)
            subprocess.run(["gsettings", "set", f"{schema}.custom-keybinding:{p}", "command", cmd],
                           timeout=5)
            subprocess.run(["gsettings", "set", f"{schema}.custom-keybinding:{p}", "binding", binding],
                           timeout=5)
            exist.append(p)
            subprocess.run(["gsettings", "set", schema, "custom-keybindings", str(exist)], timeout=5)
            return True, f"Shortcut set to {binding}"
    return False, "No empty GNOME custom keybinding slot found"


def _kde(combo_str, cmd):
    kw = shutil.which("kwriteconfig5")
    if not kw:
        return False, "kwriteconfig5 not found"
    try:
        subprocess.run([kw, "--file", os.path.expanduser("~/.config/kglobalshortcutsrc"),
                        "--group", "Ghost Screen", "--key", "Ghost Screen",
                        f"_launch {cmd}"], timeout=10)
        subprocess.run([kw, "--file", os.path.expanduser("~/.config/kglobalshortcutsrc"),
                        "--group", "Ghost Screen", "--key", "Ghost Screen",
                        combo_str], timeout=10)
        qd = shutil.which("qdbus")
        if qd:
            subprocess.run([qd, "org.kde.kglobalaccel", "/kglobalaccel",
                            "org.kde.KGlobalAccel.reloadConfig"], timeout=10)
    except Exception as e:
        return False, f"KDE shortcut failed: {e}"
    return True, f"Shortcut set to {combo_str}"


def _xfce(binding, cmd):
    xf = shutil.which("xfconf-query")
    if not xf:
        return False, "xfconf-query not found"
    alt = "-".join(binding.replace("<", "").replace(">", ""))
    try:
        r = subprocess.run([xf, "-c", "xfce4-keyboard-shortcuts", "-n", "-t", "string",
                            "-p", f"/commands/custom/{binding}", "-s", cmd],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return True, f"Shortcut set to {binding}"
        r = subprocess.run([xf, "-c", "xfce4-keyboard-shortcuts", "-n", "-t", "string",
                            "-p", f"/commands/custom/{alt}", "-s", cmd],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return True, f"Shortcut set to {alt}"
    except Exception as e:
        return False, f"XFCE shortcut failed: {e}"
    return False, "Could not set XFCE shortcut"


def _wlroots_cfg(de, key_text, line_gen):
    paths = {
        "sway": os.path.expanduser("~/.config/sway/config"),
        "hyprland": os.path.expanduser("~/.config/hypr/hyprland.conf"),
        "river": os.path.expanduser("~/.config/river/init"),
    }
    cfg = paths.get(de)
    if de == "sway" and (not cfg or not os.path.exists(cfg)):
        alt = os.path.expanduser("~/.config/i3/config")
        if os.path.exists(alt):
            cfg = alt
    if not cfg or not os.path.exists(cfg):
        return False, f"No {de} config found"
    cmd = _get_cmd_path()
    with open(cfg) as f:
        lines = f.readlines()
    filtered = [l for l in lines if cmd not in l and "Ghost Screen" not in l]
    new_line = line_gen(cmd)
    filtered.append(f"\n# Added by Ghost Screen installer — {key_text} toggles ghost overlay\n")
    filtered.append(f"{new_line}\n")
    with open(cfg, "w") as f:
        f.writelines(filtered)
    reload = {"sway": "swaymsg reload", "hyprland": "hyprctl reload",
              "river": "Restart River to activate"}.get(de, "")
    return True, f"Shortcut set to {key_text}\n    {reload}"


def _set_shortcut(combo):
    mods, key = parse_shortcut(combo)
    cmd = _get_cmd_path()
    de = detect_de()
    combo_str = "+".join(mods + [key])

    handlers = {}

    def _gnome_h():
        return _gnome(_combo_to_gnome(mods, key), cmd)

    def _deepin_h():
        return _gnome(_combo_to_gnome(mods, key), cmd)

    def _kde_h():
        return _kde(combo_str, cmd)

    def _xfce_h():
        return _xfce(_combo_to_gnome(mods, key), cmd)

    def _sway_h():
        k = key.lower() if key.isalpha() else key
        return _wlroots_cfg("sway", f"{'+'.join(mods)}+{k}",
                            lambda c: f"bindsym {'+'.join(mods)}+{k} exec {c}")

    def _hyprland_h():
        ms = ", ".join(mods)
        return _wlroots_cfg("hyprland", f"{ms}+{key}",
                            lambda c: f"bind = {ms}, {key}, exec, {c}")

    def _river_h():
        ms = " ".join(mods)
        return _wlroots_cfg("river", f"{ms}+{key}",
                            lambda c: f'riverctl map normal {ms} {key} spawn "{c}" &')

    def _lxqt_h():
        cfg = os.path.expanduser("~/.config/lxqt/globalkeyshortcuts.conf")
        if not os.path.exists(cfg):
            return False, "No LXQt config found"
        with open(cfg) as f:
            lines = f.readlines()
        filtered = [l for l in lines if cmd not in l and "[Ghost Screen]" not in l]
        filtered.append(f"\n[Ghost Screen]\nComment=\nExec={cmd}\nShortcut={combo_str}\n")
        with open(cfg, "w") as f:
            f.writelines(filtered)
        return True, f"Shortcut set to {combo_str}"

    def _xbindkeys_h():
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            return False, "xbindkeys does not work on native Wayland"
        xbk = shutil.which("xbindkeys")
        if not xbk:
            return False, "xbindkeys not found"
        xm = []
        for m in mods:
            ml = m.lower()
            if ml == "ctrl":
                xm.append("Control")
            elif ml == "alt":
                xm.append("Alt")
            elif ml == "shift":
                xm.append("Shift")
            elif ml == "super":
                xm.append("Mod4")
            else:
                xm.append(m)
        xk = key.lower() if key.isalpha() else key
        xc = "+".join(xm + [xk])
        xrc = os.path.expanduser("~/.xbindkeysrc")
        with open(xrc, "w") as f:
            f.write(f'"{cmd}"\n    {xc}\n')
        ad = os.path.expanduser("~/.config/autostart")
        os.makedirs(ad, exist_ok=True)
        with open(os.path.join(ad, "xbindkeys.desktop"), "w") as f:
            f.write("[Desktop Entry]\nType=Application\nName=xbindkeys\n"
                    f"Comment=Global keyboard shortcuts (Ghost Screen)\n"
                    f"Exec=xbindkeys\nTerminal=false\n")
        subprocess.run(["pkill", "xbindkeys"], capture_output=True, timeout=5)
        subprocess.run([xbk], timeout=5)
        return True, f"Shortcut set to {xc}"

    handlers = {
        "gnome": _gnome_h, "deepin": _deepin_h, "kde": _kde_h,
        "xfce": _xfce_h, "sway": _sway_h, "hyprland": _hyprland_h,
        "river": _river_h, "lxqt": _lxqt_h,
    }

    if de and de in handlers:
        ok, msg = handlers[de]()
    elif de == "cosmic":
        return False, "COSMIC desktop not yet supported for --shortcut"
    else:
        ok, msg = _xbindkeys_h() if os.environ.get("XDG_SESSION_TYPE") != "wayland" \
            else (False, "Could not detect desktop environment")

    if ok:
        _save_shortcut_config(combo_str, de or "x11")
    return ok, msg


# ─── Wayland input inhibition (GNOME: DBus Eval + keyboard shortcuts inhibitor) ─


def _gnome_eval(code):
    try:
        subprocess.run(["gdbus", "call", "--session", "--dest", "org.gnome.Shell",
                        "--object-path", "/org/gnome/Shell", "--method",
                        "org.gnome.Shell.Eval", code],
                       capture_output=True, timeout=5)
        return True
    except Exception:
        return False


def _inhibit_gnome_shortcuts():
    de = os.environ.get("XDG_SESSION_TYPE") == "wayland" and detect_de() == "gnome"
    if not de:
        return False
    keys = ["overview-key", "switch-applications", "switch-windows",
            "switch-group", "switch-panels", "panel-main-menu",
            "focus-active-notification", "toggle-recording",
            "maximize", "unmaximize", "close"]
    cmds = [f'Main.wm.allowKeybinding("{k}", false);' for k in keys]
    cmds.append('Main.overview.animationDuration = 99999;')
    for c in cmds:
        _gnome_eval(c)
    return True


def _restore_gnome_shortcuts():
    keys = ["overview-key", "switch-applications", "switch-windows",
            "switch-group", "switch-panels", "panel-main-menu",
            "focus-active-notification", "toggle-recording",
            "maximize", "unmaximize", "close"]
    cmds = [f'Main.wm.allowKeybinding("{k}", true);' for k in keys]
    cmds.append('Main.overview.animationDuration = 250;')
    for c in cmds:
        _gnome_eval(c)


_GSETTINGS_SAVED = {}

def _gsettings_save(schema, key):
    try:
        r = subprocess.run(["gsettings", "get", schema, key],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            _GSETTINGS_SAVED[(schema, key)] = r.stdout.strip()
            return True
    except Exception:
        pass
    return False

def _gsettings_restore_all():
    for (schema, key), val in _GSETTINGS_SAVED.items():
        try:
            subprocess.run(["gsettings", "set", schema, key, val],
                           capture_output=True, timeout=5)
        except Exception:
            pass
    _GSETTINGS_SAVED.clear()

def _inhibit_touchpad():
    """Disable touchpad via gsettings while ghost is active.
       This is the only way to block touch gestures on Wayland without
       ext-session-lock protocol (which GNOME 46 does not advertise)."""
    de = os.environ.get("XDG_SESSION_TYPE") == "wayland" and detect_de() == "gnome"
    if not de:
        return False
    schema = "org.gnome.desktop.peripherals.touchpad"
    if _gsettings_save(schema, "send-events"):
        subprocess.run(["gsettings", "set", schema, "send-events", "disabled"],
                       capture_output=True, timeout=5)
        return True
    return False

def _restore_touchpad():
    _gsettings_restore_all()


class WaylandShortcutBlocker:
    _lib = None

    @classmethod
    def _ensure_lib(cls):
        if cls._lib is not None:
            return cls._lib
        import ctypes, os
        d = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(d, "wl_inhibit.so")
        if os.path.exists(lib_path):
            cls._lib = ctypes.CDLL(lib_path)
            cls._lib.ghost_inhibit_start.restype = ctypes.c_void_p
            cls._lib.ghost_inhibit_start.argtypes = []
            cls._lib.ghost_inhibit_stop.argtypes = [ctypes.c_void_p]
            cls._lib.ghost_inhibit_is_active.argtypes = [ctypes.c_void_p]
            cls._lib.ghost_inhibit_is_active.restype = ctypes.c_int
            return cls._lib
        return None

    def __init__(self):
        self._state = None
        lib = self._ensure_lib()
        if lib:
            self._state = lib.ghost_inhibit_start()

    @property
    def active(self):
        if not self._state:
            return False
        return bool(self._ensure_lib().ghost_inhibit_is_active(self._state))

    def destroy(self):
        if self._state:
            lib = self._ensure_lib()
            if lib:
                lib.ghost_inhibit_stop(self._state)
            self._state = None


# ─── Shared base class ─────────────────────────────────────────────────

def _get_toggle_combo():
    return _load_shortcut_config().get("shortcut", "Ctrl+3")


def _combo_to_tk_event(combo):
    mods, key = parse_shortcut(combo)
    tk_map = {"ctrl": "Control", "shift": "Shift", "alt": "Alt", "super": "Mod4"}
    tk_mods = [tk_map.get(m.lower()) for m in mods]
    if None in tk_mods:
        return None
    tk_key = key.lower() if key.isalpha() else key
    return f"<{' -'.join(tk_mods)}-Key-{tk_key}>"


class GhostScreen:
    def __init__(self, cfg=None, no_sleep=False):
        raw = load_config()
        raw.update(cfg or {})
        self.cfg = merge_config(raw)
        self.time = 0.0
        self.sw, self.sh = 0, 0
        self._backend = "x11"
        self._quit = False
        self._inhibitor = None
        self._grab_active = False
        if no_sleep:
            self._acquire_inhibitor()

    def _init_particles(self):
        return [{
            "x": random.uniform(0, self.sw),
            "y": random.uniform(0, self.sh),
            "vx": random.uniform(-0.4, 0.4),
            "vy": random.uniform(-0.5, -0.15),
            "size": random.uniform(1.5, 3.5),
            "phase": random.uniform(0, 2 * math.pi),
        } for _ in range(self.cfg["particle_count"])]

    def _update_particles(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < -20:
                p["y"] = self.sh + 20
                p["x"] = random.uniform(0, self.sw)
            if p["x"] < -20 or p["x"] > self.sw + 20:
                p["x"] = random.uniform(0, self.sw)

    def _update(self):
        self.time += self.cfg["frame_delay"] / 1000.0
        self._update_particles()

    def _write_pid(self):
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))

    def _cleanup_pid(self):
        try:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
        except OSError:
            pass
        self._release_inhibitor()

    def _acquire_inhibitor(self):
        import subprocess
        try:
            self._inhibitor = subprocess.Popen(
                ["systemd-inhibit", "--what=sleep", "--who=Ghost Screen",
                 "--why=Ghost overlay is active", "--mode=block", "cat"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            self._inhibitor = None

    def _release_inhibitor(self):
        if self._inhibitor is not None:
            try:
                self._inhibitor.stdin.close()
                self._inhibitor.wait(timeout=2)
            except Exception:
                try:
                    self._inhibitor.kill()
                except Exception:
                    pass
            self._inhibitor = None

    def run(self):
        raise NotImplementedError


# ─── Tkinter backend (X11) ────────────────────────────────────────────

class TkinterGhostScreen(GhostScreen):
    def __init__(self, cfg=None, no_sleep=False):
        super().__init__(cfg, no_sleep=no_sleep)
        self._backend = "x11"
        self._root = None
        self._canvas = None
        signal.signal(signal.SIGTERM, lambda *_: self._signal_quit())

    def _signal_quit(self):
        self._quit = True
        if self._root is not None:
            try:
                self._root.quit()
            except Exception:
                pass

    def _create_window(self):
        import tkinter as tk
        self._root = tk.Tk()
        self._root.title(PROJECT)
        self._root.attributes("-fullscreen", True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", self.cfg["opacity"])
        self._root.overrideredirect(True)
        self.sw = self._root.winfo_screenwidth()
        self.sh = self._root.winfo_screenheight()

        self._canvas = tk.Canvas(
            self._root, width=self.sw, height=self.sh,
            highlightthickness=0, bg=self.cfg["colors"]["bg"],
        )
        self._canvas.pack()

        self._root.protocol("WM_DELETE_WINDOW", self._on_window_destroy)
        self._root.bind("<Destroy>", self._on_window_destroy)

        if not hasattr(self, 'particles') or not self.particles:
            self.particles = self._init_particles()
            self._write_pid()

        self._grab_input()
        self._after_id = self._root.after(100, self._draw)

    def _grab_input(self):
        try:
            self._root.grab_set_global()
            self._grab_active = True
        except Exception:
            self._grab_active = False
            return
        combo = _get_toggle_combo()
        tk_ev = _combo_to_tk_event(combo)
        if tk_ev:
            self._root.bind(tk_ev, self._on_toggle_key)
        self._root.bind("<Key>", self._on_blocked_key)
        self._root.bind("<Button>", self._on_blocked_key)
        self._root.bind("<Motion>", self._on_blocked_key)

    def _on_blocked_key(self, event):
        return "break"

    def _on_toggle_key(self, event):
        self._quit = True
        self._grab_active = False
        root = self._root
        if root is not None:
            try:
                root.grab_release()
            except Exception:
                pass
        self._cleanup_pid()
        self._on_window_destroy()
        if root is not None:
            try:
                root.quit()
            except Exception:
                pass
        return "break"

    def _on_window_destroy(self, event=None):
        if event is not None:
            w = getattr(event, 'widget', None)
            if w is not None and str(w) != '.':
                return
        self._root = None
        self._canvas = None
        self._after_id = None

    def _draw(self):
        if self._quit or self._root is None:
            return

        try:
            self._canvas.delete("all")
        except Exception:
            return

        self._update()
        t = self.time
        c = self.cfg["colors"]
        cx, cy = self.sw // 2, self.sh // 2
        float_y = math.sin(t * 2) * self.cfg["float_amplitude"]
        gy = cy + float_y
        scale = min(self.sw, self.sh) * self.cfg["ghost_scale"]

        self._draw_vignette()
        self._draw_grid(t, cx, cy, c["grid"])
        self._draw_rings(t, cx, gy, scale, c)
        self._draw_ghost(t, cx, gy, scale, c)
        self._draw_particles(t, c["particle"], c["primary"])
        self._draw_hud(t, cx, gy, scale, c["accent"])

        if self._quit or self._root is None:
            return
        try:
            self._after_id = self._root.after(self.cfg["frame_delay"], self._draw)
        except Exception:
            pass

    def _draw_vignette(self):
        w, h = self.sw, self.sh
        for i in range(5):
            r = 1 - i * 0.15
            self._canvas.create_rectangle(
                w*(1-r)/2, h*(1-r)/2, w*(1+r)/2, h*(1+r)/2,
                outline="", fill=f"#00000{i}",
            )

    def _draw_grid(self, t, cx, cy, color):
        spacing = 60
        off = (t * 8) % spacing
        for x in range(int(cx % spacing), self.sw, spacing):
            self._canvas.create_line(x+off, 0, x+off, self.sh, fill=color, width=1)
        for y in range(int(cy % spacing), self.sh, spacing):
            self._canvas.create_line(0, y+off, self.sw, y+off, fill=color, width=1)

    def _draw_rings(self, t, cx, cy, scale, c):
        radii = [scale*1.8, scale*2.3, scale*2.8]
        colors = [c["primary"], c["secondary"], c["accent"]]
        speeds = [0.3, -0.2, 0.15]
        segs = 48
        gap = 6
        for r, col, sp in zip(radii, colors, speeds):
            angle = t * sp
            for j in range(0, segs, gap):
                a1 = angle + (j/segs) * 2 * math.pi
                a2 = angle + ((j+gap-1)/segs) * 2 * math.pi
                self._canvas.create_arc(
                    cx-r, cy-r, cx+r, cy+r,
                    start=math.degrees(a1),
                    extent=math.degrees(a2-a1),
                    outline=col, width=1, style="arc",
                )
        for j in range(4):
            a = t*0.2 + j*math.pi/2
            x1 = cx + radii[0]*math.cos(a)
            y1 = cy + radii[0]*math.sin(a)
            x2 = cx + radii[2]*math.cos(a)
            y2 = cy + radii[2]*math.sin(a)
            self._canvas.create_line(
                x1, y1, x2, y2,
                fill=c["accent"], width=1, dash=(3, 6),
            )

    def _draw_ghost(self, t, cx, cy, scale, c):
        pts = []
        for px, py in GHOST_POLYGON:
            pts.append(cx + px * scale)
            pts.append(cy + py * scale)
        self._canvas.create_polygon(
            pts, fill=c["ghost_fill"], outline=c["ghost_outline"], width=2,
        )

        for i, path in enumerate(CIRCUIT_PATHS):
            col = c["primary"] if i % 2 == 0 else c["secondary"]
            for j in range(len(path) - 1):
                self._canvas.create_line(
                    cx + path[j][0]*scale, cy + path[j][1]*scale,
                    cx + path[j+1][0]*scale, cy + path[j+1][1]*scale,
                    fill=col, width=1.5,
                )
            for px, py in path:
                self._canvas.create_oval(
                    cx + px*scale - 3, cy + py*scale - 3,
                    cx + px*scale + 3, cy + py*scale + 3,
                    fill=col, outline="",
                )

        r = scale * 0.18
        angle = t * 2
        pts = []
        for i in range(8):
            a = angle + i * math.pi/4
            pts.extend([cx + r*math.cos(a), cy + r*math.sin(a)])
        self._canvas.create_polygon(
            pts, outline=c["secondary"], fill=c["ghost_fill"], width=2,
        )
        self._canvas.create_oval(
            cx - r*0.4, cy - r*0.4, cx + r*0.4, cy + r*0.4,
            fill=c["primary"], outline="",
        )

        eye_y = cy - scale * 0.28
        spread = scale * 0.18
        pulse = 1 + 0.15 * math.sin(t * 3)
        for side in [-1, 1]:
            ex = cx + side * spread
            eye_r = 6 * pulse
            pts = []
            for i in range(6):
                a = i * math.pi/3 + t * 0.5
                pts.extend([ex + eye_r*math.cos(a), eye_y + eye_r*math.sin(a)])
            self._canvas.create_polygon(pts, fill=c["primary"], outline="")

        for i in range(3):
            gr = scale * 0.7 * (1 + i * 0.15)
            self._canvas.create_oval(
                cx - gr, cy - gr, cx + gr, cy + gr,
                outline=c["glow"], width=1,
            )

    def _draw_particles(self, t, color, glow_color):
        for p in self.particles:
            twinkle = 0.5 + 0.5 * math.sin(t * 3 + p["phase"])
            sz = p["size"] * twinkle
            self._canvas.create_oval(
                p["x"] - sz, p["y"] - sz, p["x"] + sz, p["y"] + sz,
                fill=color, outline="",
            )
            self._canvas.create_oval(
                p["x"] - sz*0.5, p["y"] - sz*0.5,
                p["x"] + sz*0.5, p["y"] + sz*0.5,
                fill=glow_color, outline="",
            )

    def _draw_hud(self, t, cx, cy, scale, color):
        spread = scale * 2.0
        sz = scale * 0.15
        corners = [
            (cx-spread, cy-spread, 1, 1),
            (cx+spread, cy-spread, -1, 1),
            (cx-spread, cy+spread, 1, -1),
            (cx+spread, cy+spread, -1, -1),
        ]
        for x, y, dx, dy in corners:
            self._canvas.create_line(x, y+sz*dy, x, y, fill=color, width=1)
            self._canvas.create_line(x, y, x+sz*dx, y, fill=color, width=1)
        scan_y = (t * 60) % self.sh
        self._canvas.create_line(0, scan_y, self.sw, scan_y, fill=color, width=1)

    def run(self):
        self._create_window()
        while not self._quit:
            try:
                self._root.mainloop()
            except Exception:
                pass
            if self._quit:
                break
            if self._root is None:
                self._create_window()
        self._cleanup_pid()


# ─── GTK3 backend (Wayland + X11, uses Pillow + GdkPixbuf) ─────────────

def _hex_to_rgba_pil(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def _draw_dashed_line(draw, x1, y1, x2, y2, color, width=1, dash=3, gap=6):
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    if length < 0.5:
        return
    dx /= length
    dy /= length
    pos = 0.0
    while pos < length:
        end = min(pos + dash, length)
        draw.line([
            (x1 + dx * pos, y1 + dy * pos),
            (x1 + dx * end, y1 + dy * end),
        ], fill=color, width=width)
        pos += dash + gap


class GtkGhostScreen(GhostScreen):
    def __init__(self, cfg=None, no_sleep=False):
        super().__init__(cfg, no_sleep=no_sleep)
        self._backend = "wayland"
        self._window = None
        self._image = None
        self._GdkPixbuf = None
        self._GLib = None
        self._shortcut_blocker = None
        self._gnome_restore = False
        self._touchpad_disabled = False
        self._toggle_mods = 0
        self._toggle_keyval = 0
        self._init_toggle_key()
        signal.signal(signal.SIGTERM, lambda *_: self._signal_quit())
        self._init_once()
        self._create_window()
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import GLib
        GLib.timeout_add(self.cfg["frame_delay"], self._tick)

    def _init_toggle_key(self):
        import gi
        gi.require_version("Gdk", "3.0")
        from gi.repository import Gdk
        combo = _get_toggle_combo()
        mods, key = parse_shortcut(combo)
        mod_map = {"Ctrl": Gdk.ModifierType.CONTROL_MASK,
                   "Control": Gdk.ModifierType.CONTROL_MASK,
                   "Alt": Gdk.ModifierType.MOD1_MASK,
                   "Shift": Gdk.ModifierType.SHIFT_MASK,
                   "Super": Gdk.ModifierType.SUPER_MASK}
        mask = 0
        for m in mods:
            gdk_mod = mod_map.get(m)
            if gdk_mod:
                mask |= gdk_mod
        self._toggle_mods = mask
        self._toggle_keyval = Gdk.keyval_from_name(key)

    def _init_once(self):
        import gi
        gi.require_version("Gdk", "3.0")
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gdk, Gtk, GLib, GdkPixbuf
        self._GdkPixbuf = GdkPixbuf
        self._GLib = GLib

        display = Gdk.Display.get_default()
        if display:
            mon = (display.get_monitor(0) or
                   (getattr(display, "get_primary_monitor", lambda: None)()))
            if mon:
                geo = mon.get_geometry()
                self.sw, self.sh = geo.width, geo.height
        if not self.sw:
            self.sw, self.sh = 1920, 1080

        self.particles = self._init_particles()
        self._write_pid()

    def _create_window(self):
        import gi
        gi.require_version("Gdk", "3.0")
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gdk, Gtk

        self._window = Gtk.Window()
        self._window.set_title(PROJECT)
        self._window.set_app_paintable(True)
        self._window.set_keep_above(True)
        self._window.fullscreen()

        screen = self._window.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self._window.set_visual(visual)

        self._image = Gtk.Image()
        self._window.add(self._image)
        self._window.show_all()

        self._window.connect("destroy", self._on_window_destroy)
        self._grab_input()

    def _grab_input(self):
        import gi
        gi.require_version("Gdk", "3.0")
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gdk, Gtk

        # 1. Try keyboard shortcuts inhibitor (C .so helper, Wayland protocol)
        try:
            blk = WaylandShortcutBlocker()
            if blk._state:
                self._shortcut_blocker = blk
        except Exception:
            pass

        # 2. Disable touchpad (blocks ALL touchpad input including gestures)
        if _inhibit_touchpad():
            self._touchpad_disabled = True

        # 3. Try GNOME Shell Eval (blocks Super key, Alt+Tab)
        if not self._shortcut_blocker:
            if _inhibit_gnome_shortcuts():
                self._gnome_restore = True

        # 3. Seat grab (blocks client-level input)
        try:
            gdk_win = self._window.get_window()
            if not gdk_win:
                return
            display = gdk_win.get_display()
            seat = display.get_default_seat()
            status = seat.grab(
                gdk_win, Gdk.SeatCapabilities.ALL,
                True, None, None, None,
            )
            self._grab_active = (status == Gdk.GrabStatus.SUCCESS)
            if self._grab_active:
                self._window.connect("key-press-event", self._on_consume)
                self._window.connect("key-release-event", self._on_consume)
                self._window.connect("button-press-event", self._on_consume)
                self._window.connect("button-release-event", self._on_consume)
                self._window.connect("scroll-event", self._on_consume)
                self._window.connect("motion-notify-event", self._on_consume)
                self._window.connect("touch-event", self._on_consume)
        except Exception:
            self._grab_active = False

    def _on_consume(self, widget, event):
        import gi
        gi.require_version("Gdk", "3.0")
        from gi.repository import Gdk
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == self._toggle_keyval:
                state = event.state & Gdk.ModifierType.MODIFIER_MASK
                if state == self._toggle_mods:
                    self._toggle_off()
                    return True
        return True

    def _toggle_off(self):
        self._cleanup_inhibition()
        self._cleanup_pid()
        self._quit = True

    def _on_window_destroy(self, *args):
        self._cleanup_inhibition()
        self._window = None
        self._image = None

    def _signal_quit(self):
        self._cleanup_inhibition()
        self._quit = True

    def _cleanup_inhibition(self):
        if self._touchpad_disabled:
            _restore_touchpad()
            self._touchpad_disabled = False
        if self._gnome_restore:
            _restore_gnome_shortcuts()
            self._gnome_restore = False
        if self._shortcut_blocker:
            self._shortcut_blocker.destroy()
            self._shortcut_blocker = None

    def _tick(self):
        if self._quit:
            self._cleanup_pid()
            import gi
            gi.require_version("Gtk", "3.0")
            from gi.repository import Gtk
            Gtk.main_quit()
            return False

        if self._window is None:
            try:
                self._create_window()
            except Exception:
                pass
            return True

        self._update()
        t = self.time
        c = self.cfg["colors"]
        cx, cy = self.sw // 2, self.sh // 2
        float_y = math.sin(t * 2) * self.cfg["float_amplitude"]
        gy = cy + float_y
        scale = min(self.sw, self.sh) * self.cfg["ghost_scale"]

        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (self.sw, self.sh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        self._draw_vignette(draw, t, c)
        self._draw_grid(draw, t, cx, cy, c["grid"])
        self._draw_rings(draw, t, cx, gy, scale, c)
        self._draw_ghost(draw, t, cx, gy, scale, c)
        self._draw_particles(draw, t, c["particle"], c["primary"])
        self._draw_hud(draw, t, cx, gy, scale, c["accent"])

        pb = self._GdkPixbuf.Pixbuf.new_from_bytes(
            self._GLib.Bytes.new(img.tobytes()),
            self._GdkPixbuf.Colorspace.RGB, True, 8,
            self.sw, self.sh, self.sw * 4,
        )
        self._image.set_from_pixbuf(pb)

        return True

    def run(self):
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        Gtk.main()

    # ── Drawing helpers ───────────────────────────────────────────

    def _draw_vignette(self, draw, t, c):
        w, h = self.sw, self.sh
        for i in range(5):
            r = 1 - i * 0.15
            alpha = int(i * 0.03 * self.cfg["opacity"] * 255)
            x0 = int(w * (1 - r) / 2)
            y0 = int(h * (1 - r) / 2)
            x1 = int(w * (1 + r) / 2)
            y1 = int(h * (1 + r) / 2)
            draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, alpha))

    def _draw_grid(self, draw, t, cx, cy, color):
        spacing = 60
        off = (t * 8) % spacing
        col = _hex_to_rgba_pil(color, 76)
        for x in range(int(cx % spacing), self.sw, spacing):
            draw.line([(x + off, 0), (x + off, self.sh)], fill=col, width=1)
        for y in range(int(cy % spacing), self.sh, spacing):
            draw.line([(0, y + off), (self.sw, y + off)], fill=col, width=1)

    def _draw_rings(self, draw, t, cx, cy, scale, c):
        radii = [scale * 1.8, scale * 2.3, scale * 2.8]
        colors = [c["primary"], c["secondary"], c["accent"]]
        speeds = [0.3, -0.2, 0.15]
        segs = 48
        gap = 6
        op = self.cfg["opacity"]
        for r, col, sp in zip(radii, colors, speeds):
            angle = t * sp
            pil_col = _hex_to_rgba_pil(col, int(op * 255))
            for j in range(0, segs, gap):
                a1 = math.degrees(angle + (j / segs) * 2 * math.pi)
                a2 = math.degrees(angle + ((j + gap - 1) / segs) * 2 * math.pi)
                draw.arc([cx - r, cy - r, cx + r, cy + r], a1, a2, fill=pil_col, width=1)
        accent_col = _hex_to_rgba_pil(c["accent"], int(op * 0.6 * 255))
        for j in range(4):
            a = t * 0.2 + j * math.pi / 2
            x1 = cx + radii[0] * math.cos(a)
            y1 = cy + radii[0] * math.sin(a)
            x2 = cx + radii[2] * math.cos(a)
            y2 = cy + radii[2] * math.sin(a)
            _draw_dashed_line(draw, x1, y1, x2, y2, accent_col, width=1, dash=3, gap=6)

    def _draw_ghost(self, draw, t, cx, cy, scale, c):
        op = self.cfg["opacity"]
        ghost_pts = [(cx + px * scale, cy + py * scale) for px, py in GHOST_POLYGON]
        draw.polygon(
            ghost_pts,
            fill=_hex_to_rgba_pil(c["ghost_fill"], int(op * 0.9 * 255)),
            outline=_hex_to_rgba_pil(c["ghost_outline"], int(op * 255)),
        )

        for i, path in enumerate(CIRCUIT_PATHS):
            col = c["primary"] if i % 2 == 0 else c["secondary"]
            pil_col = _hex_to_rgba_pil(col, int(op * 255))
            for j in range(len(path) - 1):
                draw.line([
                    (cx + path[j][0] * scale, cy + path[j][1] * scale),
                    (cx + path[j + 1][0] * scale, cy + path[j + 1][1] * scale),
                ], fill=pil_col, width=2)
            for px, py in path:
                x, y = cx + px * scale, cy + py * scale
                draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=pil_col)

        r = scale * 0.18
        angle = t * 2
        core_pts = [
            (cx + r * math.cos(angle + i * math.pi / 4),
             cy + r * math.sin(angle + i * math.pi / 4))
            for i in range(8)
        ]
        draw.polygon(
            core_pts,
            fill=_hex_to_rgba_pil(c["ghost_fill"], int(op * 255)),
            outline=_hex_to_rgba_pil(c["secondary"], int(op * 255)),
        )
        draw.ellipse(
            [cx - r * 0.4, cy - r * 0.4, cx + r * 0.4, cy + r * 0.4],
            fill=_hex_to_rgba_pil(c["primary"], int(op * 255)),
        )

        eye_y = cy - scale * 0.28
        spread = scale * 0.18
        pulse = 1 + 0.15 * math.sin(t * 3)
        for side in [-1, 1]:
            ex = cx + side * spread
            eye_r = 6 * pulse
            eye_pts = [
                (ex + eye_r * math.cos(i * math.pi / 3 + t * 0.5),
                 eye_y + eye_r * math.sin(i * math.pi / 3 + t * 0.5))
                for i in range(6)
            ]
            draw.polygon(eye_pts, fill=_hex_to_rgba_pil(c["primary"], int(op * 255)))

        for i in range(3):
            gr = scale * 0.7 * (1 + i * 0.15)
            draw.ellipse(
                [cx - gr, cy - gr, cx + gr, cy + gr],
                outline=_hex_to_rgba_pil(c["glow"], int(op * 0.15 * 255)),
                width=1,
            )

    def _draw_particles(self, draw, t, color, glow_color):
        for p in self.particles:
            twinkle = 0.5 + 0.5 * math.sin(t * 3 + p["phase"])
            sz = p["size"] * twinkle
            col = _hex_to_rgba_pil(color, int(twinkle * 255))
            glow = _hex_to_rgba_pil(glow_color, int(twinkle * 0.3 * 255))
            draw.ellipse(
                [p["x"] - sz, p["y"] - sz, p["x"] + sz, p["y"] + sz],
                fill=col,
            )
            draw.ellipse(
                [p["x"] - sz * 0.5, p["y"] - sz * 0.5,
                 p["x"] + sz * 0.5, p["y"] + sz * 0.5],
                fill=glow,
            )

    def _draw_hud(self, draw, t, cx, cy, scale, color):
        spread = scale * 2.0
        sz = scale * 0.15
        col = _hex_to_rgba_pil(color, 128)
        corners = [
            (cx - spread, cy - spread, 1, 1),
            (cx + spread, cy - spread, -1, 1),
            (cx - spread, cy + spread, 1, -1),
            (cx + spread, cy + spread, -1, -1),
        ]
        for x, y, dx, dy in corners:
            draw.line([(x, y + sz * dy), (x, y)], fill=col, width=1)
            draw.line([(x, y), (x + sz * dx, y)], fill=col, width=1)
        scan_y = (t * 60) % self.sh
        draw.line([(0, scan_y), (self.sw, scan_y)], fill=col, width=1)

# ─── Factory ───────────────────────────────────────────────────────────

def create_ghost_screen(cfg=None, no_sleep=False):
    display_type = os.environ.get("XDG_SESSION_TYPE", "x11")
    if display_type == "wayland":
        try:
            from PIL import Image, ImageDraw
            return GtkGhostScreen(cfg, no_sleep=no_sleep)
        except ImportError:
            print("Pillow not installed; install python3-pil for Wayland transparency.")
        except Exception as e:
            print(f"Wayland backend failed ({e}), falling back to X11.")
    return TkinterGhostScreen(cfg, no_sleep=no_sleep)


def check_deps():
    ok = True
    display_type = os.environ.get("XDG_SESSION_TYPE", "x11")

    try:
        import tkinter as tk
        r = tk.Tk()
        r.destroy()
        print(f"  [X11]  tkinter: OK")
    except Exception as e:
        print(f"  [X11]  tkinter: MISSING ({e})")
        ok = False

    if display_type == "wayland":
        try:
            import gi
            gi.require_version("Gtk", "3.0")
            gi.require_version("Gdk", "3.0")
            from gi.repository import Gtk, Gdk
            print(f"  [WL]   GTK3 GI:  OK")
        except Exception as e:
            print(f"  [WL]   GTK3 GI:  MISSING ({e})")
            ok = False

        try:
            from PIL import Image
            print(f"  [WL]   Pillow:   OK  (PIL {Image.__version__})")
        except ImportError:
            print(f"  [WL]   Pillow:   MISSING (install python3-pil)")
            ok = False

    if ok:
        print(f"\n  All dependencies satisfied.")
    else:
        print(f"\n  Some dependencies missing — see above.")
    sys.exit(0 if ok else 1)


def main():
    parser = argparse.ArgumentParser(description=f"{PROJECT} v{VERSION}")
    parser.add_argument("--kill", "-k", action="store_true", help="Kill running instance")
    parser.add_argument("--version", "-v", action="store_true", help="Show version")
    parser.add_argument("--check", "-c", action="store_true", help="Check dependencies")
    parser.add_argument("--no-sleep", "-n", action="store_true",
                        help="Prevent PC sleep while ghost is active")
    parser.add_argument("--shortcut", "-s", type=str, metavar="COMBO",
                        help="Set keyboard shortcut (e.g. Ctrl+Shift+G)")
    args = parser.parse_args()

    if args.shortcut:
        ok, msg = _set_shortcut(args.shortcut)
        print(msg)
        sys.exit(0 if ok else 1)

    if args.version:
        print(f"{PROJECT} v{VERSION}")
        sys.exit(0)

    if args.check:
        check_deps()

    if args.kill:
        kill_ghost()
        sys.exit(0)

    if is_running():
        kill_ghost()
        print("Ghost screen dismissed.")
    else:
        atexit.register(_restore_touchpad)
        if args.no_sleep:
            print("  Prevent sleep enabled — system will not suspend\n"
                  "  while Ghost Screen is active. Toggle off to allow sleep.")
        try:
            app = create_ghost_screen(no_sleep=args.no_sleep)
            app.run()
        except KeyboardInterrupt:
            print()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
