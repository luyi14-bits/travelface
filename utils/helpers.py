import io
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    return np.array(image.convert("RGB"))


def cv2_to_pil(image: np.ndarray) -> Image.Image:
    if image.dtype != np.uint8:
        image = (image * 255).astype(np.uint8)
    return Image.fromarray(image)


def draw_face_boxes(
    image: np.ndarray,
    faces: list[dict],
    color: tuple = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray:
    pil_img = cv2_to_pil(image)
    draw = ImageDraw.Draw(pil_img)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font = ImageFont.load_default()
        font_small = font

    for idx, face in enumerate(faces):
        x, y, w, h = face["box"]
        for t in range(thickness):
            draw.rectangle(
                [(x + t, y + t), (x + w - t - 1, y + h - t - 1)],
                outline=color,
            )

        profile = face.get("profile", {})
        emotion = face.get("emotion", {})

        label = f"#{idx + 1} {profile.get('age_group', '')} {profile.get('gender', '')}"
        emo = emotion.get("emotion", "")

        draw.text((x, y - 18), label, fill=color, font=font)
        draw.text((x, y + h + 4), emo, fill=(255, 165, 0), font=font_small)

    return np.array(pil_img)


def image_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()


def read_uploaded_image(uploaded_file) -> Optional[np.ndarray]:
    if uploaded_file is None:
        return None
    raw = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    pil_img = Image.open(io.BytesIO(raw)).convert("RGB")
    return np.array(pil_img)
