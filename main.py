"""
main.py — Indian Couple Dandiya Pencil Sketch Animator

Run:
    python main.py

Controls (while the window is open):
    Space       Pause / Resume
    ↑ / ↓       Increase / Decrease drawing speed (0.25× … 8×)
    R           Restart animation from blank canvas
    S           Save current canvas immediately
    Esc         Quit (auto-saves if drawing is complete)

The final illustration is saved to:
    output/dandiya_pencil_sketch.png
"""

import os
import sys


def main():
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="Save the completed drawing without opening a window")
    parser.add_argument("--output", default="output/dandiya_pencil_sketch.png")
    args = parser.parse_args()

    print("=" * 62)
    print("  Indian Couple Dandiya — Pencil Sketch Animation")
    print("=" * 62)
    print("  Initialising drawing engine…")

    from drawing_engine import DrawingEngine
    from stroke_scene import build_scene

    engine = DrawingEngine(canvas_w=1248, canvas_h=1248, fps=60)

    print("  Composing stroke queue…", end=" ", flush=True)
    build_scene(engine)
    engine.output_path = args.output
    if args.render:
        import pygame
        engine._canvas = pygame.Surface((1248 * engine.RENDER_SCALE, 1248 * engine.RENDER_SCALE))
        engine._canvas.fill(engine.PAPER_BG)
        engine._speed_mul = 100000
        engine._prepare_next_stroke()
        while not engine._done:
            engine._advance(16)
        return
    total = len(engine._strokes)
    print(f"OK — {total} strokes queued across {len(set(s['stage'] for s in engine._strokes))} stages.")
    print()
    print("  Controls: Space=Pause  ↑↓=Speed  R=Restart  S=Save  Esc=Quit")
    print("  Starting Pygame window…")
    print()

    engine.run(title="Indian Couple Dandiya — Pencil Sketch Drawing")

    print("Done.")


if __name__ == "__main__":
    main()
