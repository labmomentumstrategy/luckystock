"""
Google Sheets Connection Module for VMR Dashboard
讀取 Google Sheets 股價資料
"""
import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from typing import List, Optional


def _get_spreadsheet_id() -> str:
    """Lazy-load Spreadsheet ID from secrets (avoids module-level st.secrets call)."""
    return st.secrets.get("gsheet", {}).get("spreadsheet_id", "")


@st.cache_resource
def get_gsheet_client():
    """取得 Google Sheets 客戶端 (使用 secrets.toml)"""
    try:
        service_account_info = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
        creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"GSheet 連線錯誤: {e}")
        return None


@st.cache_data(ttl=3600)  # 快取 1 小時 (資料為 daily refresh)
def get_all_data() -> pd.DataFrame:
    """取得所有股價資料"""
    client = get_gsheet_client()
    if not client:
        return pd.DataFrame()
    
    try:
        spreadsheet = client.open_by_key(_get_spreadsheet_id())
        worksheet = spreadsheet.get_worksheet(0)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # 轉換日期欄位
        if 'TRADE_DATE' in df.columns:
            df['TRADE_DATE'] = pd.to_datetime(df['TRADE_DATE'])
        
        return df
    except Exception as e:
        st.error(f"讀取資料錯誤: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_ticker_list() -> List[str]:
    """取得所有股票代號"""
    df = get_all_data()
    if df.empty or 'TICKER' not in df.columns:
        return []
    return sorted(df['TICKER'].astype(str).unique().tolist())


@st.cache_data(ttl=3600)
def get_ticker_name_mapping() -> tuple:
    """取得股票代號與名稱的對應表及名稱清單"""
    df = get_all_data()
    if df.empty or 'TICKER' not in df.columns or 'STOCK_NAME' not in df.columns:
        return {}, {}, []
    
    unique_df = df.drop_duplicates(subset=['TICKER'])
    
    ticker_to_name = dict(zip(unique_df['TICKER'].astype(str), unique_df['STOCK_NAME'].astype(str)))
    name_to_ticker = dict(zip(unique_df['STOCK_NAME'].astype(str), unique_df['TICKER'].astype(str)))
    
    # 建立一個乾淨的名稱清單並排序 (過濾掉 nan)
    name_list = sorted([str(name) for name in unique_df['STOCK_NAME'].unique() if pd.notna(name) and str(name).strip() != ""])
    
    return ticker_to_name, name_to_ticker, name_list


@st.cache_data(ttl=3600)
def get_ticker_list_by_exchange(exchange: str) -> List[str]:
    """
    依交易所過濾股票代號列表。

    Args:
        exchange (str): 'twse' 或 'tpex'（不區分大小寫）

    Returns:
        List[str]: 該交易所的股票代號列表（排序後）
    """
    df = get_all_data()
    if df.empty or 'TICKER' not in df.columns or 'EXCHANGE' not in df.columns:
        # EXCHANGE 欄位不存在時 fallback 到全部 ticker
        return get_ticker_list()

    filtered = df[df['EXCHANGE'].str.lower() == exchange.lower()]
    return sorted(filtered['TICKER'].astype(str).unique().tolist())


@st.cache_data(ttl=3600)
def get_stock_data(ticker: str) -> pd.DataFrame:
    """取得單一股票資料"""
    df = get_all_data()
    if df.empty or 'TICKER' not in df.columns:
        return pd.DataFrame()
    return df[df['TICKER'].astype(str) == str(ticker)].sort_values('TRADE_DATE')


def get_summary_stats() -> dict:
    """
    取得統計摘要
    TODO: 未來從 OCI 算好的 Summary Sheet 讀取，目前回傳 Mock Data 以展示 UI
    """
    # Mock Data matching the "Trust Building" requirement
    return {
        "data_range": "2021/02/04 - 2026/01/30",
        "total_signals": 16752,
        "win_count": 14600,
        "loss_count": 2152,
        "win_rate": 87.15,
        "avg_return": 13.06
    }


def get_stock_info(ticker: str) -> dict:
    """
    取得個股基本資訊 (Score Cards 用)
    從 get_all_data() 中過濾出該個股的資料並提取資訊
    """
    df = get_all_data()
    
    # 預設值 (Mock Data placeholder for calculated indicators)
    info = {
        "stock_name": "Unknown",
        "industry": "Unknown",
        "latest_price_date": "N/A",
        "first_tag_count_2yr": "--",
        "win_rate_5pct": "--",
        "no_higher_pct": "--",
        "tags_in_5days": 0,
        "tags_in_10days": 0
    }
    
    if df.empty or 'TICKER' not in df.columns:
        return info

    # 過濾出該股票的資料 (確保 ticker 格式一致)
    stock_df = df[df['TICKER'].astype(str) == str(ticker)]
    
    if not stock_df.empty:
        stock_df = stock_df.sort_values('TRADE_DATE', ascending=False)
        
        # 1. 股票名稱
        if 'STOCK_NAME' in stock_df.columns:
            val = stock_df['STOCK_NAME'].iloc[0]
            info["stock_name"] = val if pd.notna(val) else "Unknown"
        
        # 2. 行業板塊
        if 'INDUSTRY_CATEGORY' in stock_df.columns:
            val = stock_df['INDUSTRY_CATEGORY'].iloc[0]
            info["industry"] = val if pd.notna(val) else "Unknown"
            
        # 3. 最新價格日 (max TRADE_DATE)
        if 'TRADE_DATE' in stock_df.columns:
            max_date = stock_df['TRADE_DATE'].max()
            info["latest_price_date"] = max_date.strftime('%Y-%m-%d') if pd.notna(max_date) else "N/A"
            
        # 4. 近五日標籤數 (Tags in 5 Days)
        if 'FIRST_SIGNAL' in stock_df.columns and 'FOLLOWING_SIGNAL' in stock_df.columns:
            recent_5d = stock_df.head(5)
            # 計算有任何訊號的天數
            signal_count = int(((recent_5d['FIRST_SIGNAL'] == 1) | (recent_5d['FOLLOWING_SIGNAL'] == 1)).sum())
            info["tags_in_5days"] = signal_count
            
            # 5. 近十日標籤數 (Tags in 10 Days)
            recent_10d = stock_df.head(10)
            signal_count_10 = int(((recent_10d['FIRST_SIGNAL'] == 1) | (recent_10d['FOLLOWING_SIGNAL'] == 1)).sum())
            info["tags_in_10days"] = signal_count_10

    # --- 以下為暫時保留的 Mock Data (未來可進階計算) ---
    info["first_tag_count_2yr"] = 8
    info["win_rate_5pct"] = 75.00
    info["no_higher_pct"] = 12.50
    
    return info


# =====================================================
# Convertible Bond (CB) GSheet Functions
# =====================================================

def _get_cb_spreadsheet_id() -> str:
    """Lazy-load CB Spreadsheet ID from secrets."""
    return st.secrets.get("gsheet", {}).get("cb_spreadsheet_id", "")


@st.cache_data(ttl=3600)
def get_all_cb_data() -> pd.DataFrame:
    """取得所有可轉債資料 (from CB GSheet)"""
    client = get_gsheet_client()
    if not client:
        return pd.DataFrame()

    cb_sheet_id = _get_cb_spreadsheet_id()
    if not cb_sheet_id:
        st.warning("CB GSheet ID 未設定，請檢查 secrets.toml")
        return pd.DataFrame()

    try:
        spreadsheet = client.open_by_key(cb_sheet_id)
        worksheet = spreadsheet.get_worksheet(0)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        # 轉換日期欄位
        if 'TRADE_DATE' in df.columns:
            df['TRADE_DATE'] = pd.to_datetime(df['TRADE_DATE'])

        # 轉換數值欄位 (GSheet 可能回傳字串)
        numeric_cols = ['CONVERTED_PERCENTAGE', 'CONVERSION_PREMIUM_RATE',
                        'CONVERSION_VALUE', 'REFERENCE_PRICE',
                        'PRICE_OF_UNDERLYING_STOCK', 'CONVERSION_PRICE']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"讀取 CB 資料錯誤: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_cb_ids_by_ticker(ticker: str) -> List[str]:
    """
    用股票代號 fuzzy match CB_ID。
    台灣 CB 命名慣例: 股票代號 + 序號 (e.g., 2330 → 23301, 23302)
    """
    df = get_all_cb_data()
    if df.empty or 'CB_ID' not in df.columns:
        return []

    # 純數字 ticker prefix match
    ticker_str = str(ticker).strip()
    matched = df[df['CB_ID'].astype(str).str.startswith(ticker_str)]
    return sorted(matched['CB_ID'].astype(str).unique().tolist())


@st.cache_data(ttl=3600)
def get_cb_daily_data(cb_id: str) -> pd.DataFrame:
    """取得指定 CB_ID 的每日資料，依 TRADE_DATE 排序"""
    df = get_all_cb_data()
    if df.empty or 'CB_ID' not in df.columns:
        return pd.DataFrame()

    cb_df = df[df['CB_ID'].astype(str) == str(cb_id)].copy()
    if not cb_df.empty:
        cb_df = cb_df.sort_values('TRADE_DATE')
    return cb_df
