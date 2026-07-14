#!/usr/bin/env python3

import math
import random
import os
import sys
import signal
import argparse
import json

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


# ─── Shared base class ─────────────────────────────────────────────────

class GhostScreen:
    def __init__(self, cfg=None):
        raw = load_config()
        raw.update(cfg or {})
        self.cfg = merge_config(raw)
        self.time = 0.0
        self.sw, self.sh = 0, 0
        self._backend = "x11"

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

    def run(self):
        raise NotImplementedError


# ─── Tkinter backend (X11) ────────────────────────────────────────────

class TkinterGhostScreen(GhostScreen):
    def __init__(self, cfg=None):
        import tkinter as tk
        super().__init__(cfg)
        self._backend = "x11"

        self.root = tk.Tk()
        self.root.title(PROJECT)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.cfg["opacity"])
        self.root.overrideredirect(True)
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(
            self.root, width=self.sw, height=self.sh,
            highlightthickness=0, bg=self.cfg["colors"]["bg"],
        )
        self.canvas.pack()

        self.particles = self._init_particles()
        self._write_pid()
        signal.signal(signal.SIGTERM, lambda *_: os._exit(0))

    def draw(self):
        self.canvas.delete("all")
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

        self.root.after(self.cfg["frame_delay"], self.draw)

    def _draw_vignette(self):
        w, h = self.sw, self.sh
        for i in range(5):
            r = 1 - i * 0.15
            self.canvas.create_rectangle(
                w*(1-r)/2, h*(1-r)/2, w*(1+r)/2, h*(1+r)/2,
                outline="", fill=f"#00000{i}",
            )

    def _draw_grid(self, t, cx, cy, color):
        spacing = 60
        off = (t * 8) % spacing
        for x in range(int(cx % spacing), self.sw, spacing):
            self.canvas.create_line(x+off, 0, x+off, self.sh, fill=color, width=1)
        for y in range(int(cy % spacing), self.sh, spacing):
            self.canvas.create_line(0, y+off, self.sw, y+off, fill=color, width=1)

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
                self.canvas.create_arc(
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
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=c["accent"], width=1, dash=(3, 6),
            )

    def _draw_ghost(self, t, cx, cy, scale, c):
        pts = []
        for px, py in GHOST_POLYGON:
            pts.append(cx + px * scale)
            pts.append(cy + py * scale)
        self.canvas.create_polygon(
            pts, fill=c["ghost_fill"], outline=c["ghost_outline"], width=2,
        )

        for i, path in enumerate(CIRCUIT_PATHS):
            col = c["primary"] if i % 2 == 0 else c["secondary"]
            for j in range(len(path) - 1):
                self.canvas.create_line(
                    cx + path[j][0]*scale, cy + path[j][1]*scale,
                    cx + path[j+1][0]*scale, cy + path[j+1][1]*scale,
                    fill=col, width=1.5,
                )
            for px, py in path:
                self.canvas.create_oval(
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
        self.canvas.create_polygon(
            pts, outline=c["secondary"], fill=c["ghost_fill"], width=2,
        )
        self.canvas.create_oval(
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
            self.canvas.create_polygon(pts, fill=c["primary"], outline="")

        for i in range(3):
            gr = scale * 0.7 * (1 + i * 0.15)
            self.canvas.create_oval(
                cx - gr, cy - gr, cx + gr, cy + gr,
                outline=c["glow"], width=1,
            )

    def _draw_particles(self, t, color, glow_color):
        for p in self.particles:
            twinkle = 0.5 + 0.5 * math.sin(t * 3 + p["phase"])
            sz = p["size"] * twinkle
            self.canvas.create_oval(
                p["x"] - sz, p["y"] - sz, p["x"] + sz, p["y"] + sz,
                fill=color, outline="",
            )
            self.canvas.create_oval(
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
            self.canvas.create_line(x, y+sz*dy, x, y, fill=color, width=1)
            self.canvas.create_line(x, y, x+sz*dx, y, fill=color, width=1)
        scan_y = (t * 60) % self.sh
        self.canvas.create_line(0, scan_y, self.sw, scan_y, fill=color, width=1)

    def run(self):
        self.root.after(100, self.draw)
        self.root.mainloop()


# ─── GTK3 backend (Wayland + X11) ─────────────────────────────────────

class GtkGhostScreen(GhostScreen):
    def __init__(self, cfg=None):
        super().__init__(cfg)
        self._backend = "wayland"
        self._setup_gtk()

    def _setup_gtk(self):
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("Gdk", "3.0")
        gi.require_version("cairo", "1.0")
        from gi.repository import Gtk, Gdk, GLib, cairo
        self._OP_SOURCE = cairo.Operator.SOURCE
        self._OP_OVER = cairo.Operator.OVER

        display = Gdk.Display.get_default()
        if display:
            mon = (display.get_monitor(0) or
                   (getattr(display, "get_primary_monitor", lambda: None)()))
            if mon:
                geo = mon.get_geometry()
                self.sw, self.sh = geo.width, geo.height
        if not self.sw:
            self.sw, self.sh = 1920, 1080  # fallback

        self.win = Gtk.Window()
        self.win.set_title(PROJECT)
        self.win.set_app_paintable(True)
        self.win.set_keep_above(True)
        self.win.fullscreen()

        screen = self.win.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.win.set_visual(visual)
        self.win.set_events(self.win.get_events())

        self.da = Gtk.DrawingArea()
        self.win.add(self.da)
        self.da.connect("draw", self._on_draw)

        self.win.connect("destroy", lambda *_: Gtk.main_quit())

        self.particles = self._init_particles()
        self._write_pid()

        self._gtk_quit = False
        signal.signal(signal.SIGTERM, lambda *_: self._signal_quit())

        GLib.timeout_add(self.cfg["frame_delay"], self._tick)
        self.win.show_all()

    def _signal_quit(self):
        self._gtk_quit = True

    def _tick(self):
        if self._gtk_quit:
            self._cleanup_pid()
            from gi.repository import Gtk
            Gtk.main_quit()
            return False
        self._update()
        self.da.queue_draw()
        return True

    def _on_draw(self, widget, cr):
        t = self.time
        c = self.cfg["colors"]
        cx, cy = self.sw // 2, self.sh // 2
        float_y = math.sin(t * 2) * self.cfg["float_amplitude"]
        gy = cy + float_y
        scale = min(self.sw, self.sh) * self.cfg["ghost_scale"]
        op = self.cfg["opacity"]

        # Clear background to transparent (SOURCE operator replaces, not blends)
        cr.set_operator(self._OP_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(self._OP_OVER)

        self._draw_vignette(cr, op)
        self._draw_grid(cr, t, cx, cy, c["grid"])
        self._draw_rings(cr, t, cx, gy, scale, c, op)
        self._draw_ghost(cr, t, cx, gy, scale, c, op)
        self._draw_particles(cr, t, c["particle"], c["primary"])
        self._draw_hud(cr, t, cx, gy, scale, c["accent"])

        return True

    def _draw_vignette(self, cr, op):
        w, h = self.sw, self.sh
        for i in range(5):
            r = 1 - i * 0.15
            alpha = i * 0.03 * op
            cr.set_source_rgba(0, 0, 0, alpha)
            cr.rectangle(w*(1-r)/2, h*(1-r)/2, w*r, h*r)
            cr.fill()

    def _draw_grid(self, cr, t, cx, cy, color):
        spacing = 60
        off = (t * 8) % spacing
        cr.set_source_rgba(*hex_to_rgba(color, 0.3))
        cr.set_line_width(1)
        for x in range(int(cx % spacing), self.sw, spacing):
            cr.move_to(x + off, 0)
            cr.line_to(x + off, self.sh)
            cr.stroke()
        for y in range(int(cy % spacing), self.sh, spacing):
            cr.move_to(0, y + off)
            cr.line_to(self.sw, y + off)
            cr.stroke()

    def _draw_rings(self, cr, t, cx, cy, scale, c, op):
        radii = [scale*1.8, scale*2.3, scale*2.8]
        colors = [c["primary"], c["secondary"], c["accent"]]
        speeds = [0.3, -0.2, 0.15]
        segs = 48
        gap = 6
        for r, col, sp in zip(radii, colors, speeds):
            angle = t * sp
            cr.set_source_rgba(*hex_to_rgba(col, op))
            cr.set_line_width(1)
            for j in range(0, segs, gap):
                a1 = angle + (j/segs) * 2 * math.pi
                a2 = angle + ((j+gap-1)/segs) * 2 * math.pi
                cr.arc(cx, cy, r, a1, a2)
                cr.stroke()
        for j in range(4):
            a = t*0.2 + j*math.pi/2
            x1 = cx + radii[0]*math.cos(a)
            y1 = cy + radii[0]*math.sin(a)
            x2 = cx + radii[2]*math.cos(a)
            y2 = cy + radii[2]*math.sin(a)
            cr.set_source_rgba(*hex_to_rgba(c["accent"], op * 0.6))
            cr.set_dash([3, 6])
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.stroke()
            cr.set_dash([])

    def _draw_ghost(self, cr, t, cx, cy, scale, c, op):
        # Body
        cr.set_source_rgba(*hex_to_rgba(c["ghost_fill"], op * 0.9))
        first = True
        for px, py in GHOST_POLYGON:
            x, y = cx + px * scale, cy + py * scale
            if first:
                cr.move_to(x, y)
                first = False
            else:
                cr.line_to(x, y)
        cr.close_path()
        cr.fill_preserve()
        cr.set_source_rgba(*hex_to_rgba(c["ghost_outline"], op))
        cr.set_line_width(2)
        cr.stroke()

        # Circuits
        for i, path in enumerate(CIRCUIT_PATHS):
            col = c["primary"] if i % 2 == 0 else c["secondary"]
            cr.set_source_rgba(*hex_to_rgba(col, op))
            cr.set_line_width(1.5)
            for j in range(len(path) - 1):
                cr.move_to(cx + path[j][0]*scale, cy + path[j][1]*scale)
                cr.line_to(cx + path[j+1][0]*scale, cy + path[j+1][1]*scale)
                cr.stroke()
            for px, py in path:
                cr.arc(cx + px*scale, cy + py*scale, 3, 0, 2*math.pi)
                cr.fill()

        # Core
        r = scale * 0.18
        angle = t * 2
        cr.set_source_rgba(*hex_to_rgba(c["secondary"], op))
        cr.set_line_width(2)
        first = True
        for i in range(8):
            a = angle + i * math.pi/4
            x, y = cx + r*math.cos(a), cy + r*math.sin(a)
            if first:
                cr.move_to(x, y)
                first = False
            else:
                cr.line_to(x, y)
        cr.close_path()
        cr.fill_preserve()
        cr.set_source_rgba(*hex_to_rgba(c["ghost_fill"], op))
        cr.fill()

        cr.set_source_rgba(*hex_to_rgba(c["primary"], op))
        cr.arc(cx, cy, r*0.4, 0, 2*math.pi)
        cr.fill()

        # Eyes
        eye_y = cy - scale * 0.28
        spread = scale * 0.18
        pulse = 1 + 0.15 * math.sin(t * 3)
        for side in [-1, 1]:
            ex = cx + side * spread
            eye_r = 6 * pulse
            cr.set_source_rgba(*hex_to_rgba(c["primary"], op))
            first = True
            for i in range(6):
                a = i * math.pi/3 + t * 0.5
                x, y = ex + eye_r*math.cos(a), eye_y + eye_r*math.sin(a)
                if first:
                    cr.move_to(x, y)
                    first = False
                else:
                    cr.line_to(x, y)
            cr.close_path()
            cr.fill()

        # Glow rings
        for i in range(3):
            gr = scale * 0.7 * (1 + i * 0.15)
            cr.set_source_rgba(*hex_to_rgba(c["glow"], op * 0.15))
            cr.arc(cx, cy, gr, 0, 2*math.pi)
            cr.set_line_width(1)
            cr.stroke()

    def _draw_particles(self, cr, t, color, glow_color):
        for p in self.particles:
            twinkle = 0.5 + 0.5 * math.sin(t * 3 + p["phase"])
            sz = p["size"] * twinkle
            cr.set_source_rgba(*hex_to_rgba(color, twinkle))
            cr.arc(p["x"], p["y"], sz, 0, 2*math.pi)
            cr.fill()
            cr.set_source_rgba(*hex_to_rgba(glow_color, twinkle * 0.3))
            cr.arc(p["x"], p["y"], sz*2, 0, 2*math.pi)
            cr.fill()

    def _draw_hud(self, cr, t, cx, cy, scale, color):
        spread = scale * 2.0
        sz = scale * 0.15
        corners = [
            (cx-spread, cy-spread, 1, 1),
            (cx+spread, cy-spread, -1, 1),
            (cx-spread, cy+spread, 1, -1),
            (cx+spread, cy+spread, -1, -1),
        ]
        cr.set_source_rgba(*hex_to_rgba(color, 0.5))
        cr.set_line_width(1)
        for x, y, dx, dy in corners:
            cr.move_to(x, y+sz*dy)
            cr.line_to(x, y)
            cr.line_to(x+sz*dx, y)
            cr.stroke()
        scan_y = (t * 60) % self.sh
        cr.move_to(0, scan_y)
        cr.line_to(self.sw, scan_y)
        cr.stroke()

    def run(self):
        from gi.repository import Gtk
        Gtk.main()


# ─── Factory ───────────────────────────────────────────────────────────

def create_ghost_screen(cfg=None):
    display_type = os.environ.get("XDG_SESSION_TYPE", "x11")
    if display_type == "wayland":
        try:
            return GtkGhostScreen(cfg)
        except Exception:
            print("Falling back to X11 mode (black background on Wayland).")
    return TkinterGhostScreen(cfg)


def main():
    parser = argparse.ArgumentParser(description=f"{PROJECT} v{VERSION}")
    parser.add_argument("--kill", "-k", action="store_true", help="Kill running instance")
    parser.add_argument("--version", "-v", action="store_true", help="Show version")
    args = parser.parse_args()

    if args.version:
        print(f"{PROJECT} v{VERSION}")
        sys.exit(0)

    if args.kill:
        kill_ghost()
        sys.exit(0)

    if is_running():
        kill_ghost()
        print("Ghost screen dismissed.")
    else:
        app = create_ghost_screen()
        app.run()


if __name__ == "__main__":
    main()
