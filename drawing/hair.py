"""
Hair rendering module for both male and female characters.
"""

import cv2
import numpy as np
from .canvas import DrawingCanvas
from .vector_data import CATEGORIES, get_tone_density_map


def draw_hair_strands(canvas: DrawingCanvas, character: str = "male"):
    """
    Renders hair volume, individual locks, and flowing strands.
    """
    if character.lower() == "male":
        draw_male_hair(canvas)
    else:
        draw_female_hair(canvas)


def draw_male_hair(canvas: DrawingCanvas):
    """
    Renders thick, voluminous, tousled black hair for the male character.
    """
    s = canvas.scale

    # 1. Base graphite tone inside hair: smooth thresholding without box artifacts
    tone_map = get_tone_density_map()
    full_tone = cv2.resize(tone_map, (canvas.INTERNAL_SIZE, canvas.INTERNAL_SIZE), interpolation=cv2.INTER_CUBIC)

    # Hair tone only activates where density > 0.22, smoothly tapering to zero
    hair_tone = np.clip((full_tone - 0.22) / 0.45, 0.0, 1.0) * 0.75

    # Restrict to male upper body region
    m_mask = np.zeros((canvas.INTERNAL_SIZE, canvas.INTERNAL_SIZE), dtype=np.float32)
    m_y1, m_y2 = int(80 * s), int(260 * s)
    m_x1, m_x2 = int(140 * s), int(360 * s)
    m_mask[m_y1:m_y2, m_x1:m_x2] = 1.0

    # Clear face area from hair shading
    cv2.circle(m_mask, (int(290 * s), int(210 * s)), int(40 * s), 0.0, -1)

    canvas.layer_shading += hair_tone * m_mask

    # 2. Draw lock contours and tuft strokes
    hair_paths = CATEGORIES.get("male_hair", [])
    for p in hair_paths:
        canvas.draw_path(
            p["points"],
            layer="strokes",
            darkness=0.90,
            thickness=2.4,
            jitter=0.18,
        )


def draw_female_hair(canvas: DrawingCanvas):
    """
    Renders long, thick, flowing dark hair cascading below her shoulders with flower accessory.
    """
    s = canvas.scale

    # 1. Base graphite tone inside female hair: smooth thresholding
    tone_map = get_tone_density_map()
    full_tone = cv2.resize(tone_map, (canvas.INTERNAL_SIZE, canvas.INTERNAL_SIZE), interpolation=cv2.INTER_CUBIC)

    hair_tone = np.clip((full_tone - 0.20) / 0.45, 0.0, 1.0) * 0.82

    # Restrict to female upper body region
    f_mask = np.zeros((canvas.INTERNAL_SIZE, canvas.INTERNAL_SIZE), dtype=np.float32)
    f_y1, f_y2 = int(180 * s), int(530 * s)
    f_x1, f_x2 = int(620 * s), int(880 * s)
    f_mask[f_y1:f_y2, f_x1:f_x2] = 1.0

    # Clear face skin & flower from hair tone
    cv2.circle(f_mask, (int(705 * s), int(310 * s)), int(42 * s), 0.0, -1)
    cv2.circle(f_mask, (int(808 * s), int(306 * s)), int(26 * s), 0.0, -1)

    canvas.layer_shading += hair_tone * f_mask

    # 2. Draw lock contours from vector dataset
    hair_paths = CATEGORIES.get("female_hair", [])
    for p in hair_paths:
        canvas.draw_path(
            p["points"],
            layer="strokes",
            darkness=0.92,
            thickness=2.4,
            jitter=0.18,
        )

    # 3. Decorative flower tucked behind ear
    fl_c = (808.0, 306.0)
    for ang_deg in [0, 72, 144, 216, 288]:
        ang = np.radians(ang_deg)
        p_petal = (fl_c[0] + np.cos(ang) * 14.0, fl_c[1] + np.sin(ang) * 14.0)
        p_side1 = (fl_c[0] + np.cos(ang - 0.4) * 8.0, fl_c[1] + np.sin(ang - 0.4) * 8.0)
        p_side2 = (fl_c[0] + np.cos(ang + 0.4) * 8.0, fl_c[1] + np.sin(ang + 0.4) * 8.0)
        pts_pet = [fl_c, p_side1, p_petal, p_side2, fl_c]
        canvas.draw_path(pts_pet, layer="features", darkness=0.85, thickness=1.8, jitter=0.08)

    # Stamen center dot
    cv2.circle(canvas.layer_features, (int(fl_c[0] * s), int(fl_c[1] * s)), int(2.5 * s), 0.92, -1, lineType=cv2.LINE_AA)
