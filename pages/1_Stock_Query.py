"""
VMR 觀察站 - 個股 K 線圖
PRO VERSION DEMO
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.gsheet import get_ticker_list, get_stock_data, get_stock_info
from utils.analytics import track_page_view
from utils.ui import load_css, render_sidebar

# --- Page Configuration (MUST be first st.* call) ---
st.set_page_config(
    page_title="個股 K 線圖 | VMR 觀察站",
    page_icon="📈",
    layout="wide"
)

# --- Server-Side Tracking ---
track_page_view("Individual Stock", page_path="/stock")

# --- Load Custom CSS ---
load_css()

# --- Sidebar (Modular) ---
render_sidebar()

# --- Main Area ---
st.markdown("### 📈 Stock Scanner")

# Row 1: Ticker Filter (col1) + Score Cards (col2-4)
tickers = get_ticker_list()
col1, col2, col3, col4 = st.columns(4)
with col1:
    if tickers:
        selected_ticker = st.selectbox("Ticker | 股票代號", tickers, index=0)
    else:
        st.warning("No data")
        selected_ticker = None

# Score Cards (using get_stock_info dummy data)
if selected_ticker:
    info = get_stock_info(selected_ticker)
    
    # Fill remaining cols in Row 1
    with col2:
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Stock Name</div>
<div class="card-value">{info['stock_name']}</div>
<div class="card-sub">股票名稱</div>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Industry</div>
<div class="card-value">{info['industry']}</div>
<div class="card-sub">行業板塊</div>
</div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Latest Price Date</div>
<div class="card-value">{info['latest_price_date']}</div>
<div class="card-sub">最新價格日</div>
</div>""", unsafe_allow_html=True)

    # Row 2: Performance Metrics
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Tags in Past 2yrs</div>
<div class="card-value val-accent">{info['first_tag_count_2yr']}</div>
<div class="card-sub">過去兩年訊號次數</div>
</div>""", unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Win Rate (&gt;5%)</div>
<div class="card-value val-accent">{info['win_rate_5pct']}%</div>
<div class="card-sub">訊號後上漲&gt;5%機率</div>
</div>""", unsafe_allow_html=True)
    with col7:
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">No Higher Price %</div>
<div class="card-value">{info['no_higher_pct']}%</div>
<div class="card-sub">訊號後沒有更高機率</div>
</div>""", unsafe_allow_html=True)
    with col8:
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Tags in 5 Days</div>
<div class="card-value">{info['tags_in_5days']}</div>
<div class="card-sub">近五個交易日標籤數</div>
</div>""", unsafe_allow_html=True)

    # --- Chart ---
    df = get_stock_data(selected_ticker)
    
    if not df.empty:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 1. Volume Bar Chart (behind the line)
        colors = ['rgba(0,212,170,0.3)' if df['CLOSE'].iloc[i] >= df['CLOSE'].iloc[i-1] 
                  else 'rgba(255,107,53,0.3)' for i in range(1, len(df))]
        colors.insert(0, 'rgba(0,212,170,0.3)')
        
        volume = df['VOLUME']
        fig.add_trace(go.Bar(
            x=df['TRADE_DATE'],
            y=volume,
            marker=dict(color=colors, line=dict(width=0)),
            name="Volume",
            hovertemplate='Vol: %{y:,.0f}<extra></extra>',
            opacity=0.5
        ), secondary_y=True)
        
        # 2. Line Chart (HIGH price)
        fig.add_trace(go.Scatter(
            x=df['TRADE_DATE'],
            y=df['HIGH'],
            mode='lines',
            name='High Price',
            line=dict(color='#00d4aa', width=1.5),
            customdata=df[['OPEN', 'CLOSE', 'LOW']].values,
            hovertemplate=(
                'Date: %{x|%Y-%m-%d}<br>'
                'Open: %{customdata[0]:.2f}<br>'
                'High: %{y:.2f}<br>'
                'Low: %{customdata[2]:.2f}<br>'
                'Close: %{customdata[1]:.2f}'
                '<extra></extra>'
            )
        ), secondary_y=False)
        
        # 3. FIRST_SIGNAL Markers → Yellow Vertical Lines
        if 'FIRST_SIGNAL' in df.columns:
            signal_df = df[df['FIRST_SIGNAL'] == 1]
            if not signal_df.empty:
                for _, row in signal_df.iterrows():
                    fig.add_vline(
                        x=row['TRADE_DATE'].timestamp() * 1000,
                        line_width=2,
                        line_dash="solid",
                        line_color="rgba(255, 255, 0, 0.85)",
                        annotation_text="",
                    )
                
                # Add invisible scatter for legend entry
                fig.add_trace(go.Scatter(
                    x=[signal_df['TRADE_DATE'].iloc[0]],
                    y=[signal_df['HIGH'].iloc[0]],
                    mode='markers',
                    marker=dict(size=0.1, color='#ffff00'),
                    name='First Signal',
                    showlegend=True,
                    hoverinfo='skip'
                ), secondary_y=False)
        
        # 4. FOLLOWING_SIGNAL Markers → Blue Vertical Lines
        if 'FOLLOWING_SIGNAL' in df.columns:
            follow_df = df[df['FOLLOWING_SIGNAL'] == 1]
            if not follow_df.empty:
                for _, row in follow_df.iterrows():
                    fig.add_vline(
                        x=row['TRADE_DATE'].timestamp() * 1000,
                        line_width=2,
                        line_dash="solid",
                        line_color="rgba(66, 133, 244, 0.6)",
                        annotation_text="",
                    )
                
                # Add invisible scatter for legend entry
                fig.add_trace(go.Scatter(
                    x=[follow_df['TRADE_DATE'].iloc[0]],
                    y=[follow_df['HIGH'].iloc[0]],
                    mode='markers',
                    marker=dict(size=0.1, color='#4285f4'),
                    name='Following Signal',
                    showlegend=True,
                    hoverinfo='skip'
                ), secondary_y=False)
        
        # Layout Customization
        fig.update_layout(
            height=550,
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            paper_bgcolor="#0a0e17",
            plot_bgcolor="#0a0e17",
            hovermode='x unified',
            font=dict(family="JetBrains Mono"),
            legend=dict(orientation="h", y=1.02, x=0, xanchor="left", yanchor="bottom"),
            margin=dict(l=50, r=50, t=30, b=50),
            title=dict(text=f"{selected_ticker} Price Action", x=0.5, font=dict(size=16))
        )
        
        # Y-axis styling
        fig.update_yaxes(
            title_text="High Price",
            showgrid=True,
            gridcolor='rgba(42,46,57,0.5)',
            gridwidth=1,
            title_font=dict(size=12, color="#6b7280"),
            tickfont=dict(size=10, color="#6b7280"),
            secondary_y=False
        )
        
        fig.update_yaxes(
            title_text="Volume",
            showgrid=False,
            range=[0, volume.max() * 4],
            secondary_y=True
        )
        
        # X-axis styling
        fig.update_xaxes(
            showgrid=True,
            gridcolor='rgba(42,46,57,0.5)',
            gridwidth=1,
            tickfont=dict(size=10, color="#6b7280")
        )
        
        st.plotly_chart(fig, width="stretch")
        
        # --- Signal History Table ---
        if 'FIRST_SIGNAL' in df.columns:
            signal_df = df[df['FIRST_SIGNAL'] == 1].copy()
            if not signal_df.empty:
                st.subheader("📊 Signal History")
                display_df = signal_df[['TRADE_DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE']].copy()
                display_df.columns = ['Date', 'Open', 'High', 'Low', 'Close']
                display_df['Date'] = display_df['Date'].dt.date
                display_df = display_df.sort_values('Date', ascending=False).head(10)
                st.dataframe(
                    display_df, 
                    width="stretch",
                    hide_index=True
                )
    else:
        st.error(f"Failed to load data for {selected_ticker}")
else:
    st.info("👈 Select a stock from the dropdown above to begin analysis.")
