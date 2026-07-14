#!/usr/bin/env python3

import math
import random
import os
import sys
import signal
import argparse
import json

# tkinter is imported lazily — --version and --kill work without it

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


class GhostScreen:
    def __init__(self, cfg=None):
        import tkinter as tk
        self.tk = tk

        self.cfg = DEFAULT_CONFIG.copy()
        if cfg:
            for k, v in cfg.items():
                if k == "colors" and isinstance(v, dict):
                    self.cfg["colors"].update(v)
                else:
                    self.cfg[k] = v

        self.root = tk.Tk()
        self._setup_window()
        self._setup_canvas()
        self._init_particles()
        self._bind_events()
        self._write_pid()

    def _setup_window(self):
        self.root.title(PROJECT)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.cfg["opacity"])
        self.root.overrideredirect(True)
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

    def _setup_canvas(self):
        self.canvas = tk.Canvas(
            self.root,
            width=self.sw, height=self.sh,
            highlightthickness=0,
            bg=self.cfg["colors"]["bg"],
        )
        self.canvas.pack()

    def _init_particles(self):
        self.time = 0.0
        self.particles = []
        for _ in range(self.cfg["particle_count"]):
            self.particles.append({
                "x": random.uniform(0, self.sw),
                "y": random.uniform(0, self.sh),
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(-0.5, -0.15),
                "size": random.uniform(1.5, 3.5),
                "phase": random.uniform(0, 2 * math.pi),
            })

    def _bind_events(self):
        self.root.bind("<Button-1>", lambda e: self._close())
        self.root.bind("<Escape>", lambda e: self._close())
        self.root.bind("<Control-3>", lambda e: self._close())
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        signal.signal(signal.SIGTERM, lambda *_: os._exit(0))

    def _write_pid(self):
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))

    def _close(self):
        try:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
        except OSError:
            pass
        self.root.quit()
        self.root.destroy()

    def draw(self):
        self.canvas.delete("all")
        self.time += self.cfg["frame_delay"] / 1000.0
        t = self.time

        cx, cy = self.sw // 2, self.sh // 2
        float_y = math.sin(t * 2) * self.cfg["float_amplitude"]
        gy = cy + float_y
        scale = min(self.sw, self.sh) * self.cfg["ghost_scale"]

        c = self.cfg["colors"]

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
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < -20:
                p["y"] = self.sh + 20
                p["x"] = random.uniform(0, self.sw)
            if p["x"] < -20 or p["x"] > self.sw + 20:
                p["x"] = random.uniform(0, self.sw)
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
        self.canvas.create_line(0, scan_y+2, self.sw, scan_y+2, fill=color, width=1, dash=(2, 10))

    def run(self):
        self.root.after(100, self.draw)
        self.root.mainloop()


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
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            print(
                "WARNING: You are on Wayland. Transparent overlays won't work.\n"
                "         Log out, select 'Ubuntu on Xorg' at login, then try again.\n"
            )
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    cfg = json.load(f)
            except Exception:
                pass
        app = GhostScreen(cfg)
        app.run()


if __name__ == "__main__":
    main()
