import telebot
import requests
import qrcode
import io
import os
from flask import Flask, request

# ၁။ သင့်ရဲ့ Keys များကို ဖြည့်ပါ
API_TOKEN = '8512366652:AAHebX2fmUNQfj7sITrQt0g6ZAVxVy2l4qg'
IMGBB_API_KEY = 'e0e31e5ba42e35978ea3495c7bbe3ae7'
GEMINI_API_KEY = 'AIzaSyCQ1GckgGZK6s4yRFkAfKXACAwA9bJU1P8'

bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)

# --- AI Function ---
def get_ai_response(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": text}]}]}
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "AI မအားသေးလို့ ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"

# --- Webhook Endpoint ---
@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Forbidden', 403

# --- Photo Handler (Link & QR) ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "ပုံကို Link ပြောင်းနေပါသည်...")
    try:
        # Telegram ကနေ ပုံကို ယူခြင်း
        file_info = bot.get_file(message.photo[-1].file_id)
        img_data = bot.download_file(file_info.file_path)
        
        # ImgBB သို့ တင်ခြင်း
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY},
            files={"image": img_data}
        )
        img_url = response.json()['data']['url']

        # QR Code ထုတ်ခြင်း
        qr = qrcode.make(img_url)
        qr_io = io.BytesIO()
        qr.save(qr_io, 'PNG')
        qr_io.seek(0)

        bot.send_photo(message.chat.id, qr_io, caption=f"✅ ပုံ Link: {img_url}")
    except:
        bot.reply_to(message, "❌ စိတ်မရှိပါနဲ့ဗျာ။ Link ထုတ်ပေးဖို့ အခက်အခဲရှိနေပါတယ်။")

# --- Text Handler (AI Chat) ---
@bot.message_handler(func=lambda m: True)
def chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    response = get_ai_response(message.text)
    bot.reply_to(message, response)
