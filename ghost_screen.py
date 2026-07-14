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
    def __init__(self, cfg=None):
        super().__init__(cfg)
        self._backend = "wayland"
        self._setup_gtk()

    def _setup_gtk(self):
        import gi
        gi.require_version("Gdk", "3.0")
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gdk, Gtk, GLib, GdkPixbuf

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

        self.image = Gtk.Image()
        self.win.add(self.image)
        self.win.show_all()

        self.win.connect("destroy", lambda *_: Gtk.main_quit())

        self.particles = self._init_particles()
        self._write_pid()

        self._gtk_quit = False
        self._GdkPixbuf = GdkPixbuf
        self._GLib = GLib
        signal.signal(signal.SIGTERM, lambda *_: self._signal_quit())

        GLib.timeout_add(self.cfg["frame_delay"], self._tick)

    def _signal_quit(self):
        self._gtk_quit = True

    def _tick(self):
        if self._gtk_quit:
            self._cleanup_pid()
            self._gtk_quit = False
            import gi
            gi.require_version("Gtk", "3.0")
            from gi.repository import Gtk
            Gtk.main_quit()
            return False

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
        self.image.set_from_pixbuf(pb)

        return True

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

    def run(self):
        from gi.repository import Gtk
        Gtk.main()


# ─── Factory ───────────────────────────────────────────────────────────

def create_ghost_screen(cfg=None):
    display_type = os.environ.get("XDG_SESSION_TYPE", "x11")
    if display_type == "wayland":
        try:
            from PIL import Image, ImageDraw
            return GtkGhostScreen(cfg)
        except ImportError:
            print("Pillow not installed; install python3-pil for Wayland transparency.")
        except Exception as e:
            print(f"Wayland backend failed ({e}), falling back to X11.")
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
