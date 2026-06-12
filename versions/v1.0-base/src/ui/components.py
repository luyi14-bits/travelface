import streamlit as st
from PIL import Image

from utils.helpers import cv2_to_pil, draw_face_boxes


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
    st.image(pil_image, caption=caption, use_container_width=True)


def render_travel_card(route: dict, index: int) -> None:
    with st.container():
        st.markdown("---")

        emojis = ["🥇", "🥈", "🥉"]
        medal = emojis[index] if index < len(emojis) else "📍"

        st.markdown(f"### {medal} {route.get('title', '路线')}")

        col1, col2, col3 = st.columns(3)
        col1.caption(f"📍 {route.get('destination', '')}")
        col2.caption(f"⏱️ {route.get('duration', '')}")
        col3.caption(f"💰 {route.get('budget', '')}")

        st.markdown(f"> 💡 *{route.get('reason', '')}*")

        tags = route.get("tags", [])
        if tags:
            tag_html = " ".join(
                f"<span style='background:#f0f2f6;padding:2px 10px;border-radius:12px;font-size:12px;margin-right:4px;'>{t}</span>"
                for t in tags
            )
            st.markdown(tag_html, unsafe_allow_html=True)

        itinerary = route.get("itinerary", [])
        if itinerary:
            st.markdown("#### 🗺️ 行程一览")
            cols = st.columns(len(itinerary))
            for i, day in enumerate(itinerary):
                with cols[i]:
                    st.markdown(f"**{day.get('label', f'Day {i+1}')}**")
                    for spot in day.get("spots", []):
                        st.markdown(f"▸ {spot}")
                    if day.get("food"):
                        st.caption("🍴 " + " · ".join(day["food"]))


def render_travel_cards(routes: list) -> None:
    st.markdown("## 🛫 个性化旅游推荐")
    st.caption("基于您的画像与情绪，为您精选以下路线 👇")

    for idx, route in enumerate(routes):
        render_travel_card(route, idx)
