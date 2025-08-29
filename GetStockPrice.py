import requests
import yfinance as yf
from datetime import datetime

# ✅ 你的 LINE Channel Access Token（勿洩漏給他人）
CHANNEL_ACCESS_TOKEN = '?'

# ✅ 股票清單（可加更多）
symbols = ["2330.TW", "2317.TW", "0050.TW", "0056.TW"]


def get_today_close_prices():
    result_lines = []
    today = datetime.today().strftime('%Y/%m/d%d')

    # 抓取近兩天資料（收盤價已調整）
    data = yf.download(symbols, period="3d", interval="1d", auto_adjust=True)
    data2 = yf.download(symbols, period="45d", interval="1d", auto_adjust=True)

    if data.empty and data2.empty:
        return "⚠️ 查無資料（可能是假日或未開盤）"

    result_lines.append(f"📅 台股今日（{today}）收盤價與漲跌：")

    for symbol in symbols:
        try:
            close_today = data["Close"][symbol].iloc[-1]
            close_prev = data["Close"][symbol].iloc[-2]

            diff = close_today - close_prev
            percent = (diff / close_prev) * 100 if close_prev != 0 else 0

            if diff > 0:
                change = f"⬆️+{diff:.2f}（+{percent:.2f}%）"
            elif diff < 0:
                change = f"⬇️{diff:.2f}（{percent:.2f}%）"
            else:
                change = "➖ 無變化"

            close_series = data2["Close"][symbol].dropna()
            if len(close_series) < 35:
                result_lines.append(f"⚠️{symbol} 資料不足，無法計算 MACD")
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

            result_lines.append(f"🔹 {symbol}：{close_today:.2f} 元（{change}）\n MACD 訊號：{signal}")

        except Exception as e:
            result_lines.append(f"⚠️ {symbol} 錯誤：{e}")

    return "\n".join(result_lines)

def calculate_macd(close_series):
    ema12 = close_series.ewm(span=12).mean()
    ema26 = close_series.ewm(span=26).mean()
    dif = ema12 - ema26
    macd = dif.ewm(span=9).mean()
    histogram = dif - macd
    return dif, macd, histogram

# def show_macd_status():
#     today = datetime.today().strftime('%Y-%m-%d')
#     result_lines = [f"📊 MACD 指標狀態（{today}）："]
#
#     data2 = yf.download(symbols, period="45d", interval="1d", auto_adjust=True)
#
#     for symbol in symbols:
#         try:
#             close_series = data2["Close"][symbol].dropna()
#             if len(close_series) < 35:
#                 result_lines.append(f"⚠️ {symbol} 資料不足，無法計算 MACD")
#                 continue
#
#             dif, macd_line, hist = calculate_macd(close_series)
#             dif_now = dif.iloc[-1]
#             macd_now = macd_line.iloc[-1]
#             hist_now = hist.iloc[-1]
#
#             if dif_now > macd_now:
#                 signal = "📈 黃金交叉（多頭）"
#             elif dif_now < macd_now:
#                 signal = "📉 死亡交叉（空頭）"
#             else:
#                 signal = "➖ 無交叉"
#
#             result_lines.append(
#                 f"🔹 {symbol} MACD 訊號：{signal}"
#                 #f"　MACD 訊號：{signal}"
#                 #f"　DIF = {dif_now:.2f}, MACD = {macd_now:.2f}, 柱狀圖 = {hist_now:+.2f}"
#             )
#
#         except Exception as e:
#             result_lines.append(f"⚠️ {symbol} 發生錯誤：{e}")
#
#     return "\n".join(result_lines)


def send_line_broadcast(message_text):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    body = {
        'messages': [{
            'type': 'text',
            'text': message_text
        }]
    }

    response = requests.post(url, headers=headers, json=body)
    print("✅ 廣播結果:", response.status_code, response.text)

# ✅ 執行
message = get_today_close_prices()
send_line_broadcast(message)

print(message)

