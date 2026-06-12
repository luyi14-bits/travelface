import os
from pathlib import Path

import numpy as np
from deepface import DeepFace


_WEIGHTS_DIR = Path.home() / ".deepface" / "weights"


def _weights_exist(*filenames: str) -> bool:
    return all((_WEIGHTS_DIR / f).is_file() for f in filenames)


class UserProfiler:
    def __init__(self):
        self._backends = ["opencv", "ssd", "mtcnn", "retinaface"]
        self._available = _weights_exist("age_model_weights.h5", "gender_model_weights.h5")

    def analyze(self, face_crop: np.ndarray) -> dict:
        if not self._available:
            return {"age_group": "青年", "gender": "未知", "confidence": 0.0}

        for backend in self._backends:
            try:
                result = DeepFace.analyze(
                    img_path=face_crop,
                    actions=["age", "gender"],
                    detector_backend=backend,
                    enforce_detection=False,
                    silent=True,
                )
                if isinstance(result, list):
                    result = result[0]
                return self._parse(result)
            except Exception:
                continue

        return {"age_group": "青年", "gender": "未知", "confidence": 0.0}

    @staticmethod
    def _parse(result: dict) -> dict:
        age = int(float(result.get("age", 25)))
        gender_raw = result.get("dominant_gender", "未知")
        region = result.get("region", {})
        gender_label = str(gender_raw).capitalize()
        return {
            "age_group": _estimate_age_group(age),
            "gender": gender_label,
            "confidence": float(region.get(gender_raw, 0.0)),
        }


def _estimate_age_group(age: int) -> str:
    if age < 18:
        return "少年"
    if age < 30:
        return "青年"
    if age < 45:
        return "中年"
    return "中老年"
