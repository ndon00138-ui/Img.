import telebot
import requests
import json
from http.server import BaseHTTPRequestHandler

# ၁။ သင့်ရဲ့ Bot Token
API_TOKEN = '8512366652:AAFI22GhtOtOP-QCQw9R6-6u1kqPJqMm03s'
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

# Start Command ပို့တဲ့အခါ
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📸 မင်္ဂလာပါ! ကျွန်တော့်ဆီ ပုံတစ်ပုံ ပို့ပေးပါ။\nကျွန်တော်က အဲ့ဒီပုံရဲ့ URL Link ကို ထုတ်ပေးပါ့မယ်။ ✨")

# ပုံပို့လာတဲ့အခါ Link ထုတ်ပေးခြင်း
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Telegram ဆီက ပုံကို ယူခြင်း
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Telegra.ph သို့ Upload တင်ခြင်း
        response = requests.post(
            'https://telegra.ph/upload',
            files={'file': ('file', downloaded_file, 'image/jpeg')}
        )
        
        # ရလာတဲ့ Link ကို ပြန်ပို့ပေးခြင်း
        img_url = 'https://telegra.ph' + response.json()[0]['src']
        
        reply_text = (
            f"✅ ပုံရဲ့ Link ရပါပြီဗျ -\n\n"
            f"🔗 {img_url}\n\n"
            f"ဒီ Link ကို ဘယ်နေရာမှာမဆို ပြန်သုံးလို့ရပါတယ်။"
        )
        bot.reply_to(message, reply_text)
        
    except Exception as e:
        bot.reply_to(message, "❌ စိတ်မရှိပါနဲ့ဗျ၊ Link ထုတ်ပေးဖို့ အခက်အခဲရှိနေပါတယ်။ နောက်တစ်ခေါက် ပြန်စမ်းကြည့်ပါဦး။")

# တခြား စာသားတွေ ပို့လာရင်
@bot.message_handler(func=lambda message: True)
def other_messages(message):
    bot.reply_to(message, "ပုံ (Photo) ပဲ ပို့ပေးပါခင်ဗျာ။ ကျွန်တော်က ပုံတွေကိုပဲ Link ပြောင်းပေးနိုင်တာပါ 🖼️")
