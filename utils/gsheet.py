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


@st.cache_data(ttl=600)  # 快取 10 分鐘
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


@st.cache_data(ttl=600)
def get_ticker_list() -> List[str]:
    """取得所有股票代號"""
    df = get_all_data()
    if df.empty or 'TICKER' not in df.columns:
        return []
    return sorted(df['TICKER'].unique().tolist())


@st.cache_data(ttl=600)
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
    TODO: 未來從另一個 Google Sheet 讀取，目前回傳 Dummy Data
    """
    return {
        "stock_name": "康恩貝",
        "industry": "中藥",
        "latest_price_date": "2026-01-30",
        "first_tag_count_2yr": 8,
        "win_rate_5pct": 75.00,
        "no_higher_pct": 12.50,
        "tags_in_5days": 0
    }

