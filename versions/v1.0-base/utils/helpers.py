import io
from typing import Optional

import cv2
import numpy as np
from PIL import Image


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)


def cv2_to_pil(image: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def draw_face_boxes(
    image: np.ndarray,
    faces: list[dict],
    color: tuple = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray:
    canvas = image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX

    for idx, face in enumerate(faces):
        x, y, w, h = face["box"]
        cv2.rectangle(canvas, (x, y), (x + w, y + h), color, thickness)

        profile = face.get("profile", {})
        emotion = face.get("emotion", {})

        label = f"#{idx + 1} {profile.get('age_group', '')} {profile.get('gender', '')}"
        emo = emotion.get("emotion", "")

        cv2.putText(canvas, label, (x, y - 10), font, 0.5, color, 1)

        cv2.putText(
            canvas, emo, (x, y + h + 18),
            font, 0.55, (255, 165, 0), 2,
        )

    return canvas


def image_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()


def read_uploaded_image(uploaded_file) -> Optional[np.ndarray]:
    if uploaded_file is None:
        return None
    raw = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    file_bytes = np.frombuffer(raw, np.uint8)
    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
