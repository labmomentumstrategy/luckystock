"""
Telegram Channel - Explanation Page
"""
import streamlit as st

from utils.ui import load_css, inject_scanline_effect, render_sidebar

# --- Page Configuration (Streamlit 必須的第一個呼叫) ---
st.set_page_config(
    page_title="Telegram Channel | VMR Observatory",
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
    st.markdown("#### 📡 訂閱 VIP 頻道，掌握即時量價信號！")
    st.markdown(
        """
        VMR 觀察站特別設立了 **Telegram VIP 頻道**，為交易者提供高頻率、自動化的量價與可轉債（CB）即時監控服務。
        
        ##### 🚀 頻道核心價值與功能：
        1. **即時量價雷達警告**
           - 當市場主力資金有異常流入、突破關鍵大量時，系統將自動向頻道推送即時警報，絕不錯失起漲點。
        2. **可轉債（CB）轉換主力追蹤**
           - 精準追蹤 CB Unconverted %（未轉換比例）驟降的標的，抓出主力暗中吃貨並準備轉換拉抬的關鍵時刻。
        3. **獨家選股策略回測與發布**
           - 結合 7 大量化選股策略（包含多空雙向），定期發布最新回測數據與觀察清單，以科學的數據佐證勝率。
        4. **VIP 專屬討論與交流**
           - 進入 VIP 精英群組，與眾多專業量化交易者交流心得，共同精進您的交易系統。
        """
    )

with col_cta:
    # 採用專屬 HUD 風格設計的引流資訊卡，配合綠色螢光霓虹邊框
    st.markdown(
        """
        <div class="stock-info-card" style="padding: 25px; text-align: center; border-color: #00d4aa; box-shadow: 0 0 15px rgba(0, 212, 170, 0.1);">
            <div class="card-label" style="font-size: 0.9rem; color: #00d4aa; font-weight: bold;">⚡ Telegram VIP 社群 ⚡</div>
            <div class="card-value" style="font-size: 1.6rem; margin: 15px 0; color: #ffffff;">免費加入</div>
            <div class="card-sub" style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 20px; line-height: 1.5;">
                立即訂閱我們的 Telegram 頻道，開啟您的量化量價追蹤與交易智能進化之旅！
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 原生 Streamlit 連結按鈕，供使用者點擊加入頻道
    st.link_button(
        "👉 立即加入 Telegram VIP 頻道",
        "https://t.me/your_telegram_channel_link",  # 您可以隨時在此替換成實際的 TG 連結
        use_container_width=True
    )
    
    # 底部裝飾性文字
    st.markdown(
        """
        <p style="text-align: center; font-size: 0.75rem; color: #6b7280; margin-top: 10px;">
            📡 目前狀態: <span style="color: #00d4aa; font-weight: bold;">● 線上運作中</span>
        </p>
        """,
        unsafe_allow_html=True
    )
