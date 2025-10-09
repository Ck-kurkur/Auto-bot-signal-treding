import time
import requests

# === GANTI DENGAN DATA KAMU ===
TOKEN = "8471380538:AAH0fzS-j7lVmpXH2EYHNRfMPe1wod44GKs"
CHAT_ID = "6227149877"

SYMBOL = "BTCUSDT"     # coin yang mau dipantau
INTERVAL = 60          # waktu update (detik)
THRESHOLD = 0.05       # % perubahan harga untuk kirim sinyal

# === Fungsi kirim pesan ke Telegram ===
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=payload)
        print("Pesan terkirim:", r.json())
    except Exception as e:
        print("Gagal kirim pesan:", e)

# === Ambil harga dari API (pakai CryptoCompare biar tidak diblokir) ===
def get_price():
    try:
        symbol_base = SYMBOL.replace("USDT", "")
        url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol_base}&tsyms=USDT"
        data = requests.get(url, timeout=10).json()
        return float(data["USDT"])
    except Exception as e:
        print("🌐 Gagal ambil harga:", e)
        time.sleep(10)
        return get_price()

# === Jalankan bot ===
last_price = get_price()
send_message(f"🤖 Bot mulai! Memantau {SYMBOL}\nHarga awal: ${last_price:.2f}")

while True:
    try:
        current_price = get_price()
        change = ((current_price - last_price) / last_price) * 100

        if abs(change) >= THRESHOLD:
            if change > 0:
                sinyal = f"📈 BUY — {SYMBOL} naik {change:.2f}%\nHarga: ${current_price:.2f}"
            else:
                sinyal = f"📉 SELL — {SYMBOL} turun {change:.2f}%\nHarga: ${current_price:.2f}"
            send_message(sinyal)
            last_price = current_price

        time.sleep(INTERVAL)
    except Exception as e:
        print("Error utama:", e)
        time.sleep(10)
