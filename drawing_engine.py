"""
Drawing Engine — Pygame Stroke-by-Stroke Animation with Moving Pencil Cursor.

Key design decisions
────────────────────
* VIRTUAL CANVAS  (1248 × 1248) is where all strokes are drawn.
* DISPLAY WINDOW  is sized to fit the screen with a HUD strip.
* The virtual canvas is proportionally scaled + centred inside the window
  (letterbox / pillarbox) so NOTHING is ever cropped.
* A realistic pencil cursor follows the exact tip of the active stroke.
* The cursor is drawn on the SCREEN surface, NOT the canvas, so it never
  appears in the saved PNG.
"""

import math
import os
import pygame
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Geometry helpers
# ─────────────────────────────────────────────────────────────────────────────

def catmull_rom_pts(pts, num_per_seg=12):
    """Catmull-Rom spline through pts → dense (x,y) list."""
    if len(pts) < 2:
        return list(pts)
    arr = np.array(pts, dtype=np.float32)
    if len(arr) == 2:
        t = np.linspace(0, 1, num_per_seg)
        res = (1 - t[:, None]) * arr[0] + t[:, None] * arr[1]
        return [tuple(p) for p in res]
    padded = np.vstack([arr[0] - (arr[1] - arr[0]),
                        arr,
                        arr[-1] + (arr[-1] - arr[-2])])
    t  = np.linspace(0, 1, num_per_seg, endpoint=False)[:, None]
    t2 = t * t
    t3 = t2 * t
    result = []
    for i in range(1, len(padded) - 2):
        p0, p1, p2, p3 = padded[i-1], padded[i], padded[i+1], padded[i+2]
        seg = 0.5 * ((2*p1) + (-p0+p2)*t +
                     (2*p0 - 5*p1 + 4*p2 - p3)*t2 +
                     (-p0 + 3*p1 - 3*p2 + p3)*t3)
        result.extend([tuple(p) for p in seg])
    result.append(tuple(padded[-2]))
    return result


def cubic_bezier_pts(p0, p1, p2, p3, steps=40):
    t  = np.linspace(0, 1, steps)[:, None]
    p0a, p1a, p2a, p3a = (np.array(x) for x in (p0, p1, p2, p3))
    pts = ((1-t)**3 * p0a + 3*(1-t)**2*t * p1a +
           3*(1-t)*t**2 * p2a + t**3 * p3a)
    return [tuple(p) for p in pts]


def sample_arc(cx, cy, rx, ry, angle_deg=0,
               start_deg=0, end_deg=360, steps=32):
    rad    = math.radians(angle_deg)
    cos_r, sin_r = math.cos(rad), math.sin(rad)
    angles = np.linspace(math.radians(start_deg), math.radians(end_deg), steps)
    xs = cx + rx * np.cos(angles) * cos_r - ry * np.sin(angles) * sin_r
    ys = cy + rx * np.cos(angles) * sin_r + ry * np.sin(angles) * cos_r
    return list(zip(xs.tolist(), ys.tolist()))


# ─────────────────────────────────────────────────────────────────────────────
# Stroke factory
# ─────────────────────────────────────────────────────────────────────────────

