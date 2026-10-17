"""
Stroke Scene Composer â€” Pure Line Art, Solid Black Hair & Selective Color.

Key style rules:
  - Strictly high-contrast black and white ink outlines.
  - Absolutely NO shading on the clothes.
  - Solid, dark black filled-in hair for both man and woman.
  - Selective coloring strictly limited to:
      1. Bright red bindi on woman's forehead
      2. Vibrant red flower in her hair
      3. Red and yellow striped Dandiya sticks
  - CRITICAL: Hands holding the sticks remain purely uncolored white skin with black outlines.
"""

import math
import numpy as np
from drawing.vector_data import CATEGORIES, get_tone_density_map
from drawing_engine import DrawingEngine
from drawing.eyes import clean_face_paths, eye_paths

CANVAS_W = 1248
CANVAS_H = 1248
MARGIN = 0.06

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 1. Combined Scene Bounding Box & Unified Coordinate Transform
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _compute_bounds():
    all_x, all_y = [], []
    for paths in CATEGORIES.values():
        for p in paths:
            for pt in p["points"]:
                all_x.append(pt[0])
                all_y.append(pt[1])
    return min(all_x), min(all_y), max(all_x), max(all_y)

SRC_X0, SRC_Y0, SRC_X1, SRC_Y1 = _compute_bounds()
SRC_W = SRC_X1 - SRC_X0
SRC_H = SRC_Y1 - SRC_Y0

AVAIL_W = CANVAS_W * (1.0 - 2.0 * MARGIN)
AVAIL_H = CANVAS_H * (1.0 - 2.0 * MARGIN)

SCALE = min(AVAIL_W / SRC_W, AVAIL_H / SRC_H)
TX = (CANVAS_W - SRC_W * SCALE) / 2.0 - SRC_X0 * SCALE
TY = (CANVAS_H - SRC_H * SCALE) / 2.0 - SRC_Y0 * SCALE

def transform_pts(points):
    """Apply unified (scale, translation) transformation to list of (x,y)."""
    return [(x * SCALE + TX, y * SCALE + TY) for x, y in points]

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 2. Ink & Selective Color Palette
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
INK_PURE_BLACK  = (10, 8, 8)      # Crisp high-contrast pure black ink
INK_HAIR_BLACK  = (8, 6, 6)       # Solid dark black for filled-in hair
GESTURE_FAINT   = (195, 190, 185) # Very faint 2H initial gesture

# Selective color tokens
COLOR_RED_BINDI = (228, 20, 30)   # Bright red bindi
COLOR_RED_FLOWER= (138, 14, 18)   # Solid dark red flower in hair (no white gaps)
COLOR_STICK_YEL = (248, 202, 20)  # Bright golden yellow for dandiya sticks
COLOR_STICK_RED = (222, 26, 36)   # Festive red spiral stripes for dandiya sticks

