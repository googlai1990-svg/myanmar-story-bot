import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot

# --- Render Port Binding (Keep-Alive) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"MyanmarStoryAI Bot is Live!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- Config & Keys ---
TELEGRAM_BOT_TOKEN = "8706964553:AAHbyOVhBoqkoVy9vQWjoLR08YBFuZLQWzI"
GEMINI_API_KEY = "AQ.Ab8RN6LGV768ktqECkFvujNoKgH7YuvWhu1iMcufzYoiWFxy7"  # သင် screenshot မှာ ယူထားတဲ့ Key အပြည့်အစုံကိအပြည့်အအပြည့်အစုံကိအပြည့အပြည့်အစုံကိအပြည့်အအပြည့်အစုံကိအပ
ACTIVE_PASSWORD = "STORY_AUG2026"

verified_users = set()
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def ask_gemini(prompt_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"⚠️ API Error ({response.status_code}): {response.text}"

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "မင်္ဂလာပါ! MyanmarStoryAI Bot မှ ကြိုဆိုပါတယ်။ Access Password ကို ရိုက်ထည့်ပေးပါ။")

@bot.message_handler(func=lambda m: True)
def chat_handler(message):
    uid = message.from_user.id
    txt = message.text.strip()
    
    if uid not in verified_users:
        if txt == ACTIVE_PASSWORD:
            verified_users.add(uid)
            bot.reply_to(message, "🎉 Password မှန်ကန်ပါသည်။ သင်ဖန်တီးလိုသော Story Idea ကို ပေးပို့နိုင်ပါပြီ။")
        else:
            bot.reply_to(message, "❌ Password မှားယွင်းနေပါသည်။")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    try:
        reply = ask_gemini(txt)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

print("Bot is running...")
bot.infinity_polling()

