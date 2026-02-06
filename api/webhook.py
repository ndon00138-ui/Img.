import telebot
import requests
import qrcode
import os
import json
from http.server import BaseHTTPRequestHandler

# API Keys (သင့် Bot Token ထည့်ထားပေးတယ်)
API_TOKEN = '8512366652:AAHZIt4ZzHc2TtplWF61ljpSoM_is8lenbI'
IMGBB_API_KEY = 'ae1c30a6ba51b8695ac9109c7d10a39b'

bot = telebot.TeleBot(API_TOKEN, threaded=False)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = telebot.types.Update.de_json(post_data.decode('utf-8'))
        bot.process_new_updates([update])
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "မင်္ဂလာပါ! ကျွန်တော့်ဆီ ပုံတစ်ပုံ ပို့ပေးပါ။")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        tmp_img = "/tmp/temp.jpg"
        qr_path = "/tmp/qr.png"
        with open(tmp_img, 'wb') as f: f.write(downloaded_file)
        with open(tmp_img, "rb") as f:
            res = requests.post("https://api.imgbb.com/1/upload", {"key": IMGBB_API_KEY}, files={"image": f})
            data = res.json()
        if data['status'] == 200:
            img_url = data['data']['url']
            qr_img = qrcode.make(img_url)
            qr_img.save(qr_path)
            with open(qr_path, 'rb') as q:
                bot.send_photo(message.chat.id, q, caption=f"✅ Link: {img_url}")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")
