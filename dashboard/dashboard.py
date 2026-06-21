import streamlit as st
import os
from PIL import Image
from app.pipeline import Pipeline
# Set page config for professional title and layout
st.set_page_config(
    page_title="TRINETRA AI - Traffic Violation Detection",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS for rich styling, card aesthetics, and responsive layout
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 100%);
        color: #f3f4f6;
    }
    
    /* Header/Title */
    .title-container {
        padding: 2rem 0;
        text-align: center;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(to right, #60a5fa, #3b82f6, #1d4ed8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #9ca3af;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Cards */
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.3);
    }
    
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9ca3af;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #3b82f6;
        margin-top: 0.5rem;
    }
    
    /* Badges */
    .badge {
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
    }
    
    .badge-danger {
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #a7f3d0;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    /* Log console */
    .console-log {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem;
        font-family: monospace;
        color: #58a6ff;
        font-size: 0.9rem;
        height: 150px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)
# Sidebar Design
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 🚦 TRINETRA AI")
    st.markdown("<p style='color: #6b7280; font-size: 0.85rem;'>Smart Traffic Enforcement System</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("#### System Information")
    st.write("🛰️ **Status:** Operational")
    st.write("⚙️ **Engine:** YOLO11 + PaddleOCR")
    st.write("⏳ **Mode:** Real-time Single Image Inference")
    
    st.markdown("---")
    
    st.info("Trinetra AI monitors traffic feeds and automatically generates challans for violations such as **Triple Riding**.")
# Title
st.markdown("""
    <div class="title-container">
        <h1 class="main-title">TRINETRA AI</h1>
        <p class="subtitle">Next-Generation AI Traffic Enforcement & Automated Challan System</p>
    </div>
""", unsafe_allow_html=True)
# Instantiate Pipeline (wrapped in cached resource so it doesn't reload on every interaction)
@st.cache_resource
def get_pipeline():
    return Pipeline()
try:
    pipe = get_pipeline()
    st.success("🤖 Core AI Models Initialized successfully.")
except Exception as e:
    st.error(f"❌ Error initializing AI pipeline: {e}")
    st.stop()
# Layout Columns
uploaded = st.file_uploader(
    "Drag and drop or browse a traffic scene image...",
    type=["jpg", "png", "jpeg"]
)
if uploaded:
    # Create directories if they do not exist
    os.makedirs("uploads", exist_ok=True)
    image_path = os.path.join("uploads", uploaded.name)
    
    with open(image_path, "wb") as f:
        f.write(uploaded.getbuffer())
        
    st.info("Image uploaded successfully! Ready for processing.")
    # Process
    with st.spinner("⚡ Running AI Object Detection & License Plate OCR Extraction..."):
        try:
            result = pipe.run(image_path)
            
            # Layout after processing
            col1, col2 = st.columns([1.2, 1])
            
            with col1:
                st.subheader("👁️ AI Detection Analysis")
                
                # Tabs for original vs annotated evidence
                tab_evidence, tab_original = st.tabs(["✨ Annotated Evidence", "🖼️ Original Image"])
                
                with tab_evidence:
                    if os.path.exists(result["evidence"]):
                        st.image(result["evidence"], use_container_width=True, caption="TRINETRA AI - Detections and Class Labels")
                    else:
                        st.warning("Evidence image could not be loaded.")
                        
                with tab_original:
                    st.image(image_path, use_container_width=True, caption="Original Uploaded Frame")
                    
            with col2:
                st.subheader("📊 Enforcement Metrics")
                
                # Risk Score Metric Card
                risk_color = "#38bdf8" if result["risk"] < 30 else "#f59e0b" if result["risk"] < 70 else "#ef4444"
                st.markdown(f"""
                    <div class="metric-card" style="border-left: 5px solid {risk_color};">
                        <div class="metric-label">Violation Risk Index</div>
                        <div class="metric-value" style="color: {risk_color};">{result["risk"]}%</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Side-by-side metric cards
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">🏍️ Motorcycles</div>
                            <div class="metric-value">{result["motorcycles"]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with m_col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">👤 Persons</div>
                            <div class="metric-value">{result["persons"]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                # License Plate Card
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">🆔 Extracted Plate Number</div>
                        <div class="metric-value" style="color: #10b981; font-family: monospace; font-size: 1.8rem; letter-spacing: 0.05em;">
                            {result["plate"]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Violations List Card
                st.subheader("⚖️ Violation Assessment")
                if result["violations"]:
                    for v in result["violations"]:
                        st.markdown(f'<span class="badge badge-danger">⚠️ {v} DETECTED</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge badge-success">✅ NO VIOLATIONS DETECTED</span>', unsafe_allow_html=True)
                    
                # Challan Download Box
                st.markdown("---")
                st.markdown("#### 📄 Document Generation")
                if os.path.exists(result["pdf"]):
                    with open(result["pdf"], "rb") as file:
                        pdf_data = file.read()
                        
                    st.download_button(
                        label="📥 Download Official Challan PDF",
                        data=pdf_data,
                        file_name=f"Challan_{result['plate']}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("PDF Challan generated and formatted successfully.")
                else:
                    st.error("Error: Could not retrieve Challan document path.")
                    
        except Exception as ex:
            st.error(f"Failed to process image: {ex}")
            import traceback
            st.code(traceback.format_exc())
else:
    # Landing placeholder layout
    st.markdown("---")
    st.markdown("<div style='text-align: center; padding: 3rem; color: #6b7280;'>", unsafe_allow_html=True)
    st.markdown("### 📸 Upload a traffic frame to run TRINETRA AI pipeline")
    st.markdown("The system will automatically detect vehicles, calculate rider counts, scan plates with PaddleOCR, and prepare traffic tickets.")
    st.markdown("</div>", unsafe_allow_html=True)