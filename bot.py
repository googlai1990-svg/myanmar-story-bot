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
GROQ_API_KEY = "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"
ACTIVE_PASSWORD = "STORY_AUG2026"

verified_users = set()
# User တစ်ဦးချင်းစီ၏ စကားပြောမှတ်တမ်း (Memory) သိမ်းဆည်းရန် နေရာ
user_conversations = {}

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

SYSTEM_PROMPT = """You are MyanmarStoryAI Master Assistant.
Your mission is to help create continuous, high-quality 3D cinematic animation storylines, character DNA, Midjourney/Flux image prompts, Luma/Kling video camera prompts, and Burmese narration scripts.
Always maintain context and remember previous story scenes. When the user says 'ဆက်သွား' or asks for the next scene, seamlessly continue from where you left off."""

def ask_ai_with_memory(user_id, prompt_text):
    if user_id not in user_conversations:
        user_conversations[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    # User ရိုက်ပို့သော စာကို Memory ထဲ ထည့်ခြင်း
    user_conversations[user_id].append({"role": "user", "content": prompt_text})
    
    # Memory အများကြီး မပြည့်သွားစေရန် နောက်ဆုံး စာကြောင်း ၁၀ ကြောင်းသာ ထိန်းသိမ်းခြင်း
    if len(user_conversations[user_id]) > 12:
        user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-10:]

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "model": "llama-3.1-8b-instant"

",
        "messages": user_conversations[user_id]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=45)
    if response.status_code == 200:
        data = response.json()
        bot_reply = data["choices"][0]["message"]["content"]
        # AI ပြန်ဖြေသော အဖြေကိုလည်း Memory ထဲ ထည့်ခြင်း
        user_conversations[user_id].append({"role": "assistant", "content": bot_reply})
        return bot_reply
    else:
        return f"⚠️ API Error ({response.status_code}): {response.text}"

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "မင်္ဂလာပါ! MyanmarStoryAI Bot မှ ကြိုဆိုပါတယ်။ Access Password ကို ရိုက်ထည့်ပေးပါ။")

@bot.message_handler(commands=['clear', 'reset'])
def reset_cmd(message):
    uid = message.from_user.id
    if uid in user_conversations:
        user_conversations[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
    bot.reply_to(message, "🔄 ရှေ့က မှတ်ဉာဏ်ဟောင်းများကို ရှင်းလင်းပြီးပါပြီ။ ဇာတ်လမ်းအသစ် စတင်ဖန်တီးနိုင်ပါပြီ။")

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
        reply = ask_ai_with_memory(uid, txt)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

print("Bot is running with memory...")
bot.infinity_polling()
