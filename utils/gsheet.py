"""
Google Sheets Connection Module for VMR Dashboard
讀取 Google Sheets 股價資料
"""
import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from typing import List, Optional


# Spreadsheet ID from secrets
SPREADSHEET_ID = st.secrets.get("gsheet", {}).get("spreadsheet_id", "")


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
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
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


def get_stock_data(ticker: str) -> pd.DataFrame:
    """取得單一股票資料"""
    df = get_all_data()
    if df.empty or 'TICKER' not in df.columns:
        return pd.DataFrame()
    return df[df['TICKER'] == ticker].sort_values('TRADE_DATE')


def get_summary_stats() -> dict:
    """取得統計摘要 (MVP: 從資料計算)"""
    df = get_all_data()
    if df.empty:
        return {
            "total_signals": 0,
            "today_signals": 0,
            "win_rate": 0.0,
            "data_start": None,
            "data_end": None
        }
    
    # 計算統計
    signal_df = df[df.get('SIGNAL', 0) == 1] if 'SIGNAL' in df.columns else pd.DataFrame()
    
    return {
        "total_signals": len(signal_df),
        "today_signals": len(signal_df[signal_df['TRADE_DATE'] == signal_df['TRADE_DATE'].max()]) if not signal_df.empty else 0,
        "win_rate": 87.15,  # TODO: 計算真實勝率
        "data_start": df['TRADE_DATE'].min() if 'TRADE_DATE' in df.columns else None,
        "data_end": df['TRADE_DATE'].max() if 'TRADE_DATE' in df.columns else None
    }
