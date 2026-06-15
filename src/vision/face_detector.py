import numpy as np


class FaceDetector:
    """纯 numpy 肤色检测人脸定位器 - 多重校验防误检"""

    def __init__(self, min_confidence: float = 0.5):
        self._min_confidence = min_confidence

    def detect(self, image: np.ndarray) -> list[dict]:
        h, w = image.shape[:2]
        skin_mask = self._skin_mask(image)

        skin_ratio = np.sum(skin_mask) / (h * w)
        if skin_ratio < 0.015:
            return self._center_guess(image, w, h)

        regions = self._find_regions(skin_mask)
        faces = self._filter_face_regions(regions, w, h, image, skin_mask)
        return faces

    # ── 肤色掩膜 ──────────────────────────────────

    def _skin_mask(self, image: np.ndarray) -> np.ndarray:
        """收紧版 YCbCr 肤色检测 + RGB 双重校验"""
        img = image.astype(np.float32)
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]

        # YCbCr 肤色（学术公认范围，略微收紧）
        cb = 128.0 - 0.168736 * r - 0.331264 * g + 0.5 * b
        cr = 128.0 + 0.5 * r - 0.418688 * g - 0.081312 * b
        skin_ycbcr = (
            (cb >= 80) & (cb <= 125) &
            (cr >= 136) & (cr <= 170)
        )

        # RGB 肤色约束：R > 95, G > 40, B > 20, max(R,G,B)-min(R,G,B) > 15, |R-G|>15, R>G, R>B
        rgb_valid = (
            (r > 95) & (g > 40) & (b > 20) &
            (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b) > 15) &
            (np.abs(r - g) > 15) &
            (r > g) & (r > b)
        )

        return skin_ycbcr & rgb_valid

    # ── 连通域 ────────────────────────────────────

    def _find_regions(self, mask: np.ndarray) -> list[dict]:
        h, w = mask.shape
        visited = np.zeros((h, w), dtype=bool)
        regions = []

        for y in range(0, h, 2):
            for x in range(0, w, 2):
                if mask[y, x] and not visited[y, x]:
                    region = self._flood_fill(mask, visited, x, y)
                    if region and region["pixels"] >= 80:
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

    # ── 多重校验筛选 ──────────────────────────────

    def _filter_face_regions(self, regions: list[dict], img_w: int, img_h: int,
                             image: np.ndarray, skin_mask: np.ndarray) -> list[dict]:
        img_area = img_w * img_h

        scored = []
        for r in regions:
            aspect = r["w"] / max(r["h"], 1)

            # 1. 尺寸过滤：人脸在照片中通常占 1%~30%
            if r["area"] < img_area * 0.008 or r["area"] > img_area * 0.35:
                continue

            # 2. 像素数下限
            if r["pixels"] < 300:
                continue

            # 3. 纵横比：人脸接近 1:1（0.65 ~ 1.6）
            if aspect < 0.65 or aspect > 1.6:
                continue

            # 4. 填充率：人脸区域内肤色应占 42% 以上
            if r["fill_ratio"] < 0.42:
                continue

            # 5. 纹理：人脸区域不该是均匀的墙壁
            crop = image[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"]]
            gray = np.mean(crop, axis=2) if len(crop.shape) == 3 else crop
            texture = float(np.std(gray))
            if texture < 15:
                continue

            # 6. 位置偏好加分（人脸通常在画面中上部）
            center_x = r["x"] + r["w"] / 2
            center_y = r["y"] + r["h"] / 2
            pos_score = 1.0 - abs(center_x / img_w - 0.5) - 0.3 * max(0, center_y / img_h - 0.55)

            # 综合打分：填充率高 + 位置好 + 面积适中
            score = r["fill_ratio"] * 0.4 + pos_score * 0.3 + (r["pixels"] / img_area) * 100 * 0.3
            scored.append((score, r))

        if not scored:
            return self._center_guess(image, img_w, img_h)

        scored.sort(key=lambda x: x[0], reverse=True)

        filtered = []
        for score, rec in scored:
            if score < 0.55:
                continue
            if filtered and score < filtered[-1][0] * 0.55:
                continue
            filtered.append((score, rec))
            if len(filtered) >= 5:
                break

        if not filtered:
            return self._center_guess(image, img_w, img_h)

        results = []
        for _, rec in filtered:
            pad_x = int(rec["w"] * 0.12)
            pad_y = int(rec["h"] * 0.12)
            x1 = max(0, rec["x"] - pad_x)
            y1 = max(0, rec["y"] - pad_y)
            x2 = min(img_w, rec["x"] + rec["w"] + pad_x)
            y2 = min(img_h, rec["y"] + rec["h"] + pad_y)

            crop = image[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            results.append({
                "box": (x1, y1, x2 - x1, y2 - y1),
                "crop": crop,
                "detector": "skin_color",
            })

        return results or self._center_guess(image, img_w, img_h)

    # ── 降级兜底 ──────────────────────────────────

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
