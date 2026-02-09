import telebot
import requests
import qrcode
import io
from flask import Flask, request

# သင့်ရဲ့ Keys များကို ဒီမှာ ထည့်ပါ
API_TOKEN = '8512366652:AAEMH3Ko4emBHDI6SvbZratAQww1RBGsFbQ'
IMGBB_API_KEY = 'e0e31e5ba42e35978ea3495c7bbe3ae7'

bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Forbidden', 403

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "မင်္ဂလာပါ! ကျွန်တော့်ဆီ ပုံပို့ပေးရင် Link နဲ့ QR ထုတ်ပေးပါ့မယ်။")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    msg = bot.reply_to(message, "⌛ ပုံကို Link ပြောင်းနေပါတယ်...")
    try:
        # ၁။ Telegram ဆီက ပုံကို ဒေါင်းလုဒ်ဆွဲခြင်း
        file_info = bot.get_file(message.photo[-1].file_id)
        img_data = bot.download_file(file_info.file_path)

        # ၂။ ImgBB API သို့ Upload တင်ခြင်း
        res = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY},
            files={"image": img_data},
            timeout=15
        )
        data = res.json()
        
        if data['status'] == 200:
            img_url = data['data']['url']

            # ၃။ QR Code ထုတ်ခြင်း
            qr = qrcode.make(img_url)
            qr_io = io.BytesIO()
            qr.save(qr_io, 'PNG')
            qr_io.seek(0)

            # ၄။ ရလဒ်ပြန်ပို့ခြင်း
            bot.delete_message(message.chat.id, msg.message_id)
            bot.send_photo(
                message.chat.id, 
                qr_io, 
                caption=f"✅ ပုံ Link ရပါပြီ -\n\n{img_url}"
            )
        else:
            bot.edit_message_text("❌ ImgBB Error: API Key ကို စစ်ဆေးပါ။", message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ အမှားတစ်ခု ရှိနေပါတယ် - {str(e)}", message.chat.id, msg.message_id)

# Text ပို့ရင် ဘာမှမလုပ်အောင် ထားနိုင်ပါတယ် (သို့မဟုတ်) အကြောင်းပြန်ခိုင်းထားပါ
@bot.message_handler(func=lambda m: True)
def text_only(message):
    bot.reply_to(message, "ကျေးဇူးပြု၍ ဓာတ်ပုံ (Image) ပဲ ပို့ပေးပါခင်ဗျာ။")
