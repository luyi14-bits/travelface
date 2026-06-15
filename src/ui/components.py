import streamlit as st
import textwrap
from PIL import Image

from utils.helpers import cv2_to_pil, draw_face_boxes


def inject_custom_css() -> None:
    st.markdown(
        textwrap.dedent("""\
        <style>
        /* ===== 暗色模式全局背景 ===== */
        .stApp {
            background: linear-gradient(135deg, #0b0b2a 0%, #1a1a4e 30%, #16213e 60%, #0f3460 100%);
        }

        /* ===== 暗色模式文字 ===== */
        .stMarkdown, .stCaption { color: #e0e0ff; }
        h1, h2 { color: #fff !important; }

        /* ===== 暗色模式标题装饰 ===== */
        h1 { text-align: center; font-weight: 800; }
        h2 { border-left: 4px solid #7b2ff7; padding-left: 12px; }

        /* ===== 暗色模式按钮 ===== */
        .stButton button {
            background: linear-gradient(135deg, #7b2ff7, #00d2ff);
            color: white; border: none;
            border-radius: 10px; font-weight: 700;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .stButton button:hover {
            transform: scale(1.04);
            box-shadow: 0 4px 20px rgba(123, 47, 247, 0.45);
        }

        /* ===== 暗色模式 Metric 卡片 ===== */
        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 14px; padding: 12px 16px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(123, 47, 247, 0.25);
        }
        [data-testid="stMetric"] label { color: #a0a0d0 !important; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; }

        /* ===== 暗色模式 face-detail-card ===== */
        .face-detail-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px; padding: 14px; margin-bottom: 10px;
            color: #e0e0ff;
        }
        .face-detail-card .fd-label { color: #c0c0ff; }
        .face-detail-card .fd-emotion { color: #00d2ff; }
        .face-detail-card .fd-conf { color: #a0a0d0; }
        .face-detail-card .fd-title { color: #fff; }

        /* ===== 旅行卡片 ===== */
        .travel-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 18px; overflow: hidden; margin: 20px 0;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .travel-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.30);
        }
        .travel-card-body { padding: 20px; }
        .travel-card-title {
            font-size: 1.3rem; font-weight: 700;
            color: #fff; margin-bottom: 12px;
        }
        .travel-card-meta {
            display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 12px;
        }
        .travel-card-meta span {
            background: rgba(123,47,247,0.2); color: #c0c0ff;
            padding: 4px 12px; border-radius: 18px; font-size: 13px;
        }
        .travel-card-reason {
            color: #a0a0d0; font-style: italic;
            border-left: 3px solid #7b2ff7; padding-left: 14px; margin-bottom: 14px;
        }
        .travel-card-tags {
            display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px;
        }
        .travel-card-tag {
            background: linear-gradient(135deg, rgba(0,210,255,0.15), rgba(123,47,247,0.15));
            color: #90d0ff; padding: 4px 12px; border-radius: 12px; font-size: 12px;
        }
        .card-cover {
            height: 180px; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            position: relative; overflow: hidden;
        }
        .card-cover-icon { font-size: 3.5rem; }
        .card-cover-dest {
            font-size: 1.4rem; font-weight: 800;
            color: rgba(255,255,255,0.95); letter-spacing: 3px; margin-top: 8px;
        }
        .itinerary-days { display: flex; gap: 10px; margin-top: 14px; flex-wrap: wrap; }
        .itinerary-day {
            flex: 1; min-width: 180px;
            background: rgba(255,255,255,0.04);
            border-radius: 10px; padding: 14px;
            border: 1px solid rgba(255,255,255,0.06);
        }
        .itinerary-day strong { color: #7b2ff7; display: block; margin-bottom: 8px; }
        .itinerary-spot { color: #d0d0f0; font-size: 13px; padding: 2px 0; }
        .itinerary-food {
            color: #ff9f43; font-size: 12px;
            margin-top: 8px; padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.06);
        }

        /* ======================================== */
        /* ===== LIGHT MODE 覆盖 ===== */
        /* ======================================== */
        [data-theme="light"] .stApp {
            background: linear-gradient(135deg, #e8ecf8 0%, #dce4f5 30%, #eaf0fa 60%, #f0f4ff 100%);
        }
        [data-theme="light"] .stMarkdown,
        [data-theme="light"] .stCaption { color: #2a2a4e !important; }
        [data-theme="light"] h1,
        [data-theme="light"] h2 { color: #1a1a2e !important; }
        [data-theme="light"] h2 { border-left-color: #5a1fd7; }

        [data-theme="light"] .stButton button {
            background: linear-gradient(135deg, #6a1fe7, #0098cc);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        [data-theme="light"] .stButton button:hover {
            transform: scale(1.04);
            box-shadow: 0 4px 18px rgba(106, 31, 231, 0.35);
        }

        [data-theme="light"] [data-testid="stMetric"] {
            background: rgba(0,0,0,0.04) !important;
            border: 1px solid rgba(0,0,0,0.08) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        [data-theme="light"] [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        }
        [data-theme="light"] [data-testid="stMetric"] label { color: #555 !important; }
        [data-theme="light"] [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #1a1a2e !important; }

        [data-theme="light"] .face-detail-card {
            background: rgba(0,0,0,0.04);
            border: 1px solid rgba(0,0,0,0.08);
            color: #2a2a4e;
        }
        [data-theme="light"] .face-detail-card .fd-label { color: #444; }
        [data-theme="light"] .face-detail-card .fd-emotion { color: #0077b6; }
        [data-theme="light"] .face-detail-card .fd-conf { color: #666; }
        [data-theme="light"] .face-detail-card .fd-title { color: #1a1a2e; }

        [data-theme="light"] .travel-card {
            background: rgba(0,0,0,0.03);
            border: 1px solid rgba(0,0,0,0.08);
        }
        [data-theme="light"] .travel-card-title { color: #1a1a2e; }
        [data-theme="light"] .travel-card-meta span {
            background: rgba(100,40,220,0.1); color: #4a2a8e;
        }
        [data-theme="light"] .travel-card-reason { color: #555; border-left-color: #6a1fe7; }
        [data-theme="light"] .travel-card-tag {
            background: rgba(0,130,200,0.1);
            color: #006494;
        }
        [data-theme="light"] .itinerary-day {
            background: rgba(0,0,0,0.03);
            border: 1px solid rgba(0,0,0,0.06);
        }
        [data-theme="light"] .itinerary-day strong { color: #5a1fd7; }
        [data-theme="light"] .itinerary-spot { color: #444; }
        [data-theme="light"] .itinerary-food {
            color: #c76b00;
            border-top: 1px solid rgba(0,0,0,0.06);
        }
        </style>
        """),
        unsafe_allow_html=True,
    )


