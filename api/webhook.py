import telebot
import json
from http.server import BaseHTTPRequestHandler

# Token အမှန်ထည့်ထားပါတယ်
bot = telebot.TeleBot('8512366652:AAHZIt4ZzHc2TtplWF61ljpSoM_is8lenbI', threaded=False)

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
    bot.reply_to(message, "Bot အောင်မြင်စွာ အလုပ်လုပ်နေပါပြီ!")
