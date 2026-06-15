import numpy as np


class FaceDetector:
    """纯 numpy 肤色检测人脸定位器 - 零外部依赖"""

    def __init__(self, min_confidence: float = 0.5):
        self._min_confidence = min_confidence

    def detect(self, image: np.ndarray) -> list[dict]:
        h, w = image.shape[:2]
        skin_mask = self._skin_mask(image)

        skin_ratio = np.sum(skin_mask) / (h * w)
        if skin_ratio < 0.02:
            center_x, center_y = w // 2, h // 3
            face_w = int(w * 0.35)
            face_h = int(h * 0.40)
            x1 = max(0, center_x - face_w // 2)
            y1 = max(0, center_y - face_h // 2)
            x2 = min(w, x1 + face_w)
            y2 = min(h, y1 + face_h)
            crop = image[y1:y2, x1:x2]
            return [{
                "box": (x1, y1, x2 - x1, y2 - y1),
                "crop": crop,
                "detector": "center_guess",
            }]

        regions = self._find_regions(skin_mask)
        faces = self._filter_face_regions(regions, w, h, image)
        return faces

    def _skin_mask(self, image: np.ndarray) -> np.ndarray:
        """YCbCr 肤色检测"""
        img = image.astype(np.float32)

        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]

        cb = 128.0 - 0.168736 * r - 0.331264 * g + 0.5 * b
        cr = 128.0 + 0.5 * r - 0.418688 * g - 0.081312 * b

        skin = (cb >= 77) & (cb <= 127) & (cr >= 133) & (cr <= 173)
        return skin

    def _find_regions(self, mask: np.ndarray) -> list[dict]:
        """找到连通的肤色区域（简化版：按行扫描）"""
        h, w = mask.shape
        visited = np.zeros((h, w), dtype=bool)
        regions = []

        for y in range(h):
            for x in range(w):
                if mask[y, x] and not visited[y, x]:
                    region = self._flood_fill(mask, visited, x, y)
                    if region:
                        regions.append(region)
        return regions

    def _flood_fill(self, mask: np.ndarray, visited: np.ndarray,
                    start_x: int, start_y: int) -> dict | None:
        h, w = mask.shape
        stack = [(start_x, start_y)]
        visited[start_y, start_x] = True
        min_x, min_y = start_x, start_y
        max_x, max_y = start_x, start_y

        while stack:
            x, y = stack.pop()
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)
            for nx, ny in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
                if 0 <= nx < w and 0 <= ny < h:
                    if mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((nx, ny))

        area = (max_x - min_x + 1) * (max_y - min_y + 1)
        pixel_count = np.sum(mask[min_y:max_y + 1, min_x:max_x + 1])

        return {
            "x": min_x, "y": min_y,
            "w": max_x - min_x + 1, "h": max_y - min_y + 1,
            "area": area, "pixels": int(pixel_count),
        }

    def _filter_face_regions(self, regions: list[dict], img_w: int, img_h: int,
                             image: np.ndarray) -> list[dict]:
        """筛选并返回人脸区域"""
        img_area = img_w * img_h

        valid = [
            r for r in regions
            if r["pixels"] > 200
            and r["area"] > img_area * 0.005
            and r["area"] < img_area * 0.6
        ]

        if not valid:
            center_x, center_y = img_w // 2, img_h // 3
            face_w = int(img_w * 0.35)
            face_h = int(img_h * 0.40)
            x1 = max(0, center_x - face_w // 2)
            y1 = max(0, center_y - face_h // 2)
            x2 = min(img_w, x1 + face_w)
            y2 = min(img_h, y1 + face_h)
            crop = image[y1:y2, x1:x2]
            return [{
                "box": (x1, y1, x2 - x1, y2 - y1),
                "crop": crop,
                "detector": "center_guess",
            }]

        valid.sort(key=lambda r: r["area"], reverse=True)
        valid = valid[:5]

        results = []
        for r in valid:
            pad_x = int(r["w"] * 0.12)
            pad_y = int(r["h"] * 0.12)
            x1 = max(0, r["x"] - pad_x)
            y1 = max(0, r["y"] - pad_y)
            x2 = min(img_w, r["x"] + r["w"] + pad_x)
            y2 = min(img_h, r["y"] + r["h"] + pad_y)

            crop = image[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            results.append({
                "box": (x1, y1, x2 - x1, y2 - y1),
                "crop": crop,
                "detector": "skin_color",
            })

        return results
