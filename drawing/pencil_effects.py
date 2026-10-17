"""
Pencil effects and procedural stroke rendering algorithms.

Simulates genuine graphite pencil illustration techniques:
- Natural hand micro-jitter and organic line tremor
- Dynamic pressure tapering (tapered entry and release)
- Multi-pass layered sketching (underdrawing, primary contour, deep accent)
- Microscopic graphite particle grain catching paper tooth
- Directional cross-hatching and shading fields
- Realistic warm off-white fibrous paper texture
"""

import math
import cv2
import numpy as np


def catmull_rom_spline(pts: np.ndarray, num_points_per_seg: int = 8) -> np.ndarray:
    """
    Evaluates a uniform Catmull-Rom spline through a sequence of 2D control points.
    
    Args:
        pts: Array of shape (N, 2) defining control points.
        num_points_per_seg: Number of interpolated points per segment.
        
    Returns:
        Smooth array of interpolated points of shape (M, 2).
    """
    if len(pts) < 2:
        return pts
    if len(pts) == 2:
        p0, p1 = pts[0], pts[1]
        t = np.linspace(0, 1, num_points_per_seg)[:, None]
        return (1 - t) * p0 + t * p1

    padded = np.vstack([pts[0] - (pts[1] - pts[0]), pts, pts[-1] + (pts[-1] - pts[-2])])
    spline_points = []

    t = np.linspace(0, 1, num_points_per_seg, endpoint=False)[:, None]
    t2 = t * t
    t3 = t2 * t

    for i in range(1, len(padded) - 2):
        p0, p1, p2, p3 = padded[i - 1], padded[i], padded[i + 1], padded[i + 2]
        seg = 0.5 * (
            (2 * p1)
            + (-p0 + p2) * t
            + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
            + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
        )
        spline_points.append(seg)
    spline_points.append(padded[-2:])
    return np.vstack(spline_points)


def draw_bezier_curve(
    layer: np.ndarray,
    p0: tuple,
    p1: tuple,
    p2: tuple,
    p3: tuple,
    steps: int = 50,
    darkness: float = 0.75,
    thickness: float = 2.0,
    jitter: float = 0.2,
    rng: np.random.Generator = None,
):
    """
    Renders a cubic Bézier curve using graphite pencil strokes.
    
    Args:
        layer: Target float32 2D canvas layer.
        p0, p1, p2, p3: Four 2D control points (x, y).
        steps: Number of evaluation steps along the curve.
        darkness: Graphite intensity (0.0 to 1.0).
        thickness: Stroke line width in pixels.
        jitter: Amplitude of perpendicular hand-drawn jitter.
        rng: NumPy random generator for deterministic noise.
    """
    t = np.linspace(0.0, 1.0, steps)[:, None]
    p0_a = np.array(p0, dtype=np.float32)
    p1_a = np.array(p1, dtype=np.float32)
    p2_a = np.array(p2, dtype=np.float32)
    p3_a = np.array(p3, dtype=np.float32)

    bezier_pts = (
        (1.0 - t) ** 3 * p0_a
        + 3.0 * (1.0 - t) ** 2 * t * p1_a
        + 3.0 * (1.0 - t) * t ** 2 * p2_a
        + t ** 3 * p3_a
    )
    draw_pencil_stroke(layer, bezier_pts, darkness=darkness, thickness=thickness, jitter=jitter, rng=rng)


def draw_curved_line(
    layer: np.ndarray,
    points: list | np.ndarray,
    darkness: float = 0.75,
    thickness: float = 2.0,
    jitter: float = 0.25,
    rng: np.random.Generator = None,
):
    """
    Draws a smooth organic curved line passing through given control points.
    """
    draw_pencil_stroke(layer, points, darkness=darkness, thickness=thickness, jitter=jitter, rng=rng)


