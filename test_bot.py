import requests

TOKEN = "8471380538:AAH0fzS-j7lVmpXH2EYHNRfMPe1wod44GKs"
CHAT_ID = "6227149877"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=payload)
    print(r.text)  # tampilkan hasil untuk memastikan sukses

send_message("✅ Tes langsung dari Python via requests!")
