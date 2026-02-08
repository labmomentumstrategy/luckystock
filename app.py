"""
VMR 觀察站 - 首頁
Volume-Momentum-Radar Observatory
"""
import streamlit as st
import streamlit.components.v1 as components

# --- Page Configuration ---
st.set_page_config(
    page_title="VMR 觀察站 | Volume-Momentum Radar",
    page_icon="📡",
    layout="wide"
)

# --- GA4 Tracking ---
GA_MEASUREMENT_ID = st.secrets.get("ga4", {}).get("measurement_id", "")
if GA_MEASUREMENT_ID:
    GA_TRACKING_CODE = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
    """
    components.html(GA_TRACKING_CODE, height=0)

# --- Import after page config ---
from utils.gsheet import get_summary_stats

# --- Custom CSS ---
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e222d 0%, #131722 100%);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2a2e39;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2196F3;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #848e9c;
        margin-top: 5px;
    }
    .hero-section {
        text-align: center;
        padding: 40px 0;
    }
    .disclaimer {
        background-color: #1e222d;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin-top: 40px;
        font-size: 0.85rem;
        color: #848e9c;
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
<div class="hero-section">
    <h1>📡 VMR 觀察站</h1>
    <p style="color: #848e9c; font-size: 1.1rem;">
        Volume-Momentum-Radar | 量價動能觀測平台
    </p>
</div>
""", unsafe_allow_html=True)

# --- Stats Cards ---
stats = get_summary_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{stats['win_rate']:.1f}%</div>
        <div class="metric-label">歷史勝率 (60日)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{stats['total_signals']:,}</div>
        <div class="metric-label">總訊號數</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{stats['today_signals']}</div>
        <div class="metric-label">今日訊號</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    data_range = ""
    if stats['data_start'] and stats['data_end']:
        data_range = f"{stats['data_start'].strftime('%Y/%m/%d')} - {stats['data_end'].strftime('%Y/%m/%d')}"
    else:
        data_range = "載入中..."
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="font-size: 1.2rem;">{data_range}</div>
        <div class="metric-label">資料期間</div>
    </div>
    """, unsafe_allow_html=True)

# --- Description ---
st.markdown("---")
st.markdown("""
### 什麼是 VMR 觀察站？

VMR 觀察站是一個**量價動能觀測平台**，透過演算法計算成交量變化指標，
標記出異常的成交量放大訊號。我們邀請您一起「觀測」市場的量價變化。

**觀測重點：**
- 📊 **動能標籤**：識別成交量異常放大的時間點
- 📈 **K 線圖表**：視覺化股價走勢與訊號位置
- 📉 **歷史驗證**：追蹤訊號後的價格表現
""")

# --- Disclaimer ---
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ 免責聲明</strong><br>
    本平台僅供研究觀測用途，所有資料與標籤皆非投資建議。
    動能標籤為成交量經由大數據演算法計算出之指標，目的在找出異常的成交量（多方買盤動能）。
    動能資料盡力求數據正確，但無法保證數據沒有誤差。
    因此，請勿以此作為任何投資活動之根據，任何數據誤差或錯誤，以市場正確資料為主。
</div>
""", unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #848e9c; font-size: 0.8rem;">
    VMR Observatory © 2026 | Contact: lab.momentum.strategy@gmail.com
</div>
""", unsafe_allow_html=True)