STAGE_NAMES = {
    1:  "Light gesture & dynamic curves",
    2:  "Main character silhouettes",
    3:  "Facial features & anime expressions",
    4:  "Solid dark black hair",
    5:  "Arms, hands & dandiya sticks line art",
    6:  "Traditional clothing line art (no shading)",
    7:  "Selective color: Dandiya sticks (yellow & red)",
    8:  "Selective color: Bright red bindi & flower",
    9:  "Ink reinforcement & dark hair accents",
    10: "Motion celebration dashes & ground lines",
}

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 3. Main Scene Builder
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def build_scene(engine: DrawingEngine):
    engine.STAGE_NAMES = STAGE_NAMES
    rng = np.random.default_rng(42)

    # Stage 1: Faint gesture curves (subtle anatomical dynamic flow)
    # Clean line art: construction gestures are omitted.

    # Categories from vector_data
    m_face_paths   = clean_face_paths("male")
    m_hair_paths   = CATEGORIES.get("male_hair", [])
    m_kurta_paths  = CATEGORIES.get("male_kurta", [])
    m_pajama_paths = CATEGORIES.get("male_pajama_shoes", [])
    m_arm_paths    = CATEGORIES.get("male_arms_sticks", [])

    f_face_paths   = clean_face_paths("female")
    f_hair_paths   = CATEGORIES.get("female_hair", [])
    f_choli_paths  = CATEGORIES.get("female_choli_dupatta", [])
    f_lehenga_paths= CATEGORIES.get("female_lehenga", [])
    f_arm_paths    = CATEGORIES.get("female_arms_sticks", [])
    scene_paths    = CATEGORIES.get("scene_details", [])

    hair_fill_paths= CATEGORIES.get("solid_hair_fill", [])
    c_bindi        = CATEGORIES.get("selective_color_bindi", [])
    c_flower       = CATEGORIES.get("selective_color_flower", [])
    c_stick_yel    = CATEGORIES.get("selective_color_sticks_yellow", [])
    c_stick_red    = CATEGORIES.get("selective_color_sticks_red", [])

    # Stage 2: Main character silhouettes (bold outer contours)
    all_body_paths = m_kurta_paths + m_pajama_paths + f_choli_paths + f_lehenga_paths
    silhouettes = [p for p in all_body_paths if p.get("length", 0) >= 35]
    for p in silhouettes:
        _enqueue_ink_path(engine, p, stage=2, width=2, label="silhouette")

    # Stage 3: Heads & facial features (male face, female face, realistic clear eyes with pupils for BOTH characters)
    for p in sorted(m_face_paths, key=lambda p: p["points"][0][1]):
        _enqueue_ink_path(engine, p, stage=3, width=2, label="male_face")
    for p in sorted(f_face_paths, key=lambda p: p["points"][0][1]):
        _enqueue_ink_path(engine, p, stage=3, width=2, label="female_face")

    # One clean source for lids, irises and explicit catchlights. Never jitter
    # these small features or enlarge scanlines across the highlight holes.
    for character in ("male", "female"):
        for path in eye_paths(character):
            engine.add_stroke(transform_pts(path["points"]),
                              color=engine.PAPER_BG if path.get("highlight") else INK_PURE_BLACK,
                              width=path["width"], opacity=255, speed=16, stage=3,
                              label=f"{character}_eye_{path['label']}")

    # Stage 4: Solid dark black filled-in hair
    # First draw outer hair contours (both characters / figures)
    for p in sorted(m_hair_paths, key=lambda p: p["points"][0][1]):
        _enqueue_ink_path(engine, p, stage=4, width=2, speed=35, label="male_hair_outline")
    for p in sorted(f_hair_paths, key=lambda p: p["points"][0][1]):
        _enqueue_ink_path(engine, p, stage=4, width=2, speed=35, label="female_hair_outline")
    # Then fill hair solid dark black
    for p in hair_fill_paths:
        pts = transform_pts(p["points"])
        if len(pts) >= 2:
            engine.add_stroke(pts, color=INK_HAIR_BLACK, width=2, opacity=255, speed=60,
                              stage=4, label="solid_hair_fill")

    # Stage 5: Arms, hands & dandiya sticks line art (pure uncolored white skin, black outlines)
    for p in sorted(m_arm_paths, key=lambda p: p["points"][0][1]):
        _enqueue_ink_path(engine, p, stage=5, width=2, label="male_arms_sticks")
    for p in sorted(f_arm_paths, key=lambda p: p["points"][0][1]):
        _enqueue_ink_path(engine, p, stage=5, width=2, label="female_arms_sticks")

    # Stage 6: Clothing line art (strictly NO shading on clothes)
    for p in sorted(m_kurta_paths, key=lambda p: p["points"][0][1]):
        if p not in silhouettes:
            _enqueue_ink_path(engine, p, stage=6, width=2, label="male_kurta")
    for p in sorted(m_pajama_paths, key=lambda p: p["points"][0][1]):
        if p not in silhouettes:
            _enqueue_ink_path(engine, p, stage=6, width=2, label="male_pajama_shoes")
    for p in sorted(f_choli_paths, key=lambda p: p["points"][0][1]):
        if p not in silhouettes:
            _enqueue_ink_path(engine, p, stage=6, width=2, label="female_choli_dupatta")
    for p in sorted(f_lehenga_paths, key=lambda p: p["points"][0][1]):
        if p not in silhouettes:
            _enqueue_ink_path(engine, p, stage=6, width=2, label="female_lehenga")

    # Stage 7: Selective color — Dandiya sticks (bright yellow base + vibrant red spiral stripes)
    # Strictly outside hand zones (zero bleed on hands)
    for p in c_stick_yel:
        pts = transform_pts(p["points"])
        if len(pts) >= 2:
            engine.add_stroke(pts, color=COLOR_STICK_YEL, width=p.get("width", 3),
                              opacity=255, speed=18, stage=7, label="stick_yellow")
    for p in c_stick_red:
        pts = transform_pts(p["points"])
        if len(pts) >= 2:
            engine.add_stroke(pts, color=COLOR_STICK_RED, width=p.get("width", 3),
                              opacity=255, speed=18, stage=7, label="stick_red")

    # Stage 8: Selective color — Bright red bindi on woman's forehead & solid dark red hair flower (no white gaps)
    for p in c_flower:
        pts = transform_pts(p["points"])
        if len(pts) >= 2:
            engine.add_stroke(pts, color=COLOR_RED_FLOWER, width=p.get("width", 3),
                              opacity=255, speed=16, stage=8, label="solid_flower_fill")
    for p in c_bindi:
        pts = transform_pts(p["points"])
        if len(pts) >= 2:
            engine.add_stroke(pts, color=COLOR_RED_BINDI, width=4,
                              opacity=255, speed=10, stage=8, label="bindi_red")

    # Stage 9: Deep hair accents & contour reinforcement (strictly NO cloth shading)
    # Hair is filled once, with no reinforcement redraw.

    # Stage 10: Motion celebration dashes & ground lines
    for p in scene_paths:
        _enqueue_ink_path(engine, p, stage=10, width=1, label="scene_details")

    # Connected contours are the only strokes in the head regions.
    # No white backing, image blit, or replacement pass is ever queued.
    import json
    from pathlib import Path
    heads = json.loads(Path(__file__).with_name("drawing").joinpath("reference_contours.json").read_text())
    engine.excluded_regions = [transform_pts([(h["box"][0],h["box"][1]),
                                              (h["box"][2],h["box"][3])]) for h in heads]
    from drawing_engine import catmull_rom_pts
    # Remove invisible old strokes as well, so the pencil never travels over
    # a masked-out face pretending to draw it.
    visible = []
    def outside(point):
        x,y = point
        return not any(a<=x<=c and b<=y<=d for (a,b),(c,d) in engine.excluded_regions)
    for stroke in engine._strokes:
        points = catmull_rom_pts(stroke["points"], 8)
        if all(outside(point) for point in points):
            visible.append(stroke)
            continue
        run = []
        for point in points:
            if outside(point):
                run.append(point)
            else:
                if len(run)>1:
                    visible.append(dict(stroke, points=run))
                run=[]
        if len(run)>1:
            visible.append(dict(stroke,points=run))
    engine._strokes = visible
    for head in heads:
        for path in sorted(head["strokes"], key=lambda path: {"face_curve":0,"contour":1,"hair_curve":2}[path["kind"]]):
            is_hair = (path["kind"] == "hair_curve")
            stroke_speed = 60 if is_hair else 16
            engine.add_stroke(transform_pts(path["points"]),
                              color=tuple(path["color"]), width=path["width"]*SCALE,
                              speed=stroke_speed, stage=path["stage"], label="connected_contour")
    engine._strokes.sort(key=lambda stroke: stroke["stage"])