def make_stroke(points, color=(30, 28, 24), width=2, opacity=255,
                speed=4, stage=1, label=""):
    return {
        "points":  points,
        "color":   color,
        "width":   width,
        "opacity": opacity,
        "speed":   speed,
        "stage":   stage,
        "label":   label,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Pencil cursor renderer
# ─────────────────────────────────────────────────────────────────────────────

def _draw_pencil(surf, tip_x, tip_y, angle_deg):
    """
    Draw a small, sleek graphite pencil cursor on `surf`.
    Pencil body extends naturally towards the upper right without spinning 360 degrees.
    """
    L  = 26          # compact pencil body length
    BW = 5           # sleek body width
    TL = 8           # sharpened wood taper
    GL = 3           # graphite tip point

    rad = math.radians(angle_deg)
    dx  = math.cos(rad)
    dy  = math.sin(rad)
    px  = -dy
    py  =  dx

    def pt(along, across):
        return (int(tip_x + dx * along + px * across),
                int(tip_y + dy * along + py * across))

    # Graphite tip
    tip_poly = [pt(0, 0), pt(GL, BW * 0.28), pt(GL, -BW * 0.28)]
    pygame.draw.polygon(surf, (26, 24, 20), tip_poly)

    # Sharpened wood cone
    taper_poly = [pt(GL, BW * 0.28), pt(GL, -BW * 0.28), pt(GL + TL, -BW * 0.5), pt(GL + TL, BW * 0.5)]
    pygame.draw.polygon(surf, (195, 155, 95), taper_poly)

    # Yellow hexagonal body
    body_end = GL + TL + L
    body_poly = [pt(GL + TL, BW * 0.5), pt(GL + TL, -BW * 0.5), pt(body_end, -BW * 0.5), pt(body_end, BW * 0.5)]
    pygame.draw.polygon(surf, (235, 198, 55), body_poly)
    pygame.draw.polygon(surf, (55, 45, 30), body_poly, 1)

    # Subtle highlight stripe
    hi_start = pt(GL + TL + 1, -BW * 0.18)
    hi_end   = pt(body_end - 1, -BW * 0.18)
    pygame.draw.line(surf, (248, 228, 130), hi_start, hi_end, 1)

    # Silver ferrule band
    band_poly = [pt(body_end, BW * 0.5), pt(body_end, -BW * 0.5), pt(body_end + 3, -BW * 0.5), pt(body_end + 3, BW * 0.5)]
    pygame.draw.polygon(surf, (170, 160, 150), band_poly)

    # Pink eraser
    eraser_poly = [pt(body_end + 3, BW * 0.45), pt(body_end + 3, -BW * 0.45), pt(body_end + 8, -BW * 0.45), pt(body_end + 8, BW * 0.45)]
    pygame.draw.polygon(surf, (225, 162, 156), eraser_poly)

    # Graphite contact dot
    pygame.draw.circle(surf, (18, 16, 12), (int(tip_x), int(tip_y)), 1)


# ─────────────────────────────────────────────────────────────────────────────
# Drawing Engine
# ─────────────────────────────────────────────────────────────────────────────

class DrawingEngine:
    """
    Manages the ordered stroke queue and animates them in a Pygame window.

    Virtual canvas  →  fits into the display window with letterboxing.
    Pencil cursor   →  rendered on the screen surface (NOT the canvas).
    """

    PENCIL_DARK  = (25, 22, 18)
    PENCIL_MID   = (60, 55, 50)
    PENCIL_LIGHT = (130, 125, 118)
    PENCIL_FAINT = (185, 180, 172)
    PAPER_BG     = (255, 255, 255)
    RENDER_SCALE = 3

    # Overwritten by stroke_scene.py after build_scene() is called
    STAGE_NAMES = {
        1:  "Construction guidelines",
        2:  "Male face",
        3:  "Male hair",
        4:  "Male clothing",
        5:  "Male arms & sticks",
        6:  "Female face",
        7:  "Female hair",
        8:  "Female clothing",
        9:  "Female arms & sticks",
        10: "Ground & motion",
        11: "Shading",
        12: "Final touches",
    }

    # ──────────────────────────────────────────────────────────────────────
    def __init__(self, canvas_w=1248, canvas_h=1248, fps=60):
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h
        self.fps      = fps
        self.rng      = np.random.default_rng(42)

        # Stroke queue
        self._strokes      = []
        self._stroke_index = 0
        self._dense_pts    = []
        self._draw_cursor  = 0

        # Playback
        self._paused    = False
        self._speed_mul = 2.0
        self._done      = False

        # Persistent drawing canvas (pure artwork, NO HUD, NO pencil)
        self._canvas = None

        # Pencil state
        self._pencil_tip   = (canvas_w // 2, canvas_h // 2)
        self._pencil_angle = 315.0    # degrees; natural artist grip pointing up-right

        # Window layout (computed in run())
        self._win_w    = 0
        self._win_h    = 0
        self._scale    = 1.0
        self._off_x    = 0
        self._off_y    = 0
        self._hud_h    = 44

    # ── Stroke helpers ────────────────────────────────────────────────────

    def add_stroke(self, points, color=None, width=2, opacity=255,
                   speed=3, stage=1, label=""):
        if color is None:
            color = self.PENCIL_DARK
        if len(points) < 2:
            return
        self._strokes.append(make_stroke(
            points=list(points), color=color, width=max(1, width),
            opacity=min(255, max(0, opacity)), speed=max(1, speed),
            stage=stage, label=label
        ))

    def add_bezier(self, p0, p1, p2, p3, **kw):
        self.add_stroke(cubic_bezier_pts(p0, p1, p2, p3, steps=50), **kw)

    def add_arc(self, cx, cy, rx, ry, angle_deg=0,
                start_deg=0, end_deg=360, **kw):
        self.add_stroke(
            sample_arc(cx, cy, rx, ry, angle_deg, start_deg, end_deg, 48),
            **kw
        )

    # ── Window layout ─────────────────────────────────────────────────────

    def _compute_layout(self, win_w, win_h):
        """
        Compute scale + offsets so the virtual canvas fits inside the window
        (minus HUD strip) with equal margins on the free axis.
        """
        avail_w = win_w
        avail_h = win_h - self._hud_h
        scale   = min(avail_w / self.canvas_w, avail_h / self.canvas_h)
        disp_w  = self.canvas_w * scale
        disp_h  = self.canvas_h * scale
        off_x   = (avail_w - disp_w) / 2
        off_y   = (avail_h - disp_h) / 2
        return scale, int(off_x), int(off_y)

    def _canvas_to_screen(self, cx, cy):
        """Map a virtual canvas coordinate to a screen pixel."""
        return (int(cx * self._scale + self._off_x),
                int(cy * self._scale + self._off_y))

    # ── Main loop ─────────────────────────────────────────────────────────

    def run(self, title="Indian Couple Dandiya — Pencil Sketch"):
        pygame.init()
        pygame.display.set_caption(title)

        # Determine a comfortable window size  ───────────────────────────
        info = pygame.display.Info()
        scr_w, scr_h = info.current_w, info.current_h

        # Leave room for taskbar / OS chrome: ~92 % of screen
        max_w = int(scr_w * 0.92)
        max_h = int(scr_h * 0.92)

        # Square window fitting both canvas and HUD
        side = min(max_w, max_h - self._hud_h)
        win_w = side
        win_h = side + self._hud_h

        screen = pygame.display.set_mode(
            (win_w, win_h), pygame.RESIZABLE
        )

        self._win_w = win_w
        self._win_h = win_h
        self._scale, self._off_x, self._off_y = self._compute_layout(win_w, win_h)

        # Virtual canvas (artwork only)
        self._canvas = pygame.Surface((self.canvas_w * self.RENDER_SCALE, self.canvas_h * self.RENDER_SCALE))
        self._canvas.fill(self.PAPER_BG)

        # Scaled canvas surface (reused each frame)
        disp_w = int(self.canvas_w * self._scale)
        disp_h = int(self.canvas_h * self._scale)
        scaled_canvas = pygame.Surface((disp_w, disp_h))

        clock = pygame.time.Clock()

        # HUD font
        pygame.font.init()
        try:
            ui_font  = pygame.font.SysFont("Segoe UI", 14)
            ui_font2 = pygame.font.SysFont("Segoe UI", 13)
        except Exception:
            ui_font  = pygame.font.Font(None, 16)
            ui_font2 = ui_font

        self._prepare_next_stroke()

        running = True
        while running:
            dt = clock.tick(self.fps)

            # ── Events ───────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    win_w, win_h = event.w, event.h
                    self._win_w, self._win_h = win_w, win_h
                    self._scale, self._off_x, self._off_y = \
                        self._compute_layout(win_w, win_h)
                    disp_w = int(self.canvas_w * self._scale)
                    disp_h = int(self.canvas_h * self._scale)
                    scaled_canvas = pygame.Surface((disp_w, disp_h))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self._paused = not self._paused
                    elif event.key == pygame.K_UP:
                        self._speed_mul = min(32.0, self._speed_mul * 1.5)
                    elif event.key == pygame.K_DOWN:
                        self._speed_mul = max(0.25, self._speed_mul / 1.5)
                    elif event.key == pygame.K_r:
                        self._restart()
                    elif event.key == pygame.K_s:
                        self._save_canvas()

            # ── Animation step ────────────────────────────────────────────
            if not self._paused and not self._done:
                self._advance(dt)

            # ── Render ───────────────────────────────────────────────────
            win_w, win_h = screen.get_size()
            screen.fill((200, 198, 192))   # neutral grey surround

            # Scale virtual canvas → screen
            disp_w = int(self.canvas_w * self._scale)
            disp_h = int(self.canvas_h * self._scale)
            if scaled_canvas.get_size() != (disp_w, disp_h):
                scaled_canvas = pygame.Surface((disp_w, disp_h))
            pygame.transform.smoothscale(self._canvas, (disp_w, disp_h), scaled_canvas)
            screen.blit(scaled_canvas, (self._off_x, self._off_y))

            # Draw pencil cursor on screen (NOT on canvas)
            if not self._done and not self._paused:
                tip_sx, tip_sy = self._canvas_to_screen(*self._pencil_tip)
                _draw_pencil(screen, tip_sx, tip_sy, self._pencil_angle)

            # HUD strip at bottom
            self._draw_hud(screen, ui_font, ui_font2, win_w, win_h)

            pygame.display.flip()

        # Auto-save on clean exit
        if self._done:
            self._save_canvas()
        pygame.quit()

    # ── Animation internals ───────────────────────────────────────────────

    def _restart(self):
        self._stroke_index = 0
        self._draw_cursor  = 0
        self._dense_pts    = []
        self._done         = False
        self._paused       = False
        if self._canvas:
            self._canvas.fill(self.PAPER_BG)
        self._prepare_next_stroke()

    def _prepare_next_stroke(self):
        """Load next stroke and build its dense jittered point list."""
        if self._stroke_index >= len(self._strokes):
            self._done = True
            self._save_canvas()
            return
        s       = self._strokes[self._stroke_index]
        raw_pts = s["points"]
        # Smooth
        if len(raw_pts) >= 3:
            dense = catmull_rom_pts(raw_pts, num_per_seg=10)
        else:
            dense = list(raw_pts)
        # Uniform spacing makes the visible pencil advance along the curve
        # at a stable speed, independent of control-point density.
        arr = np.asarray(dense, dtype=float)
        distances = np.concatenate(([0.0], np.cumsum(np.linalg.norm(np.diff(arr,axis=0),axis=1))))
        keep = np.concatenate(([True], np.diff(distances)>1e-7))
        arr,distances = arr[keep],distances[keep]
        if len(arr)>1:
            samples = np.linspace(0,distances[-1],max(2,int(distances[-1]/.7)+1))
            dense = list(zip(np.interp(samples,distances,arr[:,0]),np.interp(samples,distances,arr[:,1])))
        else:
            dense = [tuple(arr[0]),tuple(arr[0])]
        # Clean ink paths have no random hand tremor.
        self._dense_pts = dense
        self._draw_cursor = 0
        # Initialise pencil at start of stroke
        if self._dense_pts:
            self._pencil_tip = self._dense_pts[0]

    def _advance(self, dt_ms):
        """Advance animation by one frame's worth of stroke segments."""
        if self._done or not self._dense_pts:
            return

        s          = self._strokes[self._stroke_index]
        step       = max(1, int(s["speed"] * self._speed_mul))
        end_cursor = min(self._draw_cursor + step, len(self._dense_pts) - 1)
        total      = len(self._dense_pts)

        if end_cursor > self._draw_cursor:
            segment = self._dense_pts[self._draw_cursor: end_cursor + 1]
            if len(segment) >= 2:
                col = s["color"]
                bg  = self.PAPER_BG
                for i in range(len(segment) - 1):
                    if s["label"] == "connected_contour":
                        w = s["width"]
                        blended = col
                    elif s.get("label") in ("solid_hair_fill", "hair_deep_black"):
                        w = 5
                        blended = col
                    elif s.get("label") == "solid_flower_fill":
                        w = 4
                        blended = col
                    elif s.get("label") in ("female_pupil_fill", "male_pupil_fill"):
                        w = s["width"]
                        blended = col
                    elif str(s.get("label", "")).startswith(("female_eye_", "male_eye_")):
                        w = s.get("width", 3)
                        blended = col
                    else:
                        gi      = self._draw_cursor + i
                        t_norm  = gi / max(1, total - 1)
                        pressure = math.sin(math.pi * t_norm) ** 0.40
                        w = max(1, int(round(s["width"] * (0.65 + 0.35 * pressure))))

                        alpha = s["opacity"] / 255.0 * (0.75 + 0.25 * pressure)
                        blended = (
                            max(0, min(255, int(col[0]*alpha + bg[0]*(1-alpha)))),
                            max(0, min(255, int(col[1]*alpha + bg[1]*(1-alpha)))),
                            max(0, min(255, int(col[2]*alpha + bg[2]*(1-alpha)))),
                        )
                    p0 = (round(segment[i][0] * self.RENDER_SCALE), round(segment[i][1] * self.RENDER_SCALE))
                    p1 = (round(segment[i+1][0] * self.RENDER_SCALE), round(segment[i+1][1] * self.RENDER_SCALE))
                    if s["label"] == "connected_contour":
                        # The same moving line primitive draws faces, eyes,
                        # flowing hair contours, and inward hair-fill curves.
                        width = max(1,round(w*self.RENDER_SCALE))
                        pygame.draw.line(self._canvas, col, p0, p1, width)
                        pygame.draw.circle(self._canvas,col,p1,max(1,width//2))
                    else:
                        # Partition the canvas around the head bounds: no old
                        # face, hair, garment or color strokes can enter them.
                        for clip in self._body_clips():
                            self._canvas.set_clip(clip)
                            pygame.draw.line(self._canvas, blended, p0, p1, max(1, round(w * self.RENDER_SCALE)))
                        self._canvas.set_clip(None)

            self._draw_cursor = end_cursor

            # Update pencil tip to the current head of the stroke
            self._pencil_tip = self._dense_pts[self._draw_cursor]

            # Update pencil angle: steady natural artist hand tilt (no 360-degree spinning)
            if self._draw_cursor >= 1:
                ax, ay = self._dense_pts[self._draw_cursor - 1]
                bx, by = self._dense_pts[self._draw_cursor]
                ddx, ddy = bx - ax, by - ay
                if abs(ddx) > 0.001 or abs(ddy) > 0.001:
                    # Subtle wrist tilt (+-12 deg) based on stroke direction; never rotates 360 degrees
                    subtle_tilt = math.sin(math.atan2(ddy, ddx)) * 12.0
                    target_angle = 315.0 + subtle_tilt
                    self._pencil_angle += (target_angle - self._pencil_angle) * 0.20

        # Finish stroke
        if self._draw_cursor >= len(self._dense_pts) - 1:
            self._stroke_index += 1
            self._prepare_next_stroke()

    def _body_clips(self):
        if hasattr(self, "_ink_clips"):
            return self._ink_clips
        clips = [self._canvas.get_rect()]
        k = self.RENDER_SCALE
        for (x0,y0),(x1,y1) in getattr(self, "excluded_regions", []):
            cut = pygame.Rect(round(x0*k), round(y0*k), round(x1*k)-round(x0*k), round(y1*k)-round(y0*k))
            next_clips = []
            for region in clips:
                hit = region.clip(cut)
                if not hit.width or not hit.height:
                    next_clips.append(region)
                    continue
                pieces = [pygame.Rect(region.left,region.top,region.width,hit.top-region.top),
                          pygame.Rect(region.left,hit.bottom,region.width,region.bottom-hit.bottom),
                          pygame.Rect(region.left,hit.top,hit.left-region.left,hit.height),
                          pygame.Rect(hit.right,hit.top,region.right-hit.right,hit.height)]
                next_clips.extend(r for r in pieces if r.width>0 and r.height>0)
            clips = next_clips
        self._ink_clips = clips
        return clips

    # ── HUD ───────────────────────────────────────────────────────────────

    def _draw_hud(self, screen, font, font2, win_w, win_h):
        hud_y = win_h - self._hud_h
        hud_r = pygame.Rect(0, hud_y, win_w, self._hud_h)
        pygame.draw.rect(screen, (238, 235, 228), hud_r)
        pygame.draw.line(screen, (180, 175, 168), (0, hud_y), (win_w, hud_y), 1)

        total  = len(self._strokes)
        done   = self._stroke_index
        pct    = done / max(1, total)

        # Progress bar
        bar_x = 10
        bar_y = hud_y + 28
        bar_w = win_w - 20
        bar_h = 8
        pygame.draw.rect(screen, (195, 190, 182), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            pygame.draw.rect(screen, (52, 48, 40), (bar_x, bar_y, fill_w, bar_h), border_radius=4)

        # Stage / status text
        if self._done:
            label = "✓  Drawing complete — press R to replay, Esc to exit"
        elif self._paused:
            label = "⏸  PAUSED   Space=Resume  ↑↓=Speed  R=Restart  Esc=Quit"
        else:
            stage = self._strokes[done]["stage"] if done < total else 12
            sname = self.STAGE_NAMES.get(stage, "Drawing…")
            spd   = f"{self._speed_mul:.2g}×"
            label = (f"Stage {stage}  ·  {sname}   |   "
                     f"{int(pct*100)}%  ({done}/{total})   |   "
                     f"Speed {spd}   |   Space=Pause  ↑↓=Speed  R=Restart  Esc=Quit")

        txt = font.render(label, True, (38, 34, 26))
        screen.blit(txt, (12, hud_y + 8))

    # ── Save ──────────────────────────────────────────────────────────────

    def _save_canvas(self):
        """Save the artwork surface (no pencil cursor, no HUD) to PNG."""
        path = getattr(self, "output_path", "output/dandiya_pencil_sketch.png")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        pygame.image.save(pygame.transform.smoothscale(self._canvas, (self.canvas_w, self.canvas_h)), path)
        print(f"[+] Saved -> {os.path.abspath(path)}")
