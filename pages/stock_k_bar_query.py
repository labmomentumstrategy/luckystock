"""
VMR 觀察站 - 個股 K 線圖
Stock Chart with Signal Markers
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.gsheet import get_ticker_list, get_stock_data
from utils.analytics import track_page_view

# --- Server-Side Tracking ---
track_page_view("Individual Stock")

# --- Page Configuration ---
st.set_page_config(
    page_title="個股查詢 | VMR 觀察站",
    page_icon="📈",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .stSelectbox > div > div {
        background-color: #1e222d;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("📊 股票選擇")
    
    tickers = get_ticker_list()
    if tickers:
        selected_ticker = st.selectbox(
            "選擇股票代號",
            tickers,
            index=0
        )
    else:
        st.warning("無法載入股票清單")
        selected_ticker = None
    
    st.markdown("---")
    st.markdown("""
    **圖例說明：**
    - 🔵 藍色三角形 = 動能訊號
    - 🟢 綠色 = 上漲
    - 🔴 紅色 = 下跌
    """)

# --- Main Content ---
st.title(f"📈 {selected_ticker if selected_ticker else '個股查詢'}")

if selected_ticker:
    df = get_stock_data(selected_ticker)
    
    if not df.empty:
        # Create single chart with secondary y-axis for volume (TradingView style)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 1. Volume Bar Chart FIRST (so it's behind candlesticks)
        colors = ['rgba(0,230,118,0.4)' if df['CLOSE'].iloc[i] >= df['CLOSE'].iloc[i-1] 
                  else 'rgba(255,82,82,0.4)' for i in range(1, len(df))]
        colors.insert(0, 'rgba(0,230,118,0.4)')  # First bar
        
        mock_volume = df['CLOSE'] * 1000  # Mock volume
        fig.add_trace(go.Bar(
            x=df['TRADE_DATE'],
            y=mock_volume,
            marker=dict(color=colors, line=dict(width=0)),
            name="成交量",
            hovertemplate='成交量: %{y:,.0f}<extra></extra>',
            opacity=0.5
        ), secondary_y=True)
        
        # 2. Candlestick Chart (on top)
        fig.add_trace(go.Candlestick(
            x=df['TRADE_DATE'],
            open=df['CLOSE'],
            high=df['HIGH'],
            low=df['CLOSE'] * 0.98,
            close=df['CLOSE'],
            name="OHLC",
            increasing_line_color='#00E676',
            decreasing_line_color='#FF5252'
        ), secondary_y=False)
        
        # 3. Signal Markers
        if 'SIGNAL' in df.columns:
            signal_df = df[df['SIGNAL'] == 1]
            if not signal_df.empty:
                fig.add_trace(go.Scatter(
                    x=signal_df['TRADE_DATE'],
                    y=signal_df['CLOSE'] * 0.97,
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=14, color='#2196F3'),
                    name='動能訊號',
                    hovertemplate='訊號價: %{y:.2f}<extra></extra>'
                ), secondary_y=False)
        
        # Layout Customization
        fig.update_layout(
            height=600,
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            paper_bgcolor="#131722",
            plot_bgcolor="#131722",
            hovermode='x unified',
            spikedistance=-1,
            legend=dict(orientation="h", y=1.02, x=0, xanchor="left", yanchor="bottom"),
            margin=dict(l=50, r=50, t=30, b=50),
            title=dict(text=f"{selected_ticker} 股價走勢", x=0.5, font=dict(size=16))
        )
        
        # Y-axis styling
        fig.update_yaxes(
            title_text="價格",
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            showspikes=True,
            spikemode='across',
            spikecolor="white",
            spikethickness=1,
            spikedash='dash',
            secondary_y=False
        )
        
        fig.update_yaxes(
            title_text="成交量",
            showgrid=False,
            range=[0, mock_volume.max() * 4],  # Limit volume to bottom 25% of chart
            secondary_y=True
        )
        
        # X-axis styling
        fig.update_xaxes(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            showspikes=True,
            spikemode='across',
            spikecolor="white",
            spikethickness=1,
            spikedash='dash'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # --- Signal Table ---
        if 'SIGNAL' in df.columns:
            signal_df = df[df['SIGNAL'] == 1].copy()
            if not signal_df.empty:
                st.subheader("📊 訊號記錄")
                display_df = signal_df[['TRADE_DATE', 'CLOSE', 'HIGH']].copy()
                display_df.columns = ['訊號日期', '收盤價', '最高價']
                display_df = display_df.sort_values('訊號日期', ascending=False).head(20)
                st.dataframe(display_df, use_container_width=True)
    else:
        st.warning(f"無法取得 {selected_ticker} 的資料")
else:
    st.info("請在左側選擇股票代號")

# --- Disclaimer Footer ---
st.markdown("---")
st.markdown("""
<div style="background-color: #1e222d; padding: 15px; border-radius: 8px; border-left: 4px solid #ff9800; font-size: 0.85rem; color: #848e9c;">
    <strong>⚠️ 免責聲明</strong>：本平台僅供研究觀測，所有資料與標籤皆非投資建議。
</div>
""", unsafe_allow_html=True)
