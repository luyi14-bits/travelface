import streamlit as st

from config import config
from src.vision import analyze_image
from src.llm.travel_agent import TravelAgent
from src.ui.components import (
    inject_custom_css,
    render_analysis_summary,
    render_annotated_image,
    render_travel_cards,
)
from utils.helpers import read_uploaded_image

st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
)

inject_custom_css()

st.markdown(
    f'<h1 style="text-align:center;">{config.PAGE_ICON} {config.PAGE_TITLE}</h1>'
    '<p style="text-align:center;color:#a0a0d0;font-size:1.1rem;margin-top:-10px;">'
    '上传一张照片，AI 将识别画像与情绪，为你定制专属旅行路线 ✨</p>',
    unsafe_allow_html=True,
)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown(
        '<p style="color:#c0c0ff;font-weight:600;font-size:1.1rem;">📸 上传照片</p>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "支持 JPG / PNG 格式",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    st.markdown(
        '<p style="color:#c0c0ff;font-weight:600;font-size:1.1rem;">📝 补充心情（可选）</p>',
        unsafe_allow_html=True,
    )
    mood_text = st.text_area(
        "用文字描述你此刻的心情...",
        placeholder="例：刚刚结束期末考，想出去放松一下...",
        label_visibility="collapsed",
    )

    analyze_btn = st.button("🔍 开始分析", type="primary", use_container_width=True)

with col_right:
    if uploaded_file is not None:
        image = read_uploaded_image(uploaded_file)
        if image is not None:
            st.session_state["cached_image"] = image
            st.markdown(
                '<p style="color:#90d0ff;font-size:0.9rem;text-align:center;">📷 预览</p>',
                unsafe_allow_html=True,
            )
            st.image(uploaded_file.getvalue(), use_container_width=True)

if analyze_btn and uploaded_file is not None:
    image = st.session_state.get("cached_image")
    if image is None:
        image = read_uploaded_image(uploaded_file)

    if image is None:
        st.error("无法读取图片，请确认格式正确")
    else:
        with st.spinner("👁️ 正在进行人脸检测与画像分析..."):
            vision_result = analyze_image(image)

        st.markdown("---")
        st.markdown("## 📊 分析结果")

        render_analysis_summary(vision_result)

        col_img, col_detail = st.columns([1, 1], gap="large")
        with col_img:
            render_annotated_image(
                image,
                vision_result.get("faces", []),
            )

        with col_detail:
            faces = vision_result.get("faces", [])
            for i, face in enumerate(faces):
                profile = face.get("profile", {})
                emotion = face.get("emotion", {})
                html = (
                    f'<div class="face-detail-card">'
                    f'<strong class="fd-title">👤 #{i + 1}</strong>&nbsp;'
                    f'<span class="fd-label">{profile.get("gender", "-")}</span> · '
                    f'<span class="fd-label">{profile.get("age_group", "-")}</span> · '
                    f'<span class="fd-emotion">😊 {emotion.get("emotion", "-")}</span> '
                    f'<span class="fd-conf">({emotion.get("confidence", 0):.0%})</span>'
                    f'</div>'
                )
                st.markdown(html, unsafe_allow_html=True)

            if mood_text.strip():
                st.info(f"📝 心情描述：{mood_text.strip()}")

        st.markdown("---")
        with st.spinner("🤖 正在生成个性化旅游推荐..."):
            agent = TravelAgent()
            travel_result = agent.generate(vision_result)

        render_travel_cards(travel_result.get("routes", []))

elif analyze_btn and uploaded_file is None:
    st.warning("请先上传一张照片 👆")

st.markdown(
    '<p style="text-align:center;color:#505070;font-size:0.8rem;margin-top:60px;">'
    'TravelFace · 计算机视觉课设项目 · Powered by MediaPipe + Streamlit</p>',
    unsafe_allow_html=True,
)
