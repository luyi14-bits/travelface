<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.58+-red?logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/Deps-6_pure_Python_pkgs-brightgreen" alt="Deps">
  <img src="https://img.shields.io/badge/Compile-Zero_C_extensions-success" alt="No C">
</p>

<h1 align="center">TravelFace</h1>
<p align="center"><strong>Snap a Photo . Read Your Emotion . Get a Tailored Trip</strong></p>
<p align="center">Personalized Travel Recommendation based on Face Profiling & Emotion Recognition</p>

---

## Introduction

TravelFace is an **end-to-end intelligent travel recommendation system**. Simply upload a photo, and the system will detect faces, analyze age/gender profiles, recognize emotions, then call an LLM to generate **3 personalized travel routes** for you.

### Core Features

| Module | Description |
|--------|-------------|
| **Face Detection** | Pure NumPy YCbCr skin-color detection + Flood Fill connected-component analysis |
| **User Profiling** | Heuristic age/gender estimation via image brightness and RGB channel ratios |
| **Emotion Recognition** | Seven basic emotions classified by facial brightness and contrast |
| **Travel Recommendation** | OpenAI-compatible API + 12 built-in mock routes (dual mode) |
| **Dual-Theme UI** | Dark/light mode auto-adaptation + hover zoom animations |

### Highlights

- **Zero visual dependencies** -- No OpenCV / MediaPipe / DeepFace / TensorFlow
- **Instant startup** -- No model downloads needed, total install size < 50MB
- **Dual-mode recommendation** -- LLM generation + mock data, no API key required
- **Cross-platform** -- 6 pure Python packages, runs on any OS

---

## Architecture

```
Upload Photo -> Pillow Read -> RGB ndarray
       |
FaceDetector (YCbCr Skin + Flood Fill + 6-Layer Filtering)
       |
   UserProfiler       EmotionRecognizer
   (brightness/RGB)   (brightness/contrast)
       +-------------------+
              |
       analyze_image()
       |
TravelAgent.generate()
  LLM call (with API Key) / mock data (without)
       |
render_travel_cards() -> 3 Travel Routes
```

### Directory Structure

```
travelface/
  app.py                  # Streamlit entry
  config.py               # Config management
  requirements.txt        # 6 pure Python deps
  run.bat                 # Windows one-click launcher
  src/
    vision/
      face_detector.py      # YCbCr skin detection
      user_profiler.py      # Age/gender profiling
      emotion_recognizer.py # Emotion classification
    llm/
      travel_agent.py       # Travel recommendation agent
    ui/
      components.py         # UI components + CSS
  docs/                   # Technical docs / deployment guide / flowchart
```

---

## Quick Start

### One-click Launch (Windows)

```bash
Double-click run.bat
```

### Manual Install

```bash
cd travelface
pip install -r requirements.txt
streamlit run app.py
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | >=1.28.0 | Web framework |
| Pillow | >=10.0.0 | Image processing |
| numpy | >=1.24.0 | Matrix operations |
| requests | >=2.31.0 | HTTP client |
| openai | >=1.3.0 | LLM API |
| python-dotenv | >=1.0.0 | Environment variables |

All pure Python packages -- **zero C extension compilation** required.

---

## LLM API Configuration (Optional)

Copy `.env.example` to `.env` and add your API key:

```env
LLM_API_KEY=sk-xxxxxxxx
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_MODEL_NAME=doubao-1.5-pro-32k
```

> No API key? No problem -- the system falls back to 12 built-in mock travel routes.

---

## Online Demo

Deployed on **Streamlit Cloud**:

**[travelface-luyi14-bits.streamlit.app](https://travelface-luyi14-bits.streamlit.app/)**

---

## Documentation

| Doc | Description |
|-----|-------------|
| [Technical Docs (CN)](docs/技术文档.md) | Full architecture, module details, dev issues & solutions |
| [Technical Docs (HTML)](docs/技术文档.html) | Print-to-PDF ready HTML version |
| [Deployment Guide (CN)](docs/部署指南.md) | Local + Streamlit Cloud deployment |
| [Deployment Guide (HTML)](docs/部署指南.html) | Print-to-PDF ready HTML version |
| [Flowchart](docs/flowchart.html) | Mermaid interactive flowchart |

---

## Dev Journey

From a **600MB+** heavyweight pipeline (OpenCV + MediaPipe + DeepFace + TensorFlow) down to **6 pure Python packages**:

| Removed | Reason |
|---------|--------|
| opencv-python-headless | No prebuilt wheel for Python 3.13+ |
| mediapipe | Hard dependency on cv2, chain failure |
| deepface | Depends on TensorFlow (~600MB) |
| tensorflow | Too large, OOM on Streamlit Cloud |

Face detection evolved through 3 iterations: over-filtering (false positives from walls/clothes) -> relaxing (missed real faces) -> over-detection (3-4 fake faces) -> best single result strategy.

See [Technical Docs, Chapter 7](docs/技术文档.md) for full details.

---

## Tech Stack

| Tech | Usage |
|------|-------|
| **Streamlit** | Web framework |
| **NumPy** | Face detection / profiling / emotion |
| **Pillow** | Image I/O / box drawing |
| **OpenAI SDK** | LLM API calls |
| **python-dotenv** | Environment variables |

---

## License

MIT

---

<p align="center">
  <sub>Made for Computer Vision Course Design</sub>
</p>