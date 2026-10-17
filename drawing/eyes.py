"""Clean eye geometry in the traced artwork's source coordinates."""
from .vector_data import CATEGORIES

# Exclude old eye fragments, including paths that continue into the nose.
# Splitting paths preserves the remaining nose, jaw and hairline geometry.
REGIONS = {"male": [(303, 127, 320, 141), (325, 129, 336, 141)],
           "female": [(676, 190, 690, 211), (696, 191, 715, 219)]}


def clean_face_paths(character):
    def inside(pt):
        x, y = pt
        return any(x0 <= x <= x1 and y0 <= y <= y1
                   for x0, y0, x1, y1 in REGIONS[character])
    result = []
    for path in CATEGORIES[character + "_face"]:
        run = []
        for pt in path["points"]:
            if inside(pt):
                if len(run) > 1:
                    result.append(dict(path, points=run))
                run = []
            else:
                run.append(pt)
        if len(run) > 1:
            result.append(dict(path, points=run))
    return result


def eye_paths(character):
    import json
    from pathlib import Path
    paths = json.loads(Path(__file__).with_name("reference_eyes.json").read_text())
    return paths[character]
