import requests
import statistics
import asyncio
import time
import csv
from datetime import datetime
from telegram import Bot

# === KONFIGURASI ===
TOKEN = "8471380538:AAH0fzS-j7lVmpXH2EYHNRfMPe1wod44GKs"
API_KEY_TWELVE = "28376ffef8a648b89624c13e636bae7a"
CHAT_ID = "6227149877"  # dapatkan dari @userinfobot

bot = Bot(token=TOKEN)

# === Ambil harga ===
def get_price(symbol):
    try:
        symbol = symbol.upper()
        if symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            data = requests.get(url, timeout=5).json()
            return float(data["price"])
        else:
            if "USD" not in symbol:
                symbol = symbol + "/USD"
            else:
                symbol = symbol.replace("USDT", "/USD")
            url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY_TWELVE}"
            data = requests.get(url, timeout=5).json()
            return float(data["price"]) if "price" in data else None
    except Exception as e:
        print(f"⚠️ Error ambil harga {symbol}:", e)
        return None

# === Ambil data candle ===
def get_candles(symbol, limit=10):
    try:
        symbol = symbol.upper()
        if symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit={limit}"
            data = requests.get(url, timeout=5).json()
            return [float(c[4]) for c in data]
        else:
            if "USD" not in symbol:
                symbol = symbol + "/USD"
            else:
                symbol = symbol.replace("USDT", "/USD")
            url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize={limit}&apikey={API_KEY_TWELVE}"
            data = requests.get(url, timeout=5).json()
            if "values" in data:
                return [float(v["close"]) for v in data["values"][::-1]]
            return []
    except Exception as e:
        print(f"⚠️ Error ambil candle {symbol}:", e)
        return []

# === Hitung sinyal ===
def generate_signal(prices):
    if not prices or len(prices) < 3:
        return None

    current = prices[-1]
    prev = prices[-2]
    ma_short = sum(prices[-3:]) / 3
    ma_long = statistics.mean(prices)
    change = ((current - prev) / prev) * 100

    tp_percent = 0.3 / 100
    sl_percent = 0.2 / 100
    tp = current + (current * tp_percent)
    sl = current - (current * sl_percent)

    if change > 0.01 and ma_short > ma_long:
        return ("BUY", current, tp, sl, change)
    elif change < -0.01 and ma_short < ma_long:
        tp = current - (current * tp_percent)
        sl = current + (current * sl_percent)
        return ("SELL", current, tp, sl, change)
    else:
        return ("WAIT", current, tp, sl, change)

# === Simpan log ke file ===
def log_signal(symbol, signal_data):
    signal, price, tp, sl, change = signal_data
    with open("signal_log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            signal,
            round(price, 4),
            round(tp, 4),
            round(sl, 4),
            f"{change:.4f}%"
        ])

# === Kirim sinyal ke Telegram ===
async def send_signal(symbol, signal_data, last_signal):
    signal, price, tp, sl, change = signal_data
    if signal != last_signal.get(symbol):
        message = f"💹 *{symbol}*\nHarga: ${price:,.2f}\nPerubahan: {change:.2f}%\n"
        if signal == "BUY":
            message += f"\n📈 *BUY Signal*\n🎯 TP: ${tp:,.2f}\n🛑 SL: ${sl:,.2f}"
        elif signal == "SELL":
            message += f"\n📉 *SELL Signal*\n🎯 TP: ${tp:,.2f}\n🛑 SL: ${sl:,.2f}"
        else:
            message += f"\n⏳ Pasar tenang...\n🎯 TP: ${tp:,.2f} | 🛑 SL: ${sl:,.2f}"

        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        log_signal(symbol, signal_data)  # simpan ke file
        last_signal[symbol] = signal

# === Loop utama ===
async def auto_signal():
    pairs = ["BTCUSDT", "XAUUSD", "EURUSD", "GBPUSD"]
    last_signal = {}

    # Buat file log header jika belum ada
    with open("signal_log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Waktu", "Pair", "Sinyal", "Harga", "Take Profit", "Stop Loss", "Perubahan"])

    await bot.send_message(chat_id=CHAT_ID, text="🤖 Bot Auto-Signal + Log Aktif!\nMemantau: BTC, XAU, EUR, GBP")

    while True:
        for symbol in pairs:
            prices = get_candles(symbol)
            signal_data = generate_signal(prices)
            if signal_data:
                await send_signal(symbol, signal_data, last_signal)
        await asyncio.sleep(60)  # cek setiap 1 menit

# === Jalankan ===
if __name__ == "__main__":
    print("🤖 Bot Auto-Signal + Log sedang berjalan...")
    asyncio.run(auto_signal())
