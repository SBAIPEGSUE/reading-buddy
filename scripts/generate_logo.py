"""
Generates the Reading Buddy logo and saves it to assets/logo.png.
Run once from the project root:  python scripts/generate_logo.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 820, 200
CREAM  = "#FDF6E3"
AMBER  = "#C4813A"
BROWN  = "#3D2B1F"


def make_logo(mascot_path: str, output_path: str):
    # Canvas with cream background (RGB — no transparency needed)
    canvas = Image.new("RGB", (WIDTH, HEIGHT), CREAM)

    # Load mascot and flatten transparency onto cream background
    mascot_raw = Image.open(mascot_path).convert("RGBA")
    bg = Image.new("RGBA", mascot_raw.size, (253, 246, 227, 255))
    mascot = Image.alpha_composite(bg, mascot_raw).convert("RGB")

    mascot_h = HEIGHT - 20
    ratio = mascot_h / mascot.height
    mascot_w = int(mascot.width * ratio)
    # Keep mascot to left third of canvas so text has room
    if mascot_w > WIDTH // 2:
        mascot_w = WIDTH // 2
        mascot_h = int(mascot.height * (mascot_w / mascot.width))
    mascot = mascot.resize((mascot_w, mascot_h), Image.LANCZOS)

    # Paste mascot onto canvas (centred vertically, left-aligned)
    paste_y = (HEIGHT - mascot_h) // 2
    canvas.paste(mascot, (10, paste_y))

    # Draw text to the right of the mascot
    draw = ImageDraw.Draw(canvas)
    text_x = mascot_w + 24

    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 52)
        font_sub   = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 20)
    except OSError:
        font_title = ImageFont.load_default()
        font_sub   = ImageFont.load_default()

    draw.text((text_x, 40),  "Reading Buddy",                    font=font_title, fill=BROWN)
    draw.text((text_x + 2, 106), "your spoiler-free reading companion", font=font_sub,  fill=AMBER)
    draw.line([text_x + 2, 134, WIDTH - 16, 134], fill=AMBER, width=2)

    canvas.save(output_path)
    print(f"Logo saved to {output_path}")


if __name__ == "__main__":
    make_logo("assets/mascot.png", "assets/logo.png")
