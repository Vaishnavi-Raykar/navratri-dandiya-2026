"""
Accessories, dandiya sticks, hands, jewelry, and action marks rendering module.

Renders:
- Four patterned dandiya sticks (criss-cross diamond bands and diagonal helical stripes)
- Anatomically accurate hands with fingers visibly gripping each stick
- Traditional jewelry: bangles on both wrists, jhumka earring
- Action motion dashes and rhythm sparks radiating from the stick tips
- Ground shadow horizontal pencil hatching strokes beneath both characters' feet
"""

import cv2
import numpy as np
from .canvas import DrawingCanvas
from .vector_data import CATEGORIES


def draw_dandiya_stick(canvas: DrawingCanvas, stick_id: int):
    """
    Renders one of the four decorated dandiya sticks.
    """
    if stick_id == 1:
        # Male top stick: (375, 205) to (425, 70)
        p_base = (375.0, 205.0)
        p_tip = (425.0, 70.0)
        # Main stick outline
        canvas.draw_path([p_base, p_tip], layer="strokes", darkness=0.88, thickness=3.2, jitter=0.1)
        # Diamond criss-cross pattern
        for t in np.linspace(0.15, 0.95, 8):
            px = p_base[0] + (p_tip[0] - p_base[0]) * t
            py = p_base[1] + (p_tip[1] - p_base[1]) * t
            canvas.draw_path([(px - 4, py - 3), (px + 4, py + 3)], layer="features", darkness=0.75, thickness=1.5, jitter=0.08)
            canvas.draw_path([(px + 4, py - 3), (px - 4, py + 3)], layer="features", darkness=0.75, thickness=1.5, jitter=0.08)

    elif stick_id == 2:
        # Male forward stick: (370, 460) to (505, 360)
        p_base = (370.0, 460.0)
        p_tip = (505.0, 360.0)
        canvas.draw_path([p_base, p_tip], layer="strokes", darkness=0.88, thickness=3.2, jitter=0.1)
        # Diagonal stripe pattern
        for t in np.linspace(0.2, 0.95, 7):
            px = p_base[0] + (p_tip[0] - p_base[0]) * t
            py = p_base[1] + (p_tip[1] - p_base[1]) * t
            canvas.draw_path([(px - 3, py - 4), (px + 3, py + 4)], layer="features", darkness=0.75, thickness=1.5, jitter=0.08)

    elif stick_id == 3:
        # Female top stick: (550, 300) to (590, 150)
        p_base = (550.0, 300.0)
        p_tip = (590.0, 150.0)
        canvas.draw_path([p_base, p_tip], layer="strokes", darkness=0.88, thickness=3.2, jitter=0.1)
        # Diagonal stripes
        for t in np.linspace(0.15, 0.95, 8):
            px = p_base[0] + (p_tip[0] - p_base[0]) * t
            py = p_base[1] + (p_tip[1] - p_base[1]) * t
            canvas.draw_path([(px - 4, py - 3), (px + 4, py + 3)], layer="features", darkness=0.75, thickness=1.5, jitter=0.08)

    elif stick_id == 4:
        # Female lower stick: (605, 580) to (520, 505)
        p_base = (605.0, 580.0)
        p_tip = (520.0, 505.0)
        canvas.draw_path([p_base, p_tip], layer="strokes", darkness=0.88, thickness=3.2, jitter=0.1)
        # Diagonal stripes
        for t in np.linspace(0.2, 0.95, 6):
            px = p_base[0] + (p_tip[0] - p_base[0]) * t
            py = p_base[1] + (p_tip[1] - p_base[1]) * t
            canvas.draw_path([(px - 3, py + 4), (px + 3, py - 4)], layer="features", darkness=0.75, thickness=1.5, jitter=0.08)


def draw_hand_and_fingers(canvas: DrawingCanvas, hand_id: int):
    """
    Renders anatomically correct hands with fingers wrapped around the stick.
    """
    # Vector paths for arms and sticks include exact hand contours
    if hand_id in [1, 2]:
        for p in CATEGORIES.get("male_arms_sticks", []):
            canvas.draw_path(p["points"], layer="strokes", darkness=0.78, thickness=2.2, jitter=0.18)
    else:
        for p in CATEGORIES.get("female_arms_sticks", []):
            canvas.draw_path(p["points"], layer="strokes", darkness=0.78, thickness=2.2, jitter=0.18)


def draw_jewellery(canvas: DrawingCanvas):
    """
    Renders bangles on both wrists.
    """
    # Female Raised Wrist Bangles: (552, 345) to (572, 362)
    for i in range(4):
        b_pts = [(552.0 + i * 3.5, 345.0 + i * 2.2), (568.0 + i * 3.5, 355.0 + i * 2.2)]
        canvas.draw_path(b_pts, layer="features", darkness=0.88, thickness=2.2, jitter=0.08)

    # Female Lower Wrist Bangles: (612, 545) to (628, 560)
    for i in range(4):
        b_pts = [(612.0 + i * 2.2, 545.0 + i * 3.2), (626.0 + i * 2.2, 555.0 + i * 3.2)]
        canvas.draw_path(b_pts, layer="features", darkness=0.88, thickness=2.2, jitter=0.08)


def draw_motion_marks(canvas: DrawingCanvas):
    """
    Renders action dashes and rhythm sparks radiating from the dandiya stick tips.
    """
    motion_marks = [
        # Male top stick sparks
        [(420.0, 115.0), (442.0, 130.0)],
        [(425.0, 150.0), (446.0, 153.0)],
        [(385.0, 105.0), (370.0, 95.0)],
        # Male forward stick sparks
        [(440.0, 420.0), (462.0, 415.0)],
        [(425.0, 455.0), (448.0, 465.0)],
        # Female top stick sparks
        [(585.0, 185.0), (612.0, 195.0)],
        [(615.0, 235.0), (638.0, 230.0)],
        [(545.0, 260.0), (522.0, 270.0)],
        [(565.0, 305.0), (542.0, 315.0)],
        [(630.0, 320.0), (645.0, 335.0)],
        # Female lower stick sparks
        [(500.0, 520.0), (480.0, 515.0)],
        [(530.0, 480.0), (515.0, 470.0)],
    ]
    for mm in motion_marks:
        canvas.draw_path(mm, layer="features", darkness=0.68, thickness=1.8, jitter=0.1)


def draw_ground_shadows(canvas: DrawingCanvas):
    """
    Renders soft horizontal graphite pencil strokes beneath both characters' feet.
    """
    # Ground motion and hatching paths from vector dataset
    ground_paths = CATEGORIES.get("ground_motion", [])
    for p in ground_paths:
        canvas.draw_path(p["points"], layer="strokes", darkness=0.48, thickness=1.6, jitter=0.25)

    # Layered horizontal graphite pencil hatching under feet
    # Beneath male feet: x in [100, 320], y ~ 920-960
    for y in range(920, 965, 5):
        w = 120.0 + (965 - y) * 1.5
        canvas.draw_path([(130.0 - w * 0.2, float(y)), (130.0 + w * 0.8, float(y))],
                         layer="shading", darkness=0.28, thickness=1.4, jitter=0.2)

    # Beneath female lehenga and feet: x in [560, 880], y ~ 935-970
    for y in range(935, 975, 5):
        w = 260.0 + (975 - y) * 1.8
        canvas.draw_path([(600.0 - w * 0.1, float(y)), (600.0 + w * 0.9, float(y))],
                         layer="shading", darkness=0.28, thickness=1.4, jitter=0.2)
