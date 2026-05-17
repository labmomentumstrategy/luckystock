"""
CB Scanner - 首頁
"""
import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="CB Scanner | Daily Overview",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Server-Side Tracking ---
try:
    from utils.analytics import track_page_view
    track_page_view("CB_Scanner_Home", page_path="/")
except Exception:
    pass

# --- Import Data & UI ---
from utils.gsheet import get_all_cb_data
from utils.ui import load_css, inject_scanline_effect, render_sidebar

# --- Load Custom CSS & Effects ---
load_css()
inject_scanline_effect()

# --- Sidebar (Modular) ---
render_sidebar()

# --- Main Layout ---
st.markdown("### 🔍 CB Scanner")

# --- Fetch Data ---
with st.spinner("載入 CB 資料中..."):
    df_cb = get_all_cb_data()

if not df_cb.empty:
    # 找出最新交易日 (select max trade date from cb gsheet)
    max_date = df_cb['TRADE_DATE'].max()
    
    # 標題行：左邊放 caption + 日期，右邊放 Reset 按鈕（對齊下方 5 欄 Filter）
    header_cols = st.columns(5)
    with header_cols[0]:
        st.caption("全市場可轉債當日數據掃描")
        st.write(f"**最新交易日期:** {max_date.strftime('%Y-%m-%d')}")
    # 初始化重設計數器
    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0
    rc = st.session_state.reset_counter
    
    with header_cols[4]:
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.session_state.reset_counter += 1
            st.rerun()
    
    # 篩選最新交易日的資料 (where trade date = max_date)
    df_latest = df_cb[df_cb['TRADE_DATE'] == max_date].copy()
    
    # --- 5 Columns for Filters ---
    filter_cols = st.columns(5)
    
    # 確保 REFERENCE_PRICE 是數值並計算邊界
    ref_price_series = pd.to_numeric(df_latest['REFERENCE_PRICE'], errors='coerce').dropna()
    if not ref_price_series.empty:
        min_price = float(ref_price_series.min())
        max_price = float(ref_price_series.max())
    else:
        min_price, max_price = 0.0, 1000.0  # 預設保護
        
    # 確保 CONVERSION_VALUE 是數值並計算邊界
    cv_series = pd.to_numeric(df_latest['CONVERSION_VALUE'], errors='coerce').dropna()
    if not cv_series.empty:
        min_cv = float(cv_series.min())
        max_cv = float(cv_series.max())
    else:
        min_cv, max_cv = 0.0, 1000.0
        
    # 確保 CONVERTED_PERCENTAGE 是數值並乘以 100
    conv_pct_series = pd.to_numeric(df_latest['CONVERTED_PERCENTAGE'], errors='coerce').dropna() * 100
    if not conv_pct_series.empty:
        min_pct = float(conv_pct_series.min())
        max_pct = float(conv_pct_series.max())
    else:
        min_pct, max_pct = 0.0, 100.0
        
    # 確保 REMAINING_DAYS 是數值並計算邊界
    rem_days_series = pd.to_numeric(df_latest['REMAINING_DAYS'], errors='coerce').dropna()
    if not rem_days_series.empty:
        min_days = float(rem_days_series.min())
        max_days = float(rem_days_series.max())
    else:
        min_days, max_days = 0.0, 3650.0
    
    with filter_cols[0]:
        price_range = st.slider(
            "Reference Price",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            key=f"price_slider_{rc}"
        )
        
    with filter_cols[1]:
        cv_range = st.slider(
            "Conversion Value",
            min_value=min_cv,
            max_value=max_cv,
            value=(min_cv, max_cv),
            key=f"cv_slider_{rc}"
        )
        
    with filter_cols[2]:
        conv_pct_range = st.slider(
            "Converted %",
            min_value=min_pct,
            max_value=max_pct,
            value=(min_pct, max_pct),
            key=f"conv_pct_slider_{rc}"
        )
        
    with filter_cols[3]:
        rem_days_range = st.slider(
            "Remaining Days",
            min_value=min_days,
            max_value=max_days,
            value=(min_days, max_days),
            key=f"rem_days_slider_{rc}"
        )
        
    with filter_cols[4]:
        st.markdown("<div style='height: 60px; border: 1px dashed #333; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: #666; margin-top: 25px;'>Filter 5 (Reserved)</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    # 依據 Slider 過濾資料
    # 建立一個全為 True 的 mask，逐步疊加過濾條件
    mask = pd.Series([True] * len(df_latest), index=df_latest.index)
    
    if price_range[0] > min_price or price_range[1] < max_price:
        mask &= (df_latest['REFERENCE_PRICE'] >= price_range[0]) & (df_latest['REFERENCE_PRICE'] <= price_range[1])
        
    if cv_range[0] > min_cv or cv_range[1] < max_cv:
        mask &= (df_latest['CONVERSION_VALUE'] >= cv_range[0]) & (df_latest['CONVERSION_VALUE'] <= cv_range[1])
        
    if conv_pct_range[0] > min_pct or conv_pct_range[1] < max_pct:
        mask &= ((df_latest['CONVERTED_PERCENTAGE'] * 100) >= conv_pct_range[0]) & ((df_latest['CONVERTED_PERCENTAGE'] * 100) <= conv_pct_range[1])
        
    if rem_days_range[0] > min_days or rem_days_range[1] < max_days:
        rem_days_numeric = pd.to_numeric(df_latest['REMAINING_DAYS'], errors='coerce')
        mask &= (rem_days_numeric >= rem_days_range[0]) & (rem_days_numeric <= rem_days_range[1])
        
    df_filtered = df_latest[mask].copy()
    
    # 隱藏不需要的欄位 (TRADE_DATE 已在上方顯示過)
    cols_to_drop = [
        'IS_ACTIVE', 'DATE_OF_DELISTED', 'COUPON_RATE', 'TRADE_DATE',
        'OUTSTANDING_AMOUNT', 'LATEST_PUT_PRICE', 'EARLY_REDEMPTION_PRICE'
    ]
    df_display = df_filtered.drop(columns=cols_to_drop, errors='ignore')
    
    # 新增動態序號欄位到最左側
    df_display.insert(0, 'NO.', range(1, len(df_display) + 1))
    
    # 調整欄位順序：CB_NAME 右邊依序放 REF_PRICE, CV, CONVERTED_PCT, REM_DAYS
    cols = list(df_display.columns)
    priority_after_cbname = ['REFERENCE_PRICE', 'CONVERSION_VALUE', 'CONVERTED_PERCENTAGE', 'REMAINING_DAYS']
    if 'CB_NAME' in cols:
        for col in priority_after_cbname:
            if col in cols:
                cols.remove(col)
        idx = cols.index('CB_NAME') + 1
        for i, col in enumerate(priority_after_cbname):
            if col in df_display.columns:
                cols.insert(idx + i, col)
        df_display = df_display[cols]
    
    # 顯示資料表（支援行選取 highlight）
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )
else:
    st.warning("目前無法取得 CB 資料，請確認資料源或連線設定。")