def draw_ellipse(
    layer: np.ndarray,
    center: tuple,
    axes: tuple,
    angle: float = 0.0,
    start_angle: float = 0.0,
    end_angle: float = 360.0,
    darkness: float = 0.75,
    thickness: float = 2.0,
    steps: int = 72,
    jitter: float = 0.2,
    rng: np.random.Generator = None,
):
    """
    Draws an organic pencil ellipse or elliptical arc.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    cx, cy = center
    rx, ry = axes
    theta = np.linspace(np.radians(start_angle), np.radians(end_angle), steps)
    rot = np.radians(angle)

    cos_r, sin_r = np.cos(rot), np.sin(rot)
    xs = cx + rx * np.cos(theta) * cos_r - ry * np.sin(theta) * sin_r
    ys = cy + rx * np.cos(theta) * sin_r + ry * np.sin(theta) * cos_r

    pts = np.column_stack([xs, ys])
    draw_pencil_stroke(layer, pts, darkness=darkness, thickness=thickness, jitter=jitter, rng=rng)


def draw_polygon_outline(
    layer: np.ndarray,
    points: list | np.ndarray,
    is_closed: bool = True,
    darkness: float = 0.75,
    thickness: float = 2.0,
    jitter: float = 0.25,
    rng: np.random.Generator = None,
):
    """
    Renders an open or closed polygon outline with pencil variation.
    """
    pts = np.array(points, dtype=np.float32)
    if is_closed and len(pts) > 2 and not np.allclose(pts[0], pts[-1]):
        pts = np.vstack([pts, pts[0]])
    draw_pencil_stroke(layer, pts, darkness=darkness, thickness=thickness, jitter=jitter, rng=rng)


def draw_pencil_stroke(
    layer: np.ndarray,
    points: list | np.ndarray,
    darkness: float = 0.75,
    thickness: float = 2.2,
    jitter: float = 0.3,
    rng: np.random.Generator = None,
):
    """
    Renders a realistic graphite pencil stroke with natural hand micro-jitter,
    spline smoothing, and multi-pass layering onto a float32 canvas layer.
    """
    if len(points) < 2:
        return
    if rng is None:
        rng = np.random.default_rng(42)

    pts = np.array(points, dtype=np.float32)
    diffs = np.diff(pts, axis=0)
    seg_lens = np.sqrt(np.sum(diffs ** 2, axis=1))
    total_len = np.sum(seg_lens)
    if total_len < 1.5:
        return

    num_pts = max(int(total_len / 4.0), 6)
    pts_per_seg = max(3, int(num_pts / max(1, len(pts))))
    smooth_pts = catmull_rom_spline(pts, num_points_per_seg=pts_per_seg)

    # Perpendicular normals for natural micro-jitter
    tangents = np.gradient(smooth_pts, axis=0)
    norms = np.sqrt(np.sum(tangents ** 2, axis=1, keepdims=True)) + 1e-5
    normals = np.hstack([-tangents[:, 1:2] / norms, tangents[:, 0:1] / norms])

    jit = rng.normal(0, jitter, (len(smooth_pts), 1))
    smooth_pts = smooth_pts + normals * jit

    # 1. Underdrawing pass (faint guide stroke, slightly wider)
    under_pts = smooth_pts + rng.normal(0, 0.35, smooth_pts.shape)
    cv2.polylines(
        layer,
        [np.int32(under_pts)],
        isClosed=False,
        color=float(darkness * 0.22),
        thickness=max(1, int(thickness + 1.2)),
        lineType=cv2.LINE_AA,
    )

    # 2. Primary graphite contour stroke (HB/2B)
    cv2.polylines(
        layer,
        [np.int32(smooth_pts)],
        isClosed=False,
        color=float(darkness * 0.85),
        thickness=max(1, int(thickness)),
        lineType=cv2.LINE_AA,
    )


def draw_cross_hatching(
    layer: np.ndarray,
    origin: tuple,
    width: float,
    height: float,
    angle: float = 45.0,
    spacing: float = 8.0,
    darkness: float = 0.35,
    thickness: float = 1.2,
    cross: bool = False,
    rng: np.random.Generator = None,
):
    """
    Renders directional pencil hatching / cross-hatching inside a bounding box.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    ox, oy = origin
    diag = math.hypot(width, height)
    num_lines = int(diag / spacing)

    rad = math.radians(angle)
    dx = math.cos(rad) * diag
    dy = math.sin(rad) * diag
    px = -math.sin(rad)
    py = math.cos(rad)

    for i in range(-num_lines // 2, num_lines // 2 + 1):
        offset = i * spacing + rng.normal(0, spacing * 0.1)
        p0 = (ox + width / 2 + px * offset - dx / 2, oy + height / 2 + py * offset - dy / 2)
        p1 = (ox + width / 2 + px * offset + dx / 2, oy + height / 2 + py * offset + dy / 2)
        draw_pencil_stroke(layer, [p0, p1], darkness=darkness, thickness=thickness, jitter=0.15, rng=rng)

    if cross:
        rad2 = math.radians(angle + 90.0)
        dx2 = math.cos(rad2) * diag
        dy2 = math.sin(rad2) * diag
        px2 = -math.sin(rad2)
        py2 = math.cos(rad2)
        for i in range(-num_lines // 2, num_lines // 2 + 1):
            offset = i * spacing + rng.normal(0, spacing * 0.1)
            p0 = (ox + width / 2 + px2 * offset - dx2 / 2, oy + height / 2 + py2 * offset - dy2 / 2)
            p1 = (ox + width / 2 + px2 * offset + dx2 / 2, oy + height / 2 + py2 * offset + dy2 / 2)
            draw_pencil_stroke(layer, [p0, p1], darkness=darkness * 0.8, thickness=thickness, jitter=0.15, rng=rng)


def apply_paper_texture(
    drawing_gray: np.ndarray,
    seed: int = 42,
    warmth: tuple = (252.0, 250.0, 246.0),
) -> np.ndarray:
    """
    Applies microscopic paper tooth grain, fine fibers, and natural warm tint.
    
    Args:
        drawing_gray: 2D uint8 grayscale image (0 to 255).
        seed: Random seed for procedural paper tooth noise.
        warmth: RGB multipliers representing off-white paper base color.
        
    Returns:
        RGB uint8 image of shape (H, W, 3).
    """
    rng = np.random.default_rng(seed)
    h, w = drawing_gray.shape

    # Microscopic paper tooth grain
    tooth = rng.uniform(0.96, 1.0, (h, w)).astype(np.float32)

    # Subtle paper fiber noise
    fibers = rng.normal(0.0, 1.2, (h, w)).astype(np.float32)

    textured_gray = drawing_gray.astype(np.float32) * tooth + fibers
    textured_gray = np.clip(textured_gray, 0.0, 255.0)

    # Apply authentic warm off-white paper tone
    r_mult = warmth[0] / 255.0
    g_mult = warmth[1] / 255.0
    b_mult = warmth[2] / 255.0

    r_ch = np.clip(textured_gray * r_mult, 0.0, 255.0).astype(np.uint8)
    g_ch = np.clip(textured_gray * g_mult, 0.0, 255.0).astype(np.uint8)
    b_ch = np.clip(textured_gray * b_mult, 0.0, 255.0).astype(np.uint8)

    return np.stack([r_ch, g_ch, b_ch], axis=-1)
