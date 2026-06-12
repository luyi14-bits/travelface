import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


class Config:
    ASSETS_DIR = BASE_DIR / "assets"

    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "doubao-1.5-pro-32k")

    DEEPFACE_DETECTOR = os.getenv("DEEPFACE_DETECTOR", "opencv")

    PAGE_TITLE = "TravelFace · 个性化旅游智能体"
    PAGE_ICON = "✈️"


config = Config()
