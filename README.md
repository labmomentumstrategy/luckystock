# VMR 觀察站 | VMR Observatory

📡 量價動能觀測平台 (Volume-Momentum-Radar)

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定 Credentials

複製 `secrets.toml.template` 到 `.streamlit/secrets.toml`：

```bash
cp secrets.toml.template .streamlit/secrets.toml
```

然後編輯 `.streamlit/secrets.toml` 填入：
- Google Service Account JSON 內容
- Google Sheets ID
- GA4 Measurement ID (可選)

### 3. 執行

```bash
streamlit run app.py
```

開啟瀏覽器：http://localhost:8501

## 專案結構

```
luckystock/
├── app.py                    # 首頁
├── pages/
│   └── 1_📈_Stock.py         # 個股 K 線頁
├── utils/
│   └── gsheet.py             # GSheet 連線模組
├── .streamlit/
│   ├── config.toml           # Theme 設定
│   └── secrets.toml          # 憑證 (不上傳)
└── requirements.txt
```

## 免責聲明

本平台僅供研究觀測用途，所有資料與標籤皆非投資建議。
