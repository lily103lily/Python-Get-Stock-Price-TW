import yfinance as yf
from datetime import datetime

# ✅ 股票清單（可自由增減）
symbols = ["2330.TW", "0050.TW", "0056.TW"]

def calculate_macd(close_series):
    ema12 = close_series.ewm(span=12).mean()
    ema26 = close_series.ewm(span=26).mean()
    dif = ema12 - ema26
    macd = dif.ewm(span=9).mean()
    histogram = dif - macd
    return dif, macd, histogram

def show_macd_status():
    today = datetime.today().strftime('%Y-%m-%d')
    result_lines = [f"📊 MACD 指標狀態（{today}）："]

    data = yf.download(symbols, period="45d", interval="1d", auto_adjust=True)

    for symbol in symbols:
        try:
            close_series = data["Close"][symbol].dropna()
            if len(close_series) < 35:
                result_lines.append(f"⚠️ {symbol} 資料不足，無法計算 MACD")
                continue

            dif, macd_line, hist = calculate_macd(close_series)
            dif_now = dif.iloc[-1]
            macd_now = macd_line.iloc[-1]
            hist_now = hist.iloc[-1]

            if dif_now > macd_now:
                signal = "📈 黃金交叉（多頭）"
            elif dif_now < macd_now:
                signal = "📉 死亡交叉（空頭）"
            else:
                signal = "➖ 無交叉"

            result_lines.append(
                f"\n🔹 {symbol}\n"
                f"　MACD 訊號：{signal}\n"
                f"　DIF = {dif_now:.2f}, MACD = {macd_now:.2f}, 柱狀圖 = {hist_now:+.2f}"
            )

        except Exception as e:
            result_lines.append(f"⚠️ {symbol} 發生錯誤：{e}")

    return "\n".join(result_lines)


# ✅ 執行
message = show_macd_status()
print(message)
print(type(message))