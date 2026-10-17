"""
Clothing and traditional Indian attire rendering module.

Renders authentic festive garments with fine graphite pencil details:
- Male: Traditional kurta-pajama with mandarin collar, button placket, rolled-up sleeves,
        flowing flutter hem, loose pajama folds, and mojari slip-on shoes.
- Female: Detailed lehenga-choli with voluminous flared swirling skirt, vertical pleats,
          broad decorative hem border, fitted choli blouse, and cascading sheer dupatta
          with embroidered floral butti motifs and corner tassels.
"""

import cv2
import numpy as np
from .canvas import DrawingCanvas
from .vector_data import CATEGORIES, get_tone_density_map


def draw_kurta(canvas: DrawingCanvas):
    """
    Renders traditional Indian kurta with mandarin collar, buttons, rolled cuffs, and flutter hem.
    """
    s = canvas.scale

    # 1. Structural contour and fold paths from vector dataset
    kurta_paths = CATEGORIES.get("male_kurta", [])
    for p in kurta_paths:
        canvas.draw_path(
            p["points"],
            layer="strokes",
            darkness=0.72,
            thickness=2.0,
            jitter=0.22,
        )

    # 2. Front button placket with three distinct circular buttons
    for by in [305.0, 325.0, 345.0]:
        cv2.circle(canvas.layer_features, (int(246.0 * s), int(by * s)), int(1.5 * s), 0.92, -1, lineType=cv2.LINE_AA)

    # 3. Soft graphite tone along fabric creases and side slit
    tone_map = get_tone_density_map()
    full_tone = cv2.resize(tone_map, (canvas.INTERNAL_SIZE, canvas.INTERNAL_SIZE), interpolation=cv2.INTER_LINEAR)
    kurta_mask = np.zeros((canvas.INTERNAL_SIZE, canvas.INTERNAL_SIZE), dtype=np.float32)
    k_y1, k_y2 = int(240 * s), int(640 * s)
    k_x1, k_x2 = int(50 * s), int(440 * s)
    kurta_mask[k_y1:k_y2, k_x1:k_x2] = 1.0

    canvas.layer_shading += np.where(full_tone > 0.15, full_tone * 0.35 * kurta_mask, 0.0)


def draw_pajama(canvas: DrawingCanvas):
    """
    Renders loose traditional pajama trousers with gathers and traditional mojari shoes.
    """
    s = canvas.scale

    # 1. Pajama contours and knee/ankle folds
    pajama_paths = CATEGORIES.get("male_pajama_shoes", [])
    for p in pajama_paths:
        canvas.draw_path(
            p["points"],
            layer="strokes",
            darkness=0.72,
            thickness=2.0,
            jitter=0.22,
        )

    # 2. Traditional Indian mojari shoes details (curled toe and sole trim)
    # Raised foot mojari: (130, 830) to (170, 900)
    canvas.draw_path([(130, 840), (120, 870), (135, 895), (160, 905), (175, 885)],
                     layer="features", darkness=0.85, thickness=2.2, jitter=0.15)
    # Grounded foot mojari: (190, 915) to (275, 950)
    canvas.draw_path([(190, 920), (200, 945), (245, 955), (275, 945), (280, 930)],
                     layer="features", darkness=0.85, thickness=2.2, jitter=0.15)


def draw_lehenga(canvas: DrawingCanvas):
    """
    Renders spinning flared lehenga skirt with vertical pleats and broad decorative border.
    """
    s = canvas.scale

    # 1. Structural contours, pleats, and flared hem curves from vector dataset
    lehenga_paths = CATEGORIES.get("female_lehenga", [])
    for p in lehenga_paths:
        canvas.draw_path(
            p["points"],
            layer="strokes",
            darkness=0.75,
            thickness=2.2,
            jitter=0.22,
        )

    # 2. Broad decorative border bands near bottom hem
    # Lower hem border curves
    hem_bands = [
        [(465, 840), (530, 885), (650, 915), (780, 905), (890, 860), (955, 805)],
        [(480, 860), (545, 905), (655, 935), (785, 925), (895, 880), (945, 835)],
        [(500, 880), (565, 925), (660, 950), (790, 940), (890, 900), (935, 860)],
    ]
    for band in hem_bands:
        canvas.draw_path(band, layer="features", darkness=0.72, thickness=1.8, jitter=0.15)

    # 3. Soft graphite shading in vertical fold valleys
    tone_map = get_tone_density_map()
    full_tone = cv2.resize(tone_map, (canvas.INTERNAL_SIZE, canvas.INTERNAL_SIZE), interpolation=cv2.INTER_LINEAR)
    lehenga_mask = np.zeros((canvas.INTERNAL_SIZE, canvas.INTERNAL_SIZE), dtype=np.float32)
    l_y1, l_y2 = int(500 * s), int(960 * s)
    l_x1, l_x2 = int(450 * s), int(980 * s)
    lehenga_mask[l_y1:l_y2, l_x1:l_x2] = 1.0

    canvas.layer_shading += np.where(full_tone > 0.14, full_tone * 0.32 * lehenga_mask, 0.0)


def draw_dupatta(canvas: DrawingCanvas):
    """
    Renders cascading sheer dupatta with double decorative border, embroidered butti motifs, and tassels.
    """
    s = canvas.scale

    # 1. Dupatta drape paths and borders from vector dataset
    dupatta_paths = CATEGORIES.get("female_choli_dupatta", [])
    for p in dupatta_paths:
        canvas.draw_path(
            p["points"],
            layer="strokes",
            darkness=0.75,
            thickness=2.0,
            jitter=0.2,
        )

    # 2. Embroidered floral butti motifs (scattered 4-dot flower clusters)
    butti_centers = [
        (612, 65), (670, 110), (705, 205), (748, 222), (788, 275), (880, 395),
        (635, 395), (765, 425), (825, 580), (865, 620), (905, 665),
    ]
    for bx, by in butti_centers:
        cx_s, cy_s = int(bx * s), int(by * s)
        if 0 <= cx_s < canvas.INTERNAL_SIZE and 0 <= cy_s < canvas.INTERNAL_SIZE:
            for dx, dy in [(-2.0, 0.0), (2.0, 0.0), (0.0, -2.0), (0.0, 2.0)]:
                cv2.circle(
                    canvas.layer_features,
                    (int(cx_s + dx * s), int(cy_s + dy * s)),
                    int(1.1 * s),
                    0.78,
                    -1,
                    lineType=cv2.LINE_AA,
                )

    # 3. Hanging tassels at the corner of the dupatta
    tassels = [
        ((935, 735), (940, 755)),
        ((960, 690), (968, 708)),
    ]
    for p0, p1 in tassels:
        canvas.draw_path([p0, p1], layer="features", darkness=0.85, thickness=2.2, jitter=0.1)
        # Small conical tassel flare
        canvas.draw_path([(p1[0] - 3, p1[1] + 5), p1, (p1[0] + 3, p1[1] + 5)],
                         layer="features", darkness=0.8, thickness=1.6, jitter=0.1)


def draw_choli(canvas: DrawingCanvas):
    """
    Renders fitted choli blouse with sleeve embroidery trim and seam lines.
    """
    # Blouse sleeve embroidery band
    canvas.draw_path([(638, 385), (662, 420)], layer="features", darkness=0.82, thickness=2.2, jitter=0.1)
    canvas.draw_path([(642, 388), (666, 423)], layer="features", darkness=0.75, thickness=1.5, jitter=0.1)
    # Waist hem seam
    canvas.draw_path([(678, 480), (730, 485)], layer="features", darkness=0.82, thickness=2.0, jitter=0.1)
