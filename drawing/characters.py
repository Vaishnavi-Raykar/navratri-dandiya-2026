"""
Characters coordinator module for Indian Couple Dandiya Illustration.

Orchestrates the layered programmatic drawing of both characters:
- Male Character (left side): Kurta-pajama, wavy tousled hair, handsome anime face,
  two dandiya sticks in active dance pose with lifted leg.
- Female Character (right side): Swirling flared lehenga-choli, long cascading hair
  with flower, elegant anime face, jhumka, bangles, and two dandiya sticks.
- Scene accents: motion action dashes, ground shadows, balanced whitespace.
"""

from .canvas import DrawingCanvas
from .faces import draw_male_face, draw_female_face
from .hair import draw_male_hair, draw_female_hair
from .clothing import draw_kurta, draw_pajama, draw_lehenga, draw_dupatta, draw_choli
from .accessories import (
    draw_dandiya_stick,
    draw_hand_and_fingers,
    draw_jewellery,
    draw_ground_shadows,
    draw_motion_marks,
)


def draw_male_character(canvas: DrawingCanvas):
    """
    Renders the complete male character on the left side of the canvas.
    """
    # 1. Traditional Kurta-Pajama and Mojari Shoes
    draw_kurta(canvas)
    draw_pajama(canvas)

    # 2. Arms and Hands
    draw_hand_and_fingers(canvas, hand_id=1)
    draw_hand_and_fingers(canvas, hand_id=2)

    # 3. Two Dandiya Sticks (Raised stick and forward stick)
    draw_dandiya_stick(canvas, stick_id=1)
    draw_dandiya_stick(canvas, stick_id=2)

    # 4. Voluminous tousled black hair
    draw_male_hair(canvas)

    # 5. Handsome anime facial features, smile, and neck
    draw_male_face(canvas)


def draw_female_character(canvas: DrawingCanvas):
    """
    Renders the complete female character on the right side of the canvas.
    """
    # 1. Festive Lehenga-Choli and Sheer Cascading Dupatta
    draw_choli(canvas)
    draw_lehenga(canvas)
    draw_dupatta(canvas)

    # 2. Arms, Hands, and Traditional Bangles
    draw_hand_and_fingers(canvas, hand_id=3)
    draw_hand_and_fingers(canvas, hand_id=4)
    draw_jewellery(canvas)

    # 3. Two Dandiya Sticks (Raised stick and lower stick)
    draw_dandiya_stick(canvas, stick_id=3)
    draw_dandiya_stick(canvas, stick_id=4)

    # 4. Long cascading wavy hair with tucked white flower
    draw_female_hair(canvas)

    # 5. Elegant anime facial features, joyful open smile, and Jhumka earring
    draw_female_face(canvas)


def draw_couple(canvas: DrawingCanvas):
    """
    Renders the complete dandiya dancing couple with background paper finishing,
    motion action dashes, and ground shadows.
    """
    # 1. Draw Male Character (Left side, ~40% canvas)
    draw_male_character(canvas)

    # 2. Draw Female Character (Right side, ~48% canvas)
    draw_female_character(canvas)

    # 3. Action marks and rhythm sparks around dandiya sticks
    draw_motion_marks(canvas)

    # 4. Ground shadows beneath both dancing characters' feet
    draw_ground_shadows(canvas)
