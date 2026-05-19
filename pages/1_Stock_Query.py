"""
VMR 觀察站 - 個股 K 線圖
PRO VERSION DEMO
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.gsheet import get_ticker_list, get_stock_data, get_stock_info, get_ticker_name_mapping
from utils.gsheet import get_cb_ids_by_ticker, get_cb_daily_data
from utils.analytics import track_page_view, track_event
from utils.ui import load_css, render_sidebar

# --- Page Configuration (MUST be first st.* call) ---
st.set_page_config(
    page_title="Stock Scanner | VMR Observatory",
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

# Layout: Ticker Select + Score Cards
tickers = get_ticker_list()
ticker_to_name, name_to_ticker, stock_names = get_ticker_name_mapping()

# Initialize session state for synced dropdowns
if "ticker_selector" not in st.session_state:
    st.session_state.ticker_selector = tickers[0] if tickers else None
if "name_selector" not in st.session_state:
    st.session_state.name_selector = ticker_to_name.get(tickers[0], "") if tickers else None

def on_ticker_change():
    t = st.session_state.ticker_selector
    st.session_state.name_selector = ticker_to_name.get(t, "")
    track_event("Stock_Search", {"search_type": "by_ticker", "ticker": t})

def on_name_change():
    n = st.session_state.name_selector
    st.session_state.ticker_selector = name_to_ticker.get(n, "")
    track_event("Stock_Search", {"search_type": "by_name", "stock_name": n})

filter_cols = st.columns([1.5, 1.5, 1.2])

with filter_cols[0]:
    if tickers:
        st.selectbox(
            "Ticker", 
            tickers, 
            key="ticker_selector",
            on_change=on_ticker_change
        )
    else:
        st.warning("No data")

with filter_cols[1]:
    if stock_names:
        st.selectbox(
            "Stock Name", 
            stock_names, 
            key="name_selector",
            on_change=on_name_change
        )

with filter_cols[2]:
    timeframe_val = st.select_slider(
        "Timeframe",
        options=[0, 1, 2, 3],
        value=0,
        format_func=lambda x: "All" if x == 0 else f"{x} Year" if x == 1 else f"{x} Years"
    )

selected_ticker = st.session_state.ticker_selector

if selected_ticker:
    info = get_stock_info(selected_ticker)
    
    # Score cards in a new row
    score_cols = st.columns(5)
    
    with score_cols[0]:
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Latest Price Date</div>
<div class="card-value">{info['latest_price_date']}</div>
</div>""", unsafe_allow_html=True)
        
    with score_cols[1]:
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Industry</div>
<div class="card-value">{info['industry']}</div>
</div>""", unsafe_allow_html=True)

    with score_cols[2]:
        tags_5d = info.get('tags_in_5days', 0)
        val_class = " val-accent" if tags_5d >= 5 else ""
        color_attr = ' style="color: #FF0000;"' if 3 <= tags_5d <= 4 else ""
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Tags in 5 Days</div>
<div class="card-value{val_class}"{color_attr}>{tags_5d}</div>
</div>""", unsafe_allow_html=True)

    with score_cols[3]:
        tags_10d = info.get('tags_in_10days', 0)
        val_class_10 = " val-accent" if tags_10d >= 10 else ""
        color_attr_10 = ' style="color: #FF0000;"' if 6 <= tags_10d <= 9 else ""
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Tags in 10 Days</div>
<div class="card-value{val_class_10}"{color_attr_10}>{tags_10d}</div>
</div>""", unsafe_allow_html=True)

    with score_cols[4]:
        tags_20d = info.get('tags_in_20days', 0)
        val_class_20 = " val-accent" if tags_20d >= 15 else ""
        color_attr_20 = ' style="color: #FF0000;"' if 10 <= tags_20d <= 14 else ""
        st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Tags in 20 Days</div>
<div class="card-value{val_class_20}"{color_attr_20}>{tags_20d}</div>
</div>""", unsafe_allow_html=True)



    # --- Chart ---
    df = get_stock_data(selected_ticker)
    
    if not df.empty:
        stock_date_max = df['TRADE_DATE'].max()
        stock_date_min = df['TRADE_DATE'].min()
        
        # Apply Timeframe logic
        if timeframe_val > 0:
            calculated_min = stock_date_max - pd.DateOffset(years=timeframe_val)
            stock_date_min = max(stock_date_min, calculated_min)
            
        # Determine max volume within visible range for Y-axis scaling
        visible_df = df[(df['TRADE_DATE'] >= stock_date_min) & (df['TRADE_DATE'] <= stock_date_max)]
        visible_volume_max = visible_df['VOLUME'].max() if not visible_df.empty else df['VOLUME'].max()

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
        ), secondary_y=False)
        
        # 2. Candlestick Chart (OHLC) - TradingView style
        fig.add_trace(go.Candlestick(
            x=df['TRADE_DATE'],
            open=df['OPEN'],
            high=df['HIGH'],
            low=df['LOW'],
            close=df['CLOSE'],
            increasing_line_color='#00d4aa',
            increasing_fillcolor='#00d4aa',
            decreasing_line_color='#ff6b35',
            decreasing_fillcolor='#ff6b35',
            name='OHLC',
        ), secondary_y=True)
        
        # 2b. Moving Averages
        ma_config = [
            (21,  '#ef5350', '21 MA'),   # soft red
            (144, '#66bb6a', '144 MA'),   # emerald green
            (55, '#ffca28', '55 MA'),   # amber gold
        ]
        for period, color, label in ma_config:
            if len(df) >= period:
                ma_series = df['CLOSE'].rolling(window=period).mean()
                fig.add_trace(go.Scatter(
                    x=df['TRADE_DATE'],
                    y=ma_series,
                    mode='lines',
                    name=label,
                    line=dict(color=color, width=1.2),
                    hovertemplate=f'{label}: ' + '%{y:.2f}<extra></extra>',
                ), secondary_y=True)
        
        # 3. FIRST_SIGNAL Markers → Yellow Vertical Lines
        if 'FIRST_SIGNAL' in df.columns:
            signal_df = df[df['FIRST_SIGNAL'] == 1]
            if not signal_df.empty:
                for _, row in signal_df.iterrows():
                    fig.add_vline(
                        x=row['TRADE_DATE'].timestamp() * 1000,
                        line_width=2,
                        line_dash="solid",
                        line_color="rgba(255, 0, 0, 0.9)",
                        annotation_text="",
                    )
                
                # Add invisible scatter for legend entry
                fig.add_trace(go.Scatter(
                    x=[signal_df['TRADE_DATE'].iloc[0]],
                    y=[signal_df['HIGH'].iloc[0]],
                    mode='markers',
                    marker=dict(size=0.1, color='#FF0000'),
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
            margin=dict(l=50, r=50, t=30, b=50)
        )
        
        # Y-axis styling (Price on the Right)
        fig.update_yaxes(
            title_text="Price",
            showgrid=True,
            gridcolor='rgba(42,46,57,0.5)',
            gridwidth=1,
            title_font=dict(size=12, color="#ffffff"),
            tickfont=dict(size=10, color="#ffffff"),
            side="right",
            secondary_y=True
        )
        
        # Y-axis styling (Volume on the Left)
        fig.update_yaxes(
            title_text="Volume",
            showgrid=False,
            range=[0, visible_volume_max * 4],
            title_font=dict(size=12, color="#ffffff"),
            tickfont=dict(size=10, color="#ffffff"),
            side="left",
            secondary_y=False
        )
        
        # X-axis styling
        fig.update_xaxes(
            showgrid=True,
            gridcolor='rgba(42,46,57,0.5)',
            gridwidth=1,
            tickfont=dict(size=10, color="#ffffff"),
            range=[stock_date_min, stock_date_max],
            rangebreaks=[dict(bounds=["sat", "mon"])]  # skip weekends
        )
        
        st.plotly_chart(fig, width="stretch")

    else:
        st.error(f"Failed to load data for {selected_ticker}")

    # =========================================================
    # Convertible Bond (CB) Section
    # =========================================================
    st.markdown("### 🔄 Convertible Bond")

    cb_ids = get_cb_ids_by_ticker(selected_ticker)

    if cb_ids:
        # --- CB Cards Row 1 ---
        cb_cols1 = st.columns(5)
        
        with cb_cols1[0]:
            selected_cb = st.selectbox(
                "CB ID",
                cb_ids,
                index=0,
                key="cb_id_selector"
            )

        # Fetch and process data before rendering the other cards
        cb_df = get_cb_daily_data(selected_cb)
        
        # Initialize default values
        v_cb_price = "--"
        v_conv_val = "--"
        v_conv_prem = "--"
        v_due_date = "--"
        v_conv_rate = "--"
        v_rem_days = "--"
        v_issue_amt = "--"
        cb_name = ""

        if not cb_df.empty:
            if 'CB_NAME' in cb_df.columns:
                cb_name = cb_df['CB_NAME'].iloc[0]
                
            # Filter CB data to stock date range for the chart and latest data
            if not df.empty:
                cb_df = cb_df[
                    (cb_df['TRADE_DATE'] >= stock_date_min) &
                    (cb_df['TRADE_DATE'] <= stock_date_max)
                ]
            
            if not cb_df.empty:
                # Add display column for chart
                if 'CONVERTED_PERCENTAGE' in cb_df.columns:
                    cb_df['UNCONVERTED_PCT_DISPLAY'] = (1 - cb_df['CONVERTED_PERCENTAGE']) * 100

                # Get latest row for score cards
                latest_row = cb_df.loc[cb_df['TRADE_DATE'].idxmax()]
                
                if 'REFERENCE_PRICE' in latest_row and pd.notna(latest_row['REFERENCE_PRICE']):
                    v_cb_price = f"{latest_row['REFERENCE_PRICE']:.2f}"
                if 'CONVERSION_VALUE' in latest_row and pd.notna(latest_row['CONVERSION_VALUE']):
                    v_conv_val = f"{latest_row['CONVERSION_VALUE']:.2f}"
                if 'CONVERSION_PREMIUM_RATE' in latest_row and pd.notna(latest_row['CONVERSION_PREMIUM_RATE']):
                    v_conv_prem = f"{latest_row['CONVERSION_PREMIUM_RATE']*100:.2f}%"
                if 'DUE_DATE_OF_CONVERSION' in latest_row and pd.notna(latest_row['DUE_DATE_OF_CONVERSION']):
                    try:
                        v_due_date = latest_row['DUE_DATE_OF_CONVERSION'].strftime('%Y-%m-%d')
                    except:
                        v_due_date = str(latest_row['DUE_DATE_OF_CONVERSION'])[:10]
                if 'CONVERTED_PERCENTAGE' in latest_row and pd.notna(latest_row['CONVERTED_PERCENTAGE']):
                    v_conv_rate = f"{latest_row['CONVERTED_PERCENTAGE']*100:.2f}%"
                if 'REMAINING_DAYS' in latest_row and pd.notna(latest_row['REMAINING_DAYS']):
                    v_rem_days = str(int(latest_row['REMAINING_DAYS']))
                if 'ISSUANCE_AMOUNT' in latest_row and pd.notna(latest_row['ISSUANCE_AMOUNT']):
                    try:
                        v_issue_amt = f"{float(latest_row['ISSUANCE_AMOUNT']) / 1e9:,.2f} B"
                    except:
                        v_issue_amt = str(latest_row['ISSUANCE_AMOUNT'])

        with cb_cols1[1]:
            st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">CB Price</div>
<div class="card-value">{v_cb_price}</div>
</div>""", unsafe_allow_html=True)

        with cb_cols1[2]:
            st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Conversion Value</div>
<div class="card-value">{v_conv_val}</div>
</div>""", unsafe_allow_html=True)

        with cb_cols1[3]:
            st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Conversion Premium</div>
