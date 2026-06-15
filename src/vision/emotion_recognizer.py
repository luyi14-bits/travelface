import numpy as np


class EmotionRecognizer:
    """轻量级情绪识别器 - 不依赖 DeepFace/TensorFlow"""

    _EMOTION_MAP = {
        "angry": "愤怒",
        "disgust": "厌恶",
        "fear": "恐惧",
        "happy": "开心",
        "sad": "悲伤",
        "surprise": "惊讶",
        "neutral": "中性",
    }

    def __init__(self, prewarm: bool = False):
        self._emotions = list(self._EMOTION_MAP.keys())
        self._available = self._check_dependencies()

    def _check_dependencies(self) -> bool:
        """检查 DeepFace 是否可用"""
        try:
            from deepface import DeepFace
            return True
        except ImportError:
            return False

    def recognize(self, face_crop: np.ndarray) -> dict:
        """识别情绪"""
        if self._available:
            return self._recognize_deepface(face_crop)
        else:
            return self._recognize_fallback(face_crop)

    def _recognize_deepface(self, face_crop: np.ndarray) -> dict:
        """使用 DeepFace 识别情绪"""
        from deepface import DeepFace
        try:
            result = DeepFace.analyze(
                img_path=face_crop,
                actions=["emotion"],
                detector_backend="opencv",
                enforce_detection=False,
                silent=True,
            )
            if isinstance(result, list):
                result = result[0]

            emotion_data = result.get("emotion", {})
            dominant = emotion_data.get("dominant_emotion", "neutral")
            chinese_label = self._EMOTION_MAP.get(dominant, dominant)

            confidence = float(emotion_data.get(dominant, 0.0))
            if confidence > 1.0:
                confidence /= 100.0

            return {
                "emotion": chinese_label,
                "emotion_en": dominant,
                "confidence": confidence,
                "scores": {
                    self._EMOTION_MAP.get(k, k): float(v) / 100.0 if float(v) > 1.0 else float(v)
                    for k, v in emotion_data.items()
                },
            }
        except Exception:
            return self._recognize_fallback(face_crop)

    def _recognize_fallback(self, face_crop: np.ndarray) -> dict:
        """基于图像特征的简单情绪识别（无 DeepFace 时使用）"""
        try:
            # 基于面部亮度和对比度的简单情绪判断
            gray = face_crop if len(face_crop.shape) == 2 else np.mean(face_crop, axis=2)
            brightness = np.mean(gray)
            contrast = np.std(gray)

            # 简单的启发式规则
            if brightness > 180 and contrast > 40:
                emotion = "happy"
                confidence = 0.6
            elif brightness < 120:
                emotion = "sad"
                confidence = 0.5
            elif contrast < 25:
                emotion = "neutral"
                confidence = 0.7
            else:
                emotion = "neutral"
                confidence = 0.5

            return {
                "emotion": self._EMOTION_MAP[emotion],
                "emotion_en": emotion,
                "confidence": confidence,
                "scores": {
                    self._EMOTION_MAP[e]: 0.14 for e in self._emotions
                },
            }
        except Exception:
            return {
                "emotion": "中性",
                "emotion_en": "neutral",
                "confidence": 0.5,
                "scores": {},
            }
