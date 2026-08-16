import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot

# --- Render Keep-Alive ---
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
GROQ_API_KEY = "gsk_HUoh3cJJiEOvDkRHZzNWWGdyb3FY0W0T1rkiIO0JdCwDoPrTR0"
ACTIVE_PASSWORD = "STORY_AUG2026"

verified_users = set()
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def ask_ai(prompt_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are MyanmarStoryAI Assistant. You create detailed 3D cinematic animation prompts, character DNA, and Burmese story narration."
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload, timeout=45)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
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
        reply = ask_ai(txt)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

print("Bot is running...")
bot.infinity_polling()
