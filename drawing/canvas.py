"""
High-resolution Canvas and Layer Manager for Pencil Sketch Drawing.

Manages high-resolution multi-layer canvas (2496 x 2496) and provides high-quality
downsampling to 1248 x 1248 with graphite grain simulation, paper texture blending,
and multi-layer compositing.
"""

import os
import cv2
import numpy as np
from PIL import Image

from .pencil_effects import (
    draw_pencil_stroke,
    draw_curved_line,
    draw_bezier_curve,
    draw_ellipse,
    draw_polygon_outline,
    draw_cross_hatching,
    apply_paper_texture,
)


class DrawingCanvas:
    """
    Multi-layer drawing canvas supporting high-resolution procedural pencil rendering.
    """

    INTERNAL_SIZE = 2496
    TARGET_SIZE = 1248
    BASE_COORD_SIZE = 1024.0

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.scale = self.INTERNAL_SIZE / self.BASE_COORD_SIZE

        # Canvas layers (float32, 0.0=clear paper, 1.0=full graphite deposition)
        self.layer_shading = np.zeros((self.INTERNAL_SIZE, self.INTERNAL_SIZE), dtype=np.float32)
        self.layer_strokes = np.zeros((self.INTERNAL_SIZE, self.INTERNAL_SIZE), dtype=np.float32)
        self.layer_features = np.zeros((self.INTERNAL_SIZE, self.INTERNAL_SIZE), dtype=np.float32)
        self.layer_accents = np.zeros((self.INTERNAL_SIZE, self.INTERNAL_SIZE), dtype=np.float32)

    def scale_pt(self, x: float, y: float) -> tuple[float, float]:
        """Scales coordinate from base 1024 system to internal 2496 canvas."""
        return (x * self.scale, y * self.scale)

    def scale_pts(self, pts: list | np.ndarray) -> np.ndarray:
        """Scales an array of coordinates to internal 2496 canvas."""
        return np.array(pts, dtype=np.float32) * self.scale

    def draw_path(
        self,
        points: list | np.ndarray,
        layer: str = "strokes",
        darkness: float = 0.75,
        thickness: float = 2.2,
        jitter: float = 0.25,
    ):
        """Draws an organic pencil path on the specified layer."""
        target_layer = self._get_layer(layer)
        scaled_pts = self.scale_pts(points)
        draw_pencil_stroke(
            target_layer,
            scaled_pts,
            darkness=darkness,
            thickness=thickness * (self.scale / 2.0),
            jitter=jitter * (self.scale / 2.0),
            rng=self.rng,
        )

    def draw_bezier(
        self,
        p0: tuple,
        p1: tuple,
        p2: tuple,
        p3: tuple,
        layer: str = "strokes",
        darkness: float = 0.75,
        thickness: float = 2.0,
        jitter: float = 0.2,
    ):
        """Draws a cubic Bézier curve on the specified layer."""
        target_layer = self._get_layer(layer)
        draw_bezier_curve(
            target_layer,
            self.scale_pt(*p0),
            self.scale_pt(*p1),
            self.scale_pt(*p2),
            self.scale_pt(*p3),
            steps=60,
            darkness=darkness,
            thickness=thickness * (self.scale / 2.0),
            jitter=jitter * (self.scale / 2.0),
            rng=self.rng,
        )

    def draw_ellipse_shape(
        self,
        center: tuple,
        axes: tuple,
        angle: float = 0.0,
        layer: str = "features",
        darkness: float = 0.75,
        thickness: float = 1.8,
    ):
        """Draws an ellipse outline on the specified layer."""
        target_layer = self._get_layer(layer)
        scaled_center = self.scale_pt(*center)
        scaled_axes = (axes[0] * self.scale, axes[1] * self.scale)
        draw_ellipse(
            target_layer,
            scaled_center,
            scaled_axes,
            angle=angle,
            darkness=darkness,
            thickness=thickness * (self.scale / 2.0),
            rng=self.rng,
        )

    def draw_cross_hatching_region(
        self,
        origin: tuple,
        width: float,
        height: float,
        angle: float = 45.0,
        spacing: float = 6.0,
        darkness: float = 0.35,
        layer: str = "shading",
        cross: bool = False,
    ):
        """Draws directional pencil cross-hatching inside a rectangular region."""
        target_layer = self._get_layer(layer)
        ox, oy = self.scale_pt(*origin)
        w, h = width * self.scale, height * self.scale
        draw_cross_hatching(
            target_layer,
            (ox, oy),
            w,
            h,
            angle=angle,
            spacing=spacing * self.scale,
            darkness=darkness,
            thickness=1.2 * (self.scale / 2.0),
            cross=cross,
            rng=self.rng,
        )

    def _get_layer(self, layer_name: str) -> np.ndarray:
        if layer_name == "shading":
            return self.layer_shading
        elif layer_name == "features":
            return self.layer_features
        elif layer_name == "accents":
            return self.layer_accents
        return self.layer_strokes

    def composite(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Composites all layers with graphite grain, builds natural paper tooth,
        and returns both the downsampled 1248x1248 RGB image and full 2496x2496 HD RGB image.
        """
        rng = np.random.default_rng(self.seed)

        # High-resolution graphite grain noise
        graphite_grain = rng.uniform(0.88, 1.0, (self.INTERNAL_SIZE, self.INTERNAL_SIZE)).astype(np.float32)

        # Composite graphite layers
        total_darkness = np.clip(
            self.layer_shading * 0.85
            + self.layer_strokes * graphite_grain * 0.95
            + self.layer_features * graphite_grain * 1.0
            + self.layer_accents * graphite_grain * 1.05,
            0.0,
            1.0,
        )

        # Convert darkness into graphite on white paper
        drawing_gray = np.clip(255.0 * (1.0 - total_darkness), 0.0, 255.0).astype(np.uint8)

        # Apply realistic paper tooth and warm color tone
        final_hd_rgb = apply_paper_texture(drawing_gray, seed=self.seed)

        # Downsample to 1248 x 1248 using high quality INTER_AREA filter
        final_1248_rgb = cv2.resize(
            final_hd_rgb,
            (self.TARGET_SIZE, self.TARGET_SIZE),
            interpolation=cv2.INTER_AREA,
        )

        return final_1248_rgb, final_hd_rgb

    def save(self, filepath: str, hd_filepath: str = None) -> tuple[str, str | None]:
        """
        Composites and saves the sketch to the specified filepath(s).
        """
        out_dir = os.path.dirname(os.path.abspath(filepath))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        final_1248, final_hd = self.composite()

        # Save primary 1248x1248 image (convert RGB to BGR for OpenCV write)
        cv2.imwrite(filepath, cv2.cvtColor(final_1248, cv2.COLOR_RGB2BGR))

        # Optionally save HD 2496x2496 image
        saved_hd = None
        if hd_filepath:
            hd_dir = os.path.dirname(os.path.abspath(hd_filepath))
            if hd_dir:
                os.makedirs(hd_dir, exist_ok=True)
            cv2.imwrite(hd_filepath, cv2.cvtColor(final_hd, cv2.COLOR_RGB2BGR))
            saved_hd = hd_filepath

        return filepath, saved_hd
