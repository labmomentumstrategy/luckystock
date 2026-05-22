"""
Telegram Channel - Explanation Page
"""
import streamlit as st

from utils.ui import load_css, inject_scanline_effect, render_sidebar

# --- Page Configuration (Streamlit 必須的第一個呼叫) ---
st.set_page_config(
    page_title="Telegram Channel | CB Observatory",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Server-Side Tracking (GA4 追蹤) ---
try:
    from utils.analytics import track_page_view
    track_page_view("Telegram_Channel", page_path="/telegram")
except Exception:
    pass

# --- Load Custom CSS & Effects (全站 Cyberpunk 特效與字型) ---
load_css()
inject_scanline_effect()

# --- Sidebar (模組化導覽列) ---
render_sidebar()

# --- Main Layout ---
st.markdown("### 📢 Telegram Channel")
st.markdown("---")

# 版面配置：左側介紹，右側精緻的引流 CTA 卡片
col_info, col_cta = st.columns([3, 2])

with col_info:
    st.markdown("#### 📡 Subscribe to CB Lab Channel for Latest News & Strategies!")
    st.markdown(
        """
        CB Lab has established an **Exclusive Telegram Channel** to provide automated daily Convertible Bond (CB) strategy picking for swing traders.
        
        ##### 🚀 Core Channel Strategy Picks:
        **Exclusive Quant Strategy Publishing**
           - Combining Data Engineering with Quantitative Strategies to regularly publish the latest data watchlists.
        """
    )

with col_cta:
    # 採用專屬 HUD 風格設計的引流資訊卡，配合綠色螢光霓虹邊框
    st.markdown(
        """
        <div class="stock-info-card" style="padding: 25px; text-align: center; border-color: #00d4aa; box-shadow: 0 0 15px rgba(0, 212, 170, 0.1);">
            <div class="card-label" style="font-size: 0.9rem; color: #00d4aa; font-weight: bold;">⚡ Exclusive Telegram Community ⚡</div>
            <div class="card-value" style="font-size: 1.6rem; margin: 15px 0; color: #ffffff;">Join for Free</div>
            <div class="card-sub" style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 20px; line-height: 1.5;">
                Subscribe to our Telegram channel now and start your swing trading evolution!
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Native Streamlit link button for users to join the channel
    st.link_button(
        "👉 Join the Exclusive Telegram Channel Now",
        "https://t.me/+Bo-1xK7HiyVkNmZl",
        use_container_width=True
    )
    
    st.markdown(
        """
        <p style="text-align: center; font-size: 0.75rem; color: #6b7280; margin-top: 10px;">
            📡 Status: <span style="color: #00d4aa; font-weight: bold;">● Online & Active</span>
        </p>
        """,
        unsafe_allow_html=True
    )

# --- Disclaimer Section (Full Width) ---
st.markdown("---")
st.markdown(
    """
    <div style="font-size: 0.8rem; color: #6b7280; line-height: 1.6; padding: 15px; border: 1px solid #ef4444; border-radius: 8px; background-color: rgba(31, 41, 55, 0.3);">
        <strong style="color: #ef4444;">⚠️ Disclaimer:</strong> All data and content provided on this platform are strictly for personal data engineering research and educational purposes. They do not constitute financial, investment, or trading advice. Please note that the data processing pipeline involves Artificial Intelligence (AI) and automated algorithms, which may produce errors, inaccuracies, or delayed information. Users must conduct their own independent research and verification before making any financial decisions. Past performance is not indicative of future results. The creator assumes no liability for any financial losses or damages incurred from the use of this information.
    </div>
    """,
    unsafe_allow_html=True
)
