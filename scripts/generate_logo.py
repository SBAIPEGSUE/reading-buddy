"""
Generates the Reading Buddy mascot image (otter only, no text) saved to assets/logo.png.
Run once from the project root:  python scripts/generate_logo.py
The app title is rendered by Streamlit using CSS fonts, not baked into this image.
"""

from PIL import Image
import os

BG = (247, 247, 247, 255)


def make_logo(mascot_path: str, output_path: str):
    mascot_raw = Image.open(mascot_path).convert("RGBA")

    # Flatten transparency onto sidebar background colour
    bg = Image.new("RGBA", mascot_raw.size, BG)
    mascot = Image.alpha_composite(bg, mascot_raw).convert("RGB")

    # Resize to a sensible sidebar width
    target_w = 260
    ratio = target_w / mascot.width
    target_h = int(mascot.height * ratio)
    mascot = mascot.resize((target_w, target_h), Image.LANCZOS)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    mascot.save(output_path)
    print(f"Logo saved to {output_path}")


if __name__ == "__main__":
    make_logo("assets/mascot.png", "assets/logo.png")
