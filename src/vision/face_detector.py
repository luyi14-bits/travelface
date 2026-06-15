import numpy as np


class FaceDetector:
    """纯 numpy 人脸定位器 - 宽松肤色检测 + 位置/尺寸约束"""

    def __init__(self, min_confidence: float = 0.5):
        self._min_confidence = min_confidence

    def detect(self, image: np.ndarray) -> list[dict]:
        h, w = image.shape[:2]
        skin_mask = self._skin_mask(image)

        skin_ratio = np.sum(skin_mask) / (h * w)
        if skin_ratio < 0.012:
            return self._center_guess(image, w, h)

        regions = self._find_regions(skin_mask)
        faces = self._filter_best_face(regions, w, h, image)
        return faces

    # ── 肤色掩膜 ──────────────────────────────────

    def _skin_mask(self, image: np.ndarray) -> np.ndarray:
        """宽松版 YCbCr —— 只用经典学术范围，不加 RGB 限制"""
        img = image.astype(np.float32)
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]

        cb = 128.0 - 0.168736 * r - 0.331264 * g + 0.5 * b
        cr = 128.0 + 0.5 * r - 0.418688 * g - 0.081312 * b

        return (cb >= 77) & (cb <= 127) & (cr >= 133) & (cr <= 173)

    # ── 连通域 ────────────────────────────────────

    def _find_regions(self, mask: np.ndarray) -> list[dict]:
        h, w = mask.shape
        visited = np.zeros((h, w), dtype=bool)
        regions = []

        for y in range(0, h, 2):
            for x in range(0, w, 2):
                if mask[y, x] and not visited[y, x]:
                    region = self._flood_fill(mask, visited, x, y)
                    if region and region["pixels"] >= 60:
                        regions.append(region)
        return regions

    def _flood_fill(self, mask: np.ndarray, visited: np.ndarray,
                    start_x: int, start_y: int) -> dict | None:
        h, w = mask.shape
        stack = [(start_x, start_y)]
        visited[start_y, start_x] = True
        min_x = max_x = start_x
        min_y = max_y = start_y

        while stack:
            x, y = stack.pop()
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)
            for nx, ny in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
                if 0 <= nx < w and 0 <= ny < h:
                    if mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((nx, ny))

        bw, bh = max_x - min_x + 1, max_y - min_y + 1
        pixel_count = int(np.sum(mask[min_y:max_y + 1, min_x:max_x + 1]))
        fill_ratio = pixel_count / (bw * bh) if bw * bh > 0 else 0

        return {
            "x": min_x, "y": min_y, "w": bw, "h": bh,
            "area": bw * bh, "pixels": pixel_count,
            "fill_ratio": fill_ratio,
        }

    # ── 只取最优一个 ──────────────────────────────

    def _filter_best_face(self, regions: list[dict], img_w: int, img_h: int,
                          image: np.ndarray) -> list[dict]:
        img_area = img_w * img_h
        best_score = -999.0
        best_region = None

        for r in regions:
            aspect = r["w"] / max(r["h"], 1)

            # 尺寸：占图片 0.8% ~ 35%
            if r["area"] < img_area * 0.008 or r["area"] > img_area * 0.35:
                continue

            # 最少 200 个肤色像素
            if r["pixels"] < 200:
                continue

            # 纵横比 0.6~1.7
            if aspect < 0.6 or aspect > 1.7:
                continue

            # 填充率 >= 35%
            if r["fill_ratio"] < 0.35:
                continue

            # 位置：人脸中心在画面上 5%~60% 高度
            cy_norm = (r["y"] + r["h"] / 2) / img_h
            cx_norm = (r["x"] + r["w"] / 2) / img_w

            if cy_norm < 0.05 or cy_norm > 0.60:
                continue

            pos_x = 1.0 - abs(cx_norm - 0.5) * 2.0
            pos_y = 1.0 - abs(cy_norm - 0.33) * 2.5
            pos_score = max(0.0, pos_x * 0.5 + pos_y * 0.5)

            size_score = min(1.0, r["pixels"] / max(img_area * 0.015, 1))
            score = r["fill_ratio"] * 0.50 + pos_score * 0.30 + size_score * 0.20

            if score > best_score:
                best_score = score
                best_region = r

        if best_region is None or best_score < 0.42:
            return self._center_guess(image, img_w, img_h)

        rec = best_region
        pad_x = int(rec["w"] * 0.12)
        pad_y = int(rec["h"] * 0.12)
        x1 = max(0, rec["x"] - pad_x)
        y1 = max(0, rec["y"] - pad_y)
        x2 = min(img_w, rec["x"] + rec["w"] + pad_x)
        y2 = min(img_h, rec["y"] + rec["h"] + pad_y)
        crop = image[y1:y2, x1:x2]

        return [{"box": (x1, y1, x2 - x1, y2 - y1), "crop": crop, "detector": "skin_color"}]

    def _center_guess(self, image: np.ndarray, img_w: int, img_h: int) -> list[dict]:
        face_w = int(img_w * 0.30)
        face_h = int(img_h * 0.35)
        cx, cy = img_w // 2, int(img_h * 0.32)
        x1 = max(0, cx - face_w // 2)
        y1 = max(0, cy - face_h // 2)
        x2 = min(img_w, x1 + face_w)
        y2 = min(img_h, y1 + face_h)
        crop = image[y1:y2, x1:x2]
        return [{"box": (x1, y1, x2 - x1, y2 - y1), "crop": crop, "detector": "center_guess"}]
