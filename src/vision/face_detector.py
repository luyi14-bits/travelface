import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision


_MODEL_PATH = None


def _get_model_path() -> str:
    global _MODEL_PATH
    if _MODEL_PATH is None:
        from pathlib import Path
        candidates = [
            Path("assets/blaze_face_short_range.tflite"),
            Path(__file__).resolve().parents[2] / "assets" / "blaze_face_short_range.tflite",
        ]
        for p in candidates:
            if p.is_file():
                _MODEL_PATH = str(p.resolve())
                break
        if _MODEL_PATH is None:
            raise FileNotFoundError(
                "找不到 BlazeFace 模型文件，请将 blaze_face_short_range.tflite 放到 assets/ 目录"
            )
    return _MODEL_PATH


class FaceDetector:
    def __init__(self, min_confidence: float = 0.5):
        self._min_confidence = min_confidence

    def detect(self, image: np.ndarray) -> list[dict]:
        h, w = image.shape[:2]
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        base_options = mp_python.BaseOptions(model_asset_path=_get_model_path())
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=self._min_confidence,
        )

        results: list[dict] = []
        with vision.FaceDetector.create_from_options(options) as detector:
            detections = detector.detect(mp_image)

        if not detections:
            return results

        for detection in detections.detections:
            bbox = detection.bounding_box
            x1, y1 = max(0, bbox.origin_x), max(0, bbox.origin_y)
            bw, bh = bbox.width, bbox.height

            pad_x = int(bw * 0.1)
            pad_y = int(bh * 0.1)

            x1 = max(0, x1 - pad_x)
            y1 = max(0, y1 - pad_y)
            x2 = min(w, x1 + bw + pad_x * 2)
            y2 = min(h, y1 + bh + pad_y * 2)

            crop = image[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            results.append({
                "box": (x1, y1, x2 - x1, y2 - y1),
                "crop": crop,
                "detector": "mediapipe",
            })

        return results
