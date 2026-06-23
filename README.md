# ⚡ TRINETRA AI — Smart Traffic Violation Detection & Automated Challan System

> **AI-powered traffic enforcement pipeline** that detects vehicles, identifies traffic violations, reads license plates via OCR, and auto-generates official PDF challans (tickets) — all from a single traffic scene image.

---

## 🧠 What It Does

TRINETRA AI is a multi-agent computer vision pipeline built for automated traffic law enforcement. Upload an image of a traffic scene and the system:

1. **Detects vehicles & persons** using YOLOv11 object detection
2. **Identifies violations** — currently: **Triple Riding** (3+ persons on a motorcycle)
3. **Reads license plates** via PaddleOCR (tries full image first, then crops per-vehicle)
4. **Generates annotated evidence image** with YOLO bounding boxes drawn
5. **Creates a PDF challan** (official traffic ticket) with plate number, violation details, receipt ID, timestamp, and embedded evidence image
6. **Computes a Violation Risk Score** (0–100%) based on detected violations

All of this is surfaced through a **Streamlit web dashboard** with a dark-mode UI.

---

## 🏗️ Project Structure

```
TRINETRA_AI/
├── main.py                   # Entry point — launches Streamlit dashboard
├── requirements.txt          # Python dependencies
│
├── app/
│   └── pipeline.py           # Core orchestration: runs all agents in sequence
│
├── agents/
│   ├── vehicle_agent.py      # YOLO11 — detects persons, motorcycles, cars, buses, trucks
│   ├── triple_riding_agent.py# Logic: motorcycle_count >= 1 AND person_count >= 3
│   ├── violation_agent.py    # Maps detected conditions → violation labels
│   ├── ocr_agent.py          # PaddleOCR — reads license plate text from image
│   ├── challan_agent.py      # Generates PDF challan with ReportLab
│   ├── plate_agent.py        # (stub)
│   ├── helmet_agent.py       # (stub)
│   ├── tracking_agent.py     # (stub)
│   ├── enhancement_agent.py  # (stub)
│   └── violation_agent.py    # Violation rule engine
│
├── models/
│   └── detection/            # YOLO model weights stored here (yolo11n.pt)
│
├── dashboard/
│   └── dashboard.py          # Streamlit UI — upload, display results, download challan
│
├── uploads/                  # Uploaded images saved here
└── outputs/
    ├── evidence/             # Annotated images (YOLO boxes drawn)
    └── challans/             # Generated PDF challan files
```

---

## 🔄 Pipeline Flow

```
Image Upload
    │
    ▼
VehicleAgent  ──────── YOLO11 detects: persons (cls=0), motorcycles (cls=3),
    │                  cars (cls=2), buses (cls=5), trucks (cls=7)
    ▼
TripleRidingAgent ──── Check: motorcycle_count >= 1 AND person_count >= 3
    │
    ▼
ViolationAgent ──────── Maps triple_riding → ["Triple Riding"]
    │
    ▼
OCRAgent ───────────── PaddleOCR on full image → extract Indian plate (e.g. DL01AB1234)
    │                  Fallback: crop each vehicle bbox → OCR each crop
    ▼
ChallanAgent ───────── ReportLab PDF with: receipt no., plate, timestamp,
    │                  violations, embedded evidence image
    ▼
Risk Score ─────────── triple_riding = +40pts, each violation = +20pts (cap 100)
    │
    ▼
Streamlit Dashboard ── Annotated image tabs, metric cards, badge violations, PDF download
```

---

## 📤 Outputs

| Output | Location | Description |
|--------|----------|-------------|
| **Annotated Evidence Image** | `outputs/evidence/evidence_<name>_<timestamp>.jpg` | Original image with YOLO bounding boxes and class labels drawn |
| **PDF Challan** | `outputs/challans/<PLATE>_<timestamp>.pdf` | Official ticket with receipt number, vehicle plate, violations, and evidence image embedded |

### Sample PDF Challan Contents
```
TRINETRA AI - TRAFFIC VIOLATION REPORT
───────────────────────────────────────
Receipt Number:     TRN-20250621143022
Vehicle Plate:      MH12AB1234
Date & Time:        2025-06-21 14:30:22
Violations:         Triple Riding
───────────────────────────────────────
[Annotated Evidence Image]

Notice: This is an official AI-generated traffic violation ticket.
```

### Risk Score Logic
| Condition | Points |
|-----------|--------|
| Triple Riding detected | +40 |
| Each additional violation | +20 |
| Maximum score | 100 |

---

## 🖥️ Dashboard UI

Streamlit dark-mode interface with:
- **Image uploader** — drag & drop JPG/PNG
- **Annotated Evidence tab** vs **Original Image tab**
- **Metric cards**: Violation Risk Index, Motorcycle count, Person count, License Plate
- **Violation badges**: red `⚠️ Triple Riding DETECTED` or green `✅ NO VIOLATIONS`
- **PDF download button** — download generated challan instantly

---

## 🚀 Setup & Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `paddlepaddle` and `paddleocr` may require specific install steps on Windows. Refer to [PaddlePaddle install guide](https://www.paddlepaddle.org.cn/en/install/quick).

### 2. YOLO Model

Model auto-downloads `yolo11n.pt` from Ultralytics on first run if not present in `models/detection/`.

To use a custom model, place it at:
```
models/detection/yolo11n.pt   # or yolo26s.pt
```

### 3. Run

```bash
python main.py
```

Or directly:

```bash
python -m streamlit run dashboard/dashboard.py
```

App opens at: `http://localhost:8501`

---

## 🛠️ Tech Stack

| Component | Library |
|-----------|---------|
| Object Detection | [Ultralytics YOLO11](https://github.com/ultralytics/ultralytics) |
| OCR (License Plate) | [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) |
| PDF Generation | [ReportLab](https://www.reportlab.com/) |
| Web Dashboard | [Streamlit](https://streamlit.io/) |
| Image Processing | OpenCV, Pillow |
| Deep Learning Backend | PyTorch, PaddlePaddle |

---

## 🔮 Planned / Stub Agents

These agents exist as stubs for future expansion:

| Agent | Planned Function |
|-------|-----------------|
| `helmet_agent.py` | Detect helmet absence on riders |
| `tracking_agent.py` | Multi-frame vehicle tracking |
| `enhancement_agent.py` | Image super-resolution before OCR |
| `plate_agent.py` | Dedicated license plate region detector |

---

## ⚠️ Notes

- Currently detects **Triple Riding** violation only (architecture supports adding more)
- License plate regex matches **Indian format**: `XX00XX0000` (e.g. `DL01AB1234`)
- OCR uses CPU by default; auto-switches to GPU if CUDA-enabled PaddlePaddle found
- MKLDNN disabled by default to avoid PaddlePaddle oneDNN compatibility crash on Windows

---

## 📄 License

Built for **Gridlock Round 2** competition. All rights reserved.
