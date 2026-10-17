# Indian Couple Dandiya — Pure Line Art & Real-Time Sketch Animation

A Python-based vector illustration and real-time stroke animation engine drawing a high-contrast anime line art illustration of a young Indian couple performing Dandiya Raas for Navratri.

## ✨ Highlights

1. **Strictly High-Contrast Pure Line Art**: Clean black ink outlines on crisp paper background with zero clothing shading.
2. **Solid Dark Black Filled-In Hair**: Velvety, solid jet-black hair with natural wavy curls and locks drawn with accelerated nested curves.
3. **Selective Pops of Vibrant Color**:
   - Bright red bindi on the woman's forehead (`#E4141E`).
   - Solid dark red flower in her hair (`#8C0E12`, zero white gaps).
   - Golden yellow (`#F8CA14`) and festive red (`#DE1A24`) spiral stripes on Dandiya sticks end-to-end.
4. **Pure Uncolored Hands (Zero Color Bleed)**: Hands holding sticks remain pure white skin with crisp black contours.
5. **Real-Time Pygame Pencil Animator**: Watch the illustration get drawn stroke-by-stroke in real time with an artist pencil cursor that smoothly tracks active stroke tips.
6. **No External Assets Required**: All vector curves, contours, and eye coordinates are bundled locally in the repository.

---

## 📁 Repository Structure

```text
├── main.py                     # Entry point for real-time Pygame animation & rendering
├── drawing_engine.py           # Pygame animation engine with pencil cursor & HUD
├── stroke_scene.py             # Stroke queue composer and coordinate transformer
├── drawing/
│   ├── vector_data.py          # Extracted vector paths, solid hair fills, and selective color data
│   ├── reference_contours.json # Connected vector curves for heads, expressions, and hair
│   ├── reference_eyes.json     # Reference eye points and catchlight geometry
│   ├── eyes.py                 # Clean eye coordinates and pupil/lid helpers
│   ├── canvas.py               # Canvas utilities
│   ├── characters.py           # Character composition coordinator
│   ├── faces.py                # Facial feature helpers
│   ├── hair.py                 # Hair procedural curves
│   ├── clothing.py             # Clothing paths
│   ├── accessories.py          # Dandiya sticks & hand geometry
│   ├── pencil_effects.py       # Organic spline strokes & paper texture
│   └── __init__.py             # Module exports
├── output/
│   └── dandiya_pencil_sketch.png # High-contrast 1248x1248 completed artwork preview
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # Documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `pip` package manager

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/navratri-garba-connected-lines.git
cd navratri-garba-connected-lines
pip install -r requirements.txt
```

---

## 🎮 Running the Animation

### 1. Watch Real-Time Pencil Drawing

Launch the live animated drawing in an interactive window:

```bash
python main.py
```

#### Controls (while window is open):
| Key | Action |
|---|---|
| `Space` | Pause / Resume animation |
| `↑` / `↓` | Increase / Decrease drawing speed (0.25× up to 32×) |
| `R` | Restart animation from blank canvas |
| `S` | Save current canvas immediately |
| `Esc` | Exit window (auto-saves if drawing is complete) |

---

### 2. Fast Export Without Animation Window

Save the completed high-resolution illustration immediately:

```bash
python main.py --render --output output/dandiya_pencil_sketch.png
```

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
