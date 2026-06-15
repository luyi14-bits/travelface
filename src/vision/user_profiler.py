import numpy as np


class UserProfiler:
    """轻量级用户画像分析器 - 不依赖 DeepFace/TensorFlow"""

    def __init__(self, prewarm: bool = False):
        """初始化分析器"""
        pass

    def analyze(self, face_crop: np.ndarray) -> dict:
        """基于图像特征分析年龄和性别"""
        try:
            return self._analyze_features(face_crop)
        except Exception:
            return {"age_group": "青年", "gender": "未知", "confidence": 0.5}

    def _analyze_features(self, face_crop: np.ndarray) -> dict:
        """基于图像特征进行简单分析"""
        # 获取图像统计特征
        if len(face_crop.shape) == 3:
            gray = np.mean(face_crop, axis=2)
        else:
            gray = face_crop

        # 基于亮度估计年龄（简化版）
        brightness = np.mean(gray)
        if brightness < 100:
            age_group = "中老年"
        elif brightness > 180:
            age_group = "少年"
        else:
            age_group = "青年"

        # 基于色彩偏红程度估计性别
        if len(face_crop.shape) == 3:
            r_mean = np.mean(face_crop[:, :, 0])
            g_mean = np.mean(face_crop[:, :, 1])
            b_mean = np.mean(face_crop[:, :, 2])

            # 皮肤红润程度
            red_ratio = r_mean / (g_mean + b_mean + 1)
            if red_ratio > 1.1:
                gender = "Female"
                confidence = min(red_ratio * 0.5, 0.8)
            else:
                gender = "Male"
                confidence = min((2 - red_ratio) * 0.5, 0.8)
        else:
            gender = "未知"
            confidence = 0.5

        return {
            "age_group": age_group,
            "gender": gender,
            "confidence": confidence,
        }


def _estimate_age_group(age: int) -> str:
    if age < 18:
        return "少年"
    if age < 30:
        return "青年"
    if age < 45:
        return "中年"
    return "中老年"
