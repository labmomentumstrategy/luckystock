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
    return sorted(df['TICKER'].unique().tolist())


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
    return sorted(filtered['TICKER'].unique().tolist())


@st.cache_data(ttl=3600)
def get_stock_data(ticker: str) -> pd.DataFrame:
    """取得單一股票資料"""
    df = get_all_data()
    if df.empty or 'TICKER' not in df.columns:
        return pd.DataFrame()
    return df[df['TICKER'] == ticker].sort_values('TRADE_DATE')


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
        "tags_in_5days": 0
    }
    
    if df.empty or 'TICKER' not in df.columns:
        return info

    # 過濾出該股票的資料 (確保 ticker 格式一致)
    stock_df = df[df['TICKER'].astype(str) == str(ticker)]
    
    if not stock_df.empty:
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

    # --- 以下為暫時保留的 Mock Data (未來可進階計算) ---
    info["first_tag_count_2yr"] = 8
    info["win_rate_5pct"] = 75.00
    info["no_higher_pct"] = 12.50
    info["tags_in_5days"] = 0
    
    return info

