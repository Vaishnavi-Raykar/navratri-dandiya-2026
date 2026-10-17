"""Drawing helpers, loaded lazily so the animator needs no OpenCV."""
from importlib import import_module

_EXPORTS = {'DrawingCanvas': 'canvas', 'draw_couple': 'characters', 'draw_male_character': 'characters', 'draw_female_character': 'characters', 'draw_pencil_stroke': 'pencil_effects', 'draw_curved_line': 'pencil_effects', 'draw_bezier_curve': 'pencil_effects', 'draw_ellipse': 'pencil_effects', 'draw_polygon_outline': 'pencil_effects', 'draw_cross_hatching': 'pencil_effects', 'apply_paper_texture': 'pencil_effects', 'draw_face_features': 'faces', 'draw_male_face': 'faces', 'draw_female_face': 'faces', 'draw_hair_strands': 'hair', 'draw_male_hair': 'hair', 'draw_female_hair': 'hair', 'draw_kurta': 'clothing', 'draw_lehenga': 'clothing', 'draw_dupatta': 'clothing', 'draw_pajama': 'clothing', 'draw_choli': 'clothing', 'draw_dandiya_stick': 'accessories', 'draw_hand_and_fingers': 'accessories', 'draw_jewellery': 'accessories', 'draw_ground_shadows': 'accessories', 'draw_motion_marks': 'accessories'}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module("." + _EXPORTS[name], __name__), name)
    globals()[name] = value
    return value
