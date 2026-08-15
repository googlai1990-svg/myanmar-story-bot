import os
import telebot
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = "8706964553:AAHbyOVhBoqkoVy9vQWjoLR08YBFuZLQWzI"
GEMINI_API_KEY = "AQ.Ab8RN6Ix2d72Vzd-7cz0HjBHjhkq9Qw5CwwUJHGhZF3KX-z2JA"
ACTIVE_PASSWORD = "STORY_AUG2026"

verified_users = set()
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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
        res = model.generate_content(txt)
        bot.reply_to(message, res.text)
    except Exception as e:
        bot.reply_to(message, "ခေတ္တစောင့်ဆိုင်းပြီး ပြန်လည်ကြိုးစားပေးပါ။")

print("Bot started...")
bot.infinity_polling()
