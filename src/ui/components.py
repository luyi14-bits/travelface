import streamlit as st
import textwrap
from PIL import Image

from utils.helpers import cv2_to_pil, draw_face_boxes


def inject_custom_css() -> None:
    st.markdown(
        textwrap.dedent("""\
        <style>
        /* ===== 全局背景 ===== */
        .stApp {
            background: linear-gradient(135deg, #0b0b2a 0%, #1a1a4e 30%, #16213e 60%, #0f3460 100%);
            background-attachment: fixed;
        }

        /* ===== 全局文字高对比度 ===== */
        [data-testid="stMarkdownContainer"] {
            color: #e0e0ff;
        }
        [data-testid="stCaptionContainer"] {
            color: #a0a0d0;
        }
        /* 白色底组件保持深色文字 */
        [data-testid="stNotification"] {
            color: #1a1a2e !important;
        }
        [data-testid="stNotification"] p {
            color: #1a1a2e !important;
        }
        input, textarea, [data-baseweb="input"] {
            color: #e0e0ff !important;
        }
        textarea {
            background: rgba(255, 255, 255, 0.85) !important;
            border-color: rgba(123, 47, 247, 0.4) !important;
            color: #1a1a2e !important;
        }
        textarea::placeholder {
            color: #8888aa !important;
        }
        [data-baseweb="input"] input {
            color: #e0e0ff !important;
        }

        /* ===== 主内容区域玻璃拟态 ===== */
        .stMain, section[data-testid="stSidebar"] > div:first-child {
            background: transparent !important;
        }
        div[data-testid="stVerticalBlock"] > div[style*="flex"] {
            gap: 0.5rem;
        }

        /* ===== 标题光效 ===== */
        h1 {
            background: linear-gradient(90deg, #00d2ff, #7b2ff7, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            text-align: center;
            animation: titlePulse 3s ease-in-out infinite;
            filter: drop-shadow(0 0 20px rgba(0,210,255,0.3));
        }
        @keyframes titlePulse {
            0%, 100% { filter: drop-shadow(0 0 20px rgba(0,210,255,0.3)); }
            50% { filter: drop-shadow(0 0 40px rgba(123,47,247,0.5)); }
        }

        h2 {
            color: #e0e0ff !important;
            border-left: 4px solid #7b2ff7;
            padding-left: 16px;
        }

        h3 {
            color: #c0c0ff !important;
        }

        /* ===== 上传区域 ===== */
        section[data-testid="stFileUploader"] {
            background: rgba(255,255,255,0.05);
            border: 2px dashed rgba(123,47,247,0.4) !important;
            border-radius: 16px !important;
            transition: all 0.3s ease;
        }
        section[data-testid="stFileUploader"]:hover {
            border-color: rgba(123,47,247,0.8) !important;
            background: rgba(255,255,255,0.08);
        }

        /* ===== 按钮动效 ===== */
        .stButton > button {
            background: linear-gradient(135deg, #7b2ff7, #00d2ff) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 32px !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 20px rgba(123,47,247,0.3);
        }
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 40px rgba(123,47,247,0.5), 0 0 60px rgba(0,210,255,0.2) !important;
        }
        .stButton > button:active {
            transform: scale(0.98);
        }

        /* ===== 分析结果 Metric 卡片 ===== */
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 16px;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(123,47,247,0.2);
        }
        div[data-testid="stMetric"] label {
            color: #a0a0d0 !important;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 700 !important;
        }

        /* ===== 旅行卡片 ===== */
        .travel-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            overflow: hidden;
            margin: 24px 0;
            backdrop-filter: blur(12px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .travel-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(0,0,0,0.4), 0 0 40px rgba(123,47,247,0.15);
        }
        .travel-card-body {
            padding: 24px;
        }
        .travel-card-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 12px;
        }
        .travel-card-meta {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }
        .travel-card-meta span {
            background: rgba(123,47,247,0.2);
            color: #c0c0ff;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 13px;
            border: 1px solid rgba(123,47,247,0.3);
        }
        .travel-card-reason {
            color: #a0a0d0;
            font-style: italic;
            border-left: 3px solid #7b2ff7;
            padding-left: 16px;
            margin-bottom: 16px;
        }
        .travel-card-tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }
        .travel-card-tag {
            background: linear-gradient(135deg, rgba(0,210,255,0.15), rgba(123,47,247,0.15));
            color: #90d0ff;
            padding: 4px 14px;
            border-radius: 14px;
            font-size: 12px;
        }

        /* ===== 卡片封面 ===== */
        .card-cover {
            width: 100%;
            height: 220px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        .card-cover-icon {
            font-size: 4rem;
            filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));
            animation: iconFloat 3s ease-in-out infinite;
        }
        @keyframes iconFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        .card-cover-dest {
            font-size: 1.6rem;
            font-weight: 800;
            color: rgba(255,255,255,0.9);
            text-shadow: 0 2px 12px rgba(0,0,0,0.4);
            letter-spacing: 4px;
            margin-top: 8px;
        }
        .card-cover-shimmer {
            position: absolute;
            top: 0; left: -100%;
            width: 60%;
            height: 100%;
            background: linear-gradient(90deg,
                transparent 0%,
                rgba(255,255,255,0.05) 40%,
                rgba(255,255,255,0.12) 50%,
                rgba(255,255,255,0.05) 60%,
                transparent 100%
            );
            animation: shimmer 3s ease-in-out infinite;
        }
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 200%; }
        }

        /* ===== 行程日卡片 ===== */
        .itinerary-days {
            display: flex;
            gap: 12px;
            margin-top: 16px;
        }
        .itinerary-day {
            flex: 1;
            background: rgba(255,255,255,0.04);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid rgba(255,255,255,0.06);
        }
        .itinerary-day strong {
            color: #7b2ff7;
            display: block;
            margin-bottom: 8px;
        }
        .itinerary-spot {
            color: #d0d0f0;
            font-size: 13px;
            padding: 2px 0;
        }
        .itinerary-food {
            color: #ff9f43;
            font-size: 12px;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.06);
        }

        /* ===== 人脸分析弹窗 ===== */
        .face-detail-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            backdrop-filter: blur(8px);
        }

        /* ===== Scrollbar ===== */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
        ::-webkit-scrollbar-thumb { background: rgba(123,47,247,0.3); border-radius: 3px; }

        /* ===== 关闭不需要的元素 ===== */
        footer { visibility: hidden; }
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
    return f"""
    <div class="card-cover" style="background:linear-gradient(135deg,{c1} 0%,{c2} 100%);">
        <div class="card-cover-icon">{icon}</div>
        <div class="card-cover-dest">{destination}</div>
        <div class="card-cover-shimmer"></div>
    </div>
    """


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
                f"""<div class="itinerary-day">
                    <strong>{day.get('label', '')}</strong>
                    {spots}
                    {food_block}
                </div>"""
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