def render_analysis_summary(vision_result: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 人数", vision_result.get("face_count", 0))
    col2.metric("🏷️ 类型", vision_result.get("crowd_type", "-"))

    tags = vision_result.get("tags", {})
    emotions = tags.get("emotions", ["-"])
    age_groups = tags.get("age_groups", ["-"])

    col3.metric("😊 情绪", emotions[0] if len(emotions) == 1 else "多样")
    col4.metric("🎂 年龄段", age_groups[0] if len(age_groups) == 1 else "多样")


def render_annotated_image(image_np, faces: list, caption: str = "人脸检测结果") -> None:
    annotated = draw_face_boxes(image_np, faces)
    pil_image = cv2_to_pil(annotated)
    st.image(pil_image, caption=caption, width="stretch")


def _get_travel_card_cover(destination: str, index: int) -> str:
    icons = ["🏔️", "🏖️", "🏯"]
    icon = icons[index % len(icons)]
    colors = [
        ("#1a1a4e", "#7b2ff7"),
        ("#16213e", "#e94560"),
        ("#0f3460", "#00d2ff"),
    ]
    c1, c2 = colors[index % len(colors)]
    return f'<div class="card-cover" style="background:linear-gradient(135deg,{c1} 0%,{c2} 100%);"><div class="card-cover-icon">{icon}</div><div class="card-cover-dest">{destination}</div></div>'


def render_travel_card(route: dict, index: int) -> None:
    destination = route.get("destination", "")
    cover_html = _get_travel_card_cover(destination, index)

    emojis = ["🥇", "🥈", "🥉"]
    medal = emojis[index] if index < len(emojis) else "📍"

    meta_items = [
        f"<span>📍 {destination}</span>",
        f"<span>⏱️ {route.get('duration', '')}</span>",
        f"<span>💰 {route.get('budget', '')}</span>",
    ]

    tags_html = "".join(
        f'<span class="travel-card-tag">{t}</span>'
        for t in route.get("tags", [])
    )

    itinerary = route.get("itinerary", [])
    days_html = ""
    if itinerary:
        days_parts = []
        for day in itinerary:
            spots = "".join(
                f'<div class="itinerary-spot">▸ {s}</div>'
                for s in day.get("spots", [])
            )
            food_block = ""
            if day.get("food"):
                food_block = (
                    f'<div class="itinerary-food">{" · ".join(day["food"])}</div>'
                )
            days_parts.append(
                f'<div class="itinerary-day"><strong>{day.get("label", "")}</strong>{spots}{food_block}</div>'
            )
        days_html = f'<div class="itinerary-days">{"".join(days_parts)}</div>'

    html = f"""
    <div class="travel-card">
        {cover_html}
        <div class="travel-card-body">
            <div class="travel-card-title">{medal} {route.get('title', '路线')}</div>
            <div class="travel-card-meta">{"".join(meta_items)}</div>
            <div class="travel-card-reason">💡 {route.get('reason', '')}</div>
            <div class="travel-card-tags">{tags_html}</div>
            {days_html}
        </div>
    </div>
    """

    st.html(html)


def render_travel_cards(routes: list) -> None:
    st.markdown("## 🛫 个性化旅游推荐")
    st.caption("基于您的画像与情绪，为您精选以下路线 👇")

    for idx, route in enumerate(routes):
        render_travel_card(route, idx)
