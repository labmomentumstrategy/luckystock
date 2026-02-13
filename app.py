"""
VMR 觀察站 - 首頁
Professional Demo & Trust Building
"""
import streamlit as st
import streamlit.components.v1 as components

# --- Page Configuration ---
st.set_page_config(
    page_title="VMR 觀察站 | Professional Demo",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Server-Side Tracking ---
try:
    from utils.analytics import track_page_view
    track_page_view("Home", page_path="/")
except Exception:
    pass

# --- Import Data & UI ---
from utils.gsheet import get_summary_stats
from utils.ui import load_css, inject_scanline_effect, render_sidebar

# --- Load Custom CSS & Effects ---
load_css()
inject_scanline_effect()

# --- Main Layout ---
st.markdown("### 🔭 System Dashboard")
st.caption("Professional Demo & Trust Verification")

# --- Sidebar (Modular) ---
render_sidebar()

# --- Sci-Fi HUD Ticker (Custom Component) ---
stats = get_summary_stats()

st.markdown(f"""
<div class="hud-container">
<!-- Row 1 -->
<div class="hud-item">
<div class="hud-label">DATA RANGE</div>
<div class="hud-value">2021-2026</div>
</div>
<div class="hud-item highlight">
<div class="hud-label">WIN RATE</div>
<div class="hud-value">{stats['win_rate']}%</div>
</div>
<div class="hud-item">
<div class="hud-label">AVG RETURN</div>
<div class="hud-value val-green">+{stats['avg_return']}%</div>
</div>

<!-- Row 2 -->
<div class="hud-item">
<div class="hud-label">TOTAL SIGNALS</div>
<div class="hud-value">{stats['total_signals']:,}</div>
</div>
<div class="hud-item">
<div class="hud-label">WIN COUNT</div>
<div class="hud-value val-green">{stats['win_count']:,}</div>
</div>
<div class="hud-item">
<div class="hud-label">LOSS COUNT</div>
<div class="hud-value val-red">{stats['loss_count']:,}</div>
</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Content Body ---
st.markdown("### 📊 What is VMR?")
st.info("""
**VMR (Volume-Momentum-Radar)** 是一個量價動能演算法，專門捕捉市場中**異常的買盤動能**。

此 Demo 站點展示了我們演算法的歷史回測數據與即時訊號的可視化效果。
我們相信數據會說話，透過透明的歷史紀錄，驗證策略的有效性。
""")

st.markdown("### 🔥 Strategy Highlights")
st.markdown("""
- **量能偵測**：不只看價，更看量。捕捉主力進場痕跡。
- **動能確認**：過濾雜訊，只在動能最強時介入。
- **歷史驗證**：超過 5 年的完整市場回測數據支持。
""")

# --- Footer Disclaimer ---
st.markdown("""
<div class="disclaimer-box">
    <strong>⚠️ 免責聲明 (Disclaimer)</strong><br><br>
    本平台僅供 [技術展示] 與 [學術研究] 用途。所有數據皆為歷史回測結果或模擬演示，非投資建議。<br>
    金融市場具有高度風險，過去績效不代表未來表現。使用者應自行評估風險，本團隊不對任何交易損失負責。
</div>
""", unsafe_allow_html=True)
