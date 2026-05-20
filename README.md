# CB Observatory | Convertible Bond Scanner & Stock Query

📡 **CB Observatory** is a premium, automated data-driven observation dashboard designed to track market-wide Convertible Bond (CB) dynamics and CB signals in real-time. Built with a sleek Cyberpunk HUD aesthetic, this platform empowers quantitative traders and analysts to spot institutional convertible bond flows, conversions, and CB price action signals instantly.

---

## 🚀 Key Features

### 1. Market-Wide CB Scanner (Home Page)
*   **Dynamic Sliders**: Multi-dimensional filtering across key metrics including:
    *   *Reference Price* & *Conversion Value*
    *   *Converted Percentage (%)*
    *   *Remaining Days* to maturity
    *   *Listed Days* (calculated dynamically from conversion initiation dates)
*   **Interactive Data Grid**: Streamlined table supporting single-row highlighting for in-depth comparative analysis.
*   **One-Click Export**: Easily download filtered CB scanner datasets as a standard CSV format (pre-encoded with `utf-8-sig` for seamless Excel compatibility).

### 2. Stock Scanner (Individual Stock Query Page)
*   **Advanced Charting**: A customized Plotly visualization pane featuring:
    *   *OHLC Candlestick Charts* with clear color-coded price action.
    *   *Multi-Period Moving Averages* (21 MA, 55 MA, and 144 MA).
    *   *Volume Bars* layered behind price action.
    *   *CB Signals* mapped as bright vertical markers (Red for **First Signals**, Blue for **Following Signals**) indicating key institutional momentum entry points.
*   **Tickers Mapping**: Seamless dual-synchronization selector allows searching by either Ticker Symbol or Stock Name.
*   **Trend Score Cards**: Key metrics at a glance, highlighting ticker industry, latest update dates, and short-to-medium CB signal counts (5-day, 10-day, and 20-day signal frequency).

### 3. Convertible Bond Deep-Dive Analysis
*   **Dual-Axis Visualization**: Track the relationship between CB Price and **Unconverted Percentage (%)** over the stock's corresponding timeline.
*   **CB Financial Metrics**: Comprehensive scorecards tracking CB Price, Conversion Value, Conversion Premium rate, Due Date, Conversion Rate, Remaining Days, and total Issuance Amount.

### 4. Telegram VIP Channel Integration
*   Real-time automated webhook alerts streaming convertible bond spikes, conversion activities, and sudden drops in unconverted CB percentages straight to subscription channels.

### 5. Cyberpunk HUD UI/UX Style
*   Immersive visual aesthetics leveraging dark glassmorphism, responsive grid systems, vibrant neon accents, JetBrains Mono font face, and interactive CRT scanline overlay.

---

## 📂 Project Architecture

```
luckystock/
├── app.py                      # CB Scanner Dashboard (Home Page)
├── pages/
│   ├── 1_Stock_Query.py        # Stock Scanner & CB Deep-Dive Page
│   └── 2_Telegram_Channel.py   # Telegram VIP Channel Info Page
├── utils/
│   ├── __init__.py             # Module initialization
│   ├── gsheet.py               # Google Sheets cache & retrieval module (CB Dashboard)
│   ├── ui.py                   # Central UI styling, navigation & RAM monitoring
│   ├── analytics.py            # GA4 Server-Side event logging & page tracking
│   └── system.py               # Operating system resource utility
├── assets/
│   └── style.css               # Central stylesheet (HUD styling, effects & animations)
├── .streamlit/
│   ├── config.toml             # Streamlit environment & theme parameters
│   └── secrets.toml            # Sensitive credentials (excluded from version control)
├── requirements.txt            # Python library dependencies
├── secrets.toml.template       # Template configuration file for secrets
└── .gitignore                  # Git tracking exclusion list
```

---

## 🛠️ Tech Stack
*   **Framework**: Streamlit (v1.30.0+)
*   **Data Processing**: Pandas (v2.0.0+)
*   **Visualization**: Plotly (v5.18.0+)
*   **Database Connectivity**: Google Sheets API (`gspread`, `google-auth`)
*   **Analytics**: Server-side Google Analytics 4 (GA4) tracker

---

## ⏱️ Quick Start

### 1. Prerequisites Installation
Ensure you have Python 3.9+ installed. Run the command below to install all necessary packages in your virtual environment:
```bash
pip install -r requirements.txt
```

### 2. Configure Credentials & Secrets
To connect to the backend Google Sheet data source, copy the credentials template:
```bash
cp secrets.toml.template .streamlit/secrets.toml
```
Open `.streamlit/secrets.toml` and populate the placeholders with your secure credentials:
*   **`[gcp_service_account]`**: Paste your GCP Service Account JSON details.
*   **`[gsheet]`**: Fill in your `spreadsheet_id` and `cb_spreadsheet_id`.
*   **`[ga4]`**: Add your GA4 Measurement ID (optional for local deployment).

> [!WARNING]
> Never commit `.streamlit/secrets.toml` to public version control systems. It is already appended to `.gitignore`.

### 3. Run the Server
Launch the Streamlit interface locally:
```bash
streamlit run app.py
```
Open your browser and navigate to: [http://localhost:8501](http://localhost:8501)

---

## ⚖️ Disclaimer
*CB Observatory is developed strictly for research and observation purposes. All indicators, signals, and charts represent historical mathematical calculations and do not constitute financial advice, buy/sell recommendations, or investment endorsements.*