def _enqueue_ink_path(engine: DrawingEngine, path, stage=5, width=2, speed=16, label=""):
    pts = transform_pts(path["points"])
    if len(pts) < 2:
        return
    length = path.get("length", 10)
    w = 2 if length > 20 else width
    engine.add_stroke(pts, color=INK_PURE_BLACK, width=w, opacity=255, speed=speed, stage=stage, label=label)


def _add_faint_gestures(engine: DrawingEngine):
    """Extremely faint initial gesture lines for dancing poses."""
    g1 = [(310, 120), (290, 240), (250, 420), (200, 580), (180, 720)]
    engine.add_stroke(transform_pts(g1), color=GESTURE_FAINT, width=1, opacity=18, speed=16, stage=1, label="gesture_m")

    g2 = [(250, 420), (330, 520), (335, 600), (270, 700), (250, 740)]
    engine.add_stroke(transform_pts(g2), color=GESTURE_FAINT, width=1, opacity=18, speed=16, stage=1, label="gesture_m_leg")

    g3 = [(675, 230), (660, 340), (665, 420), (720, 580), (780, 720)]
    engine.add_stroke(transform_pts(g3), color=GESTURE_FAINT, width=1, opacity=18, speed=16, stage=1, label="gesture_f")


def _add_hair_reinforcement(engine: DrawingEngine, rng):
    """Deep solid black hair reinforcement strokes (NO shading on clothes)."""
    # Second dense pass over hair to ensure deep solid black coverage
    for p in CATEGORIES.get("solid_hair_fill", []):
        if rng.random() > 0.5:
            pts = transform_pts(p["points"])
            if len(pts) >= 2:
                engine.add_stroke(pts, color=INK_HAIR_BLACK, width=2, opacity=255,
                                  speed=24, stage=9, label="solid_hair_fill")

