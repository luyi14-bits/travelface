from typing import Optional

import numpy as np

from src.vision.emotion_recognizer import EmotionRecognizer
from src.vision.user_profiler import UserProfiler

_user_profiler: Optional[UserProfiler] = None
_emotion_recognizer: Optional[EmotionRecognizer] = None


def _get_profiler() -> UserProfiler:
    global _user_profiler
    if _user_profiler is None:
        _user_profiler = UserProfiler(prewarm=True)
    return _user_profiler


def _get_recognizer() -> EmotionRecognizer:
    global _emotion_recognizer
    if _emotion_recognizer is None:
        _emotion_recognizer = EmotionRecognizer(prewarm=True)
    return _emotion_recognizer


def analyze_image(image: np.ndarray) -> dict:
    h, w = image.shape[:2]

    face_data = {
        "box": (0, 0, w, h),
        "crop": image,
        "detector": "pillow",
    }
    faces = [face_data]

    profiler = _get_profiler()
    recognizer = _get_recognizer()

    face_results = []
    age_groups = []
    emotions = []
    genders = []

    for face_data in faces:
        crop = face_data["crop"]

        profile = profiler.analyze(crop)
        emotion = recognizer.recognize(crop)

        face_results.append({
            "box": face_data["box"],
            "profile": profile,
            "emotion": emotion,
        })

        age_groups.append(profile["age_group"])
        emotions.append(emotion["emotion"])
        genders.append(profile["gender"])

    crowd_type = _classify_crowd(len(faces), age_groups, genders)

    return {
        "face_count": len(faces),
        "faces": face_results,
        "crowd_type": crowd_type,
        "tags": {
            "age_groups": age_groups,
            "emotions": emotions,
            "genders": genders,
        },
        "summary": _build_summary(len(faces), age_groups, emotions, genders),
    }


def _classify_crowd(count: int, age_groups: list, genders: list) -> str:
    if count == 1:
        return "单人"
    if count == 2:
        return "双人"
    if count <= 5:
        return "小团体"
    return "多人合照"


def _build_summary(
    count: int,
    age_groups: list[str],
    emotions: list[str],
    genders: list[str],
) -> str:
    parts = [f"检测到 {count} 人"]
    if count == 1:
        parts.append(f"({genders[0]}, {age_groups[0]})")
        parts.append(f"，情绪：{emotions[0]}")
    else:
        male_count = sum(1 for g in genders if g == "Man")
        female_count = count - male_count
        if male_count and female_count:
            parts.append(f"(男{male_count}女{female_count})")
        elif male_count:
            parts.append("(全男)")
        else:
            parts.append("(全女)")

        top_emotion = max(set(emotions), key=emotions.count)
        parts.append(f"，主要情绪：{top_emotion}")

    return "".join(parts)
