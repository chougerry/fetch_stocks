import pandas as pd
import yfinance as yf
from datetime import datetime

# 1. 設定要追蹤的股票清單 (可自由增減)
TICKERS = [
    "2330.TW",  # 台積電
    "2317.TW",  # 鴻海
    "2454.TW",  # 聯發科
    "0050.TW",  # 元大台灣50
    "AAPL",     # 蘋果 (美股範例)
    "NVDA"      # 輝達 (美股範例)
]

def calculate_ma_diff(tickers):
    results = []
    
    # 一次下載近 6 個月資料，確保有足夠交易日計算 60MA (季線)
    data = yf.download(tickers, period="6mo", group_by="ticker", progress=False)
    
    for ticker in tickers:
        try:
            # 取得單一股票的收盤價並移除空值
            if len(tickers) == 1:
                df = data.dropna(subset=['Close']).copy()
            else:
                df = data[ticker].dropna(subset=['Close']).copy()
                
            if len(df) < 60:
                print(f"{ticker} 資料不足 60 個交易日，跳過計算。")
                continue
            
            # 計算均線
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA60'] = df['Close'].rolling(window=60).mean()
            
            # 取得最新一個交易日的數據
            latest = df.iloc[-1]
            latest_date = df.index[-1].strftime('%Y-%m-%d')
            close = float(latest['Close'])
            ma5 = float(latest['MA5'])
            ma20 = float(latest['MA20'])
            ma60 = float(latest['MA60'])
            
            # 計算 (收盤價 - 均線) / 收盤價 百分比
            diff_5_pct = ((close - ma5) / close) * 100
            diff_20_pct = ((close - ma20) / close) * 100
            diff_60_pct = ((close - ma60) / close) * 100
            
            results.append({
                "資料日期": latest_date,
                "股票代號": ticker,
                "最新收盤價": round(close, 2),
                "週線(5MA)": round(ma5, 2),
                "月線(20MA)": round(ma20, 2),
                "季線(60MA)": round(ma60, 2),
                "週線差對收盤價(%)": round(diff_5_pct, 2),
                "月線差對收盤價(%)": round(diff_20_pct, 2),
                "季線差對收盤價(%)": round(diff_60_pct, 2),
            })
        except Exception as e:
            print(f"處理 {ticker} 時發生錯誤: {e}")

    # 轉成 DataFrame 並存成 CSV (使用 utf-8-sig 確保 Excel 開啟中文不亂碼)
    result_df = pd.DataFrame(results)
    result_df.to_csv("stock_ma_diff.csv", index=False, encoding="utf-8-sig")
    print(f"[{datetime.now()}] 成功更新 stock_ma_diff.csv，共 {len(result_df)} 檔股票。")

if __name__ == "__main__":
    calculate_ma_diff(TICKERS)
