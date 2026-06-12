import os
from pathlib import Path

import numpy as np
from deepface import DeepFace


_WEIGHTS_DIR = Path.home() / ".deepface" / "weights"


def _weights_exist(*filenames: str) -> bool:
    return all((_WEIGHTS_DIR / f).is_file() for f in filenames)


class EmotionRecognizer:
    _EMOTION_MAP = {
        "angry": "愤怒",
        "disgust": "厌恶",
        "fear": "恐惧",
        "happy": "开心",
        "sad": "悲伤",
        "surprise": "惊讶",
        "neutral": "中性",
    }

    def __init__(self):
        self._backends = ["opencv", "ssd", "mtcnn", "retinaface"]
        self._available = _weights_exist("facial_expression_model_weights.h5")

    def recognize(self, face_crop: np.ndarray) -> dict:
        if not self._available:
            return {"emotion": "中性", "emotion_en": "neutral", "confidence": 0.0, "scores": {}}

        for backend in self._backends:
            try:
                result = DeepFace.analyze(
                    img_path=face_crop,
                    actions=["emotion"],
                    detector_backend=backend,
                    enforce_detection=False,
                    silent=True,
                )
                if isinstance(result, list):
                    result = result[0]

                emotion_data = result.get("emotion", {})
                dominant = emotion_data.get("dominant_emotion", "neutral")
                chinese_label = self._EMOTION_MAP.get(dominant, dominant)

                return {
                    "emotion": chinese_label,
                    "emotion_en": dominant,
                    "confidence": float(emotion_data.get(dominant, 0.0)),
                    "scores": {
                        self._EMOTION_MAP.get(k, k): float(v)
                        for k, v in emotion_data.items()
                    },
                }
            except Exception:
                continue

        return {"emotion": "中性", "emotion_en": "neutral", "confidence": 0.0, "scores": {}}