<div class="card-value">{v_conv_prem}</div>
</div>""", unsafe_allow_html=True)

        with cb_cols1[4]:
            st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Due Date of Conv</div>
<div class="card-value">{v_due_date}</div>
</div>""", unsafe_allow_html=True)

        # --- CB Cards Row 2 ---
        cb_cols2 = st.columns(5)
        
        with cb_cols2[0]:
            st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Conversion Rate</div>
<div class="card-value">{v_conv_rate}</div>
</div>""", unsafe_allow_html=True)
            
        with cb_cols2[1]:
            st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Remaining Days</div>
<div class="card-value">{v_rem_days}</div>
</div>""", unsafe_allow_html=True)
            
        with cb_cols2[2]:
            st.markdown(f"""
<div class="stock-info-card">
<div class="card-label">Issue Amount</div>
<div class="card-value">{v_issue_amt}</div>
</div>""", unsafe_allow_html=True)

        if not cb_df.empty and 'UNCONVERTED_PCT_DISPLAY' in cb_df.columns:

            fig_cb = make_subplots(specs=[[{"secondary_y": True}]])
            fig_cb.add_trace(go.Bar(
                x=cb_df['TRADE_DATE'],
                y=cb_df['UNCONVERTED_PCT_DISPLAY'],
                marker=dict(
                    color=cb_df['UNCONVERTED_PCT_DISPLAY'],
                    colorscale=[
                        [0.0, '#ff6b35'],
                        [0.3, '#ffca28'],
                        [0.6, '#66bb6a'],
                        [0.8, '#00bcd4'],
                        [1.0, '#1a237e']
                    ],
                    line=dict(width=0)
                ),
                name='Unconverted %',
                showlegend=False,
                hovertemplate='Date: %{x|%Y-%m-%d}<br>Unconverted: %{y:.2f}%<extra></extra>',
            ), secondary_y=False)

            # Add CB Price (REFERENCE_PRICE) on secondary Y-axis
            if 'REFERENCE_PRICE' in cb_df.columns:
                fig_cb.add_trace(go.Scatter(
                    x=cb_df['TRADE_DATE'],
                    y=cb_df['REFERENCE_PRICE'],
                    mode='lines',
                    name='CB Price',
                    line=dict(color='#ffffff', width=2),
                    hovertemplate='CB Price: %{y:.2f}<extra></extra>',
                    showlegend=False
                ), secondary_y=True)

            fig_cb.update_layout(
                title=dict(
                    text=f"{selected_cb} {cb_name} — Unconverted (%) & CB Price",
                    font=dict(size=14, color="#ffffff")
                ),
                height=380,
                template="plotly_dark",
                paper_bgcolor="#0a0e17",
                plot_bgcolor="#0a0e17",
                hovermode='x unified',
                font=dict(family="JetBrains Mono"),
                margin=dict(l=50, r=50, t=50, b=50),
                bargap=0.15
            )

            fig_cb.update_xaxes(
                showgrid=True,
                gridcolor='rgba(42,46,57,0.5)',
                gridwidth=1,
                tickfont=dict(size=10, color="#ffffff"),
                range=[stock_date_min, stock_date_max] if not df.empty else None,
                rangebreaks=[dict(bounds=["sat", "mon"])]  # skip weekends
            )

            # Left Y-axis: Unconverted %
            fig_cb.update_yaxes(
                title_text="Unconverted %",
                showgrid=True,
                gridcolor='rgba(42,46,57,0.5)',
                gridwidth=1,
                title_font=dict(size=12, color="#ffffff"),
                tickfont=dict(size=10, color="#ffffff"),
                ticksuffix="%",
                range=[0, 100],
                side="left",
                secondary_y=False
            )

            # Right Y-axis: CB Price
            fig_cb.update_yaxes(
                title_text="CB Price",
                showgrid=False,
                showticklabels=True,
                title_font=dict(size=12, color="#ffffff"),
                tickfont=dict(size=10, color="#ffffff"),
                side="right",
                secondary_y=True
            )

            st.plotly_chart(fig_cb, use_container_width=True)
        else:
            st.info(f"No CONVERTED_PERCENTAGE data for {selected_cb}")
    else:
        st.info(f"No convertible bonds found for ticker {selected_ticker}")
else:
    st.info("👈 Select a stock from the dropdown above to begin analysis.")
