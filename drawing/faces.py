"""
Facial features rendering module for both male and female characters.
"""

import cv2
import numpy as np
from .canvas import DrawingCanvas
from .vector_data import CATEGORIES


def draw_face_features(canvas: DrawingCanvas, character: str = "male"):
    """
    Renders the facial features of the specified character.
    """
    if character.lower() == "male":
        draw_male_face(canvas)
    else:
        draw_female_face(canvas)


def draw_male_face(canvas: DrawingCanvas):
    """
    Renders the male character's face, features, ear, and neck contours.
    """
    # 1. Draw structural contour paths from vector dataset
    male_face_paths = CATEGORIES.get("male_face", [])
    for p in male_face_paths:
        canvas.draw_path(
            p["points"],
            layer="strokes",
            darkness=0.88,
            thickness=2.0,
            jitter=0.15,
        )

    s = canvas.scale

    # 2. Pupil core fill and catchlight in right eye (3/4 view)
    m_eye_pupil = (int(290.0 * s), int(176.0 * s))
    cv2.circle(canvas.layer_features, m_eye_pupil, int(2.0 * s), 0.95, -1, lineType=cv2.LINE_AA)
    # Catchlight white highlight
    cv2.circle(canvas.layer_features, (int(289.0 * s), int(175.0 * s)), int(0.75 * s), 0.0, -1, lineType=cv2.LINE_AA)

    # Eyebrow fine hair feathering
    for bx in range(275, 301, 3):
        canvas.draw_path([(bx, 166.0), (bx + 1.2, 162.5)], layer="features", darkness=0.6, thickness=1.2, jitter=0.08)

    # Teeth shading in mouth opening
    teeth_poly = canvas.scale_pts([(290, 224), (305, 228), (298, 233)])
    cv2.fillPoly(canvas.layer_features, [np.int32(teeth_poly)], 0.22, lineType=cv2.LINE_AA)

    # Subtle cheek blush hatching
    for dy in range(0, 12, 3):
        p_b0 = (275.0 + dy * 0.5, 195.0 + dy)
        p_b1 = (282.0 + dy * 0.5, 192.0 + dy)
        canvas.draw_path([p_b0, p_b1], layer="features", darkness=0.35, thickness=1.2, jitter=0.08)

    # Neck tendon shadow cross-hatching
    canvas.draw_cross_hatching_region((245, 240), 25, 25, angle=55.0, spacing=4.0, darkness=0.22, layer="shading")


def draw_female_face(canvas: DrawingCanvas):
    """
    Renders the female character's face, anime eyes, smile, ear, and Indian jhumka earring.
    """
    # 1. Structural contour paths from vector dataset
    female_face_paths = CATEGORIES.get("female_face", [])
    for p in female_face_paths:
        canvas.draw_path(
            p["points"],
            layer="strokes",
            darkness=0.90,
            thickness=2.0,
            jitter=0.15,
        )

    s = canvas.scale

    # 2. Pupil core accents and sparkling catchlights inside anime eyes
    # Right eye pupil
    f_pupil_r = (int(692.0 * s), int(276.5 * s))
    cv2.circle(canvas.layer_features, f_pupil_r, int(3.0 * s), 0.95, -1, lineType=cv2.LINE_AA)
    # Double catchlight sparkle
    cv2.circle(canvas.layer_features, (int(690.5 * s), int(274.5 * s)), int(1.1 * s), 0.0, -1, lineType=cv2.LINE_AA)
    cv2.circle(canvas.layer_features, (int(693.5 * s), int(278.5 * s)), int(0.6 * s), 0.0, -1, lineType=cv2.LINE_AA)

    # Left eye pupil
    f_pupil_l = (int(723.0 * s), int(285.5 * s))
    cv2.circle(canvas.layer_features, f_pupil_l, int(2.2 * s), 0.92, -1, lineType=cv2.LINE_AA)
    cv2.circle(canvas.layer_features, (int(721.5 * s), int(284.0 * s)), int(0.7 * s), 0.0, -1, lineType=cv2.LINE_AA)

    # Teeth shading in smile
    teeth_f_poly = canvas.scale_pts([(681, 322), (700, 326), (690, 332)])
    cv2.fillPoly(canvas.layer_features, [np.int32(teeth_f_poly)], 0.22, lineType=cv2.LINE_AA)

    # Delicate cheek blush hatching lines
    for dy in range(0, 15, 3):
        p_b0 = (698.0 + dy * 0.5, 295.0 + dy)
        p_b1 = (706.0 + dy * 0.5, 291.0 + dy)
        canvas.draw_path([p_b0, p_b1], layer="features", darkness=0.38, thickness=1.2, jitter=0.08)

    # Traditional Indian Dangling Jhumka Earring
    jh_stud = (int(742.0 * s), int(335.0 * s))
    cv2.circle(canvas.layer_features, jh_stud, int(2.0 * s), 0.90, -1, lineType=cv2.LINE_AA)
    cv2.line(canvas.layer_features, jh_stud, (int(742.0 * s), int(342.0 * s)), 0.85, int(1.5 * s), lineType=cv2.LINE_AA)
    jh_bell = [(735.0, 350.0), (742.0, 343.0), (749.0, 350.0), (750.0, 355.0), (734.0, 355.0), (735.0, 350.0)]
    canvas.draw_path(jh_bell, layer="features", darkness=0.88, thickness=2.0, jitter=0.08)
    canvas.draw_path([(734.0, 353.0), (750.0, 353.0)], layer="features", darkness=0.82, thickness=1.5, jitter=0.08)
    for px in [736.0, 740.0, 744.0, 748.0]:
        cv2.circle(canvas.layer_features, (int(px * s), int(358.0 * s)), int(1.2 * s), 0.88, -1, lineType=cv2.LINE_AA)
