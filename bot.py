import os
import telebot
import google.generativeai as genai

# --- API Keys ---
TELEGRAM_BOT_TOKEN = "8706964553:AAHbyOVhBoqkoVy9vQWjoLR08YBFuZLQWzI"
GEMINI_API_KEY = AQ.Ab8RN6Ix2d72Vzd-7czOHjBHjhkq9Qw5CwwUJHGhZF3KX-z2JA

ACTIVE_PASSWORD = "STORY_AUG2026"
verified_users = set()

# --- Gemini Setup ---
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {"temperature": 0.7}

SYSTEM_PROMPT = """
You are "MyanmarStoryAI Studio Bot," an elite 3D Cinematic Animation Director and Workflow Automation Specialist. You convert simple story ideas into full, production-ready animation packs (Consistent Visual Prompts, Video Motion Prompts, Burmese Narration, CapCut Guides, and Sound Effects).

When the user provides their choice and story idea, output strictly in this complete structured layout:

1. Story Overview & Master Character DNA (ဇာတ်လမ်းအကျဉ်းနှင့် ဇာတ်ကောင် DNA):
   - Story Synopsis (မြန်မာလို ဇာတ်လမ်းအကျဉ်း)
   - Master Character Visual DNA: (Detailed 3D Pixar/Disney style prompt locking character species, facial features, clothing, specific colors, and key props to ensure 100% visual consistency across all scenes).

2. Scene-by-Scene Production Breakdown (for each scene):
   - Scene Number & Title:
   - Midjourney/Flux Image Prompt: (Detailed 3D cinematic framing, includes Master Character DNA, cinematic volumetric lighting, octane render --ar [9:16 if Option 1, 16:9 if Option 2] --no text, watermark, deformed limbs, extra fingers, blurry, 2D flat style --v 6.1 --stylize 250)
   - Kling / Runway Video Motion Prompt: (Camera motion: Pan/Zoom/Tilt, dynamic character actions, smooth 4k cinematic animation)
   - Myanmar Narration / Voiceover: (မြန်မာလို ဇာတ်ကြောင်းပြောစာသား + အသံ Tone လမ်းညွှန်: ဥပမာ- ရယ်စရာ/စိတ်လှုပ်ရှားဖွယ်)
   - Audio & SFX: [BGM Recommendation] + [Exact Sound Effects: e.g., Whoosh, Pop, Footsteps, Cartoon thud]

3. CapCut Quick Editing Guide:
   - Canvas Ratio, Video Transitions, and Text Style.
   - Recommended Viral TikTok / YouTube Tags.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
    generation_config=generation_config
)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id in verified_users:
        bot.reply_to(message, "မင်္ဂလာပါ! MyanmarStoryAI Studio မှ ကြိုဆိုပါတယ်။ သင်ဖန်တီးလိုသော ပုံစံနံပါတ် (1/2/3) နှင့် Story Idea ကို ပေးပို့နိုင်ပါပြီ။")
    else:
        bot.reply_to(message, "မင်္ဂလာပါ! MyanmarStoryAI Bot ကို အသုံးပြုရန် ကျေးဇူးပြု၍ ယခုလအတွက် ဝယ်ယူထားသော Access Password ကို ရိုက်ထည့်ပေးပါ။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in verified_users:
        if text == ACTIVE_PASSWORD:
            verified_users.add(user_id)
            menu_text = (
                "🎉 Password မှန်ကန်ပါသည်။ MyanmarStoryAI Studio မှ ကြိုဆိုပါတယ်။\n\n"
                "သင် ဖန်တီးလိုသော ပုံစံကို နံပါတ်ရွေးချယ်ပေးပါ-\n"
                "[1] TikTok / Shorts / Reels (9:16 Vertical | 3 to 5 Scenes)\n"
                "[2] YouTube Long-form (16:9 Horizontal | 6 to 10 Scenes)\n"
                "[3] Custom Character DNA & Story Creation\n\n"
                "ရွေးချယ်လိုသော နံပါတ်နှင့်အတူ သင့် ဇာတ်လမ်း Idea ကို တစ်ခါတည်း ရေးသားပေးပို့နိုင်ပါပြီ။"
            )
            bot.reply_to(message, menu_text)
        else:
            bot.reply_to(message, "❌ Password မှားယွင်းနေပါသည်။ ကျေးဇူးပြု၍ မှန်ကန်သော Password ပြန်လည်ရိုက်ထည့်ပါ (သို့မဟုတ်) ဝယ်ယူရန် Admin ကို ဆက်သွယ်ပါ။")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = model.generate_content(text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "ခေတ္တစောင့်ဆိုင်းပြီး ပြန်လည်ကြိုးစားပေးပါ။")

print("Bot is successfully running...")
bot.infinity_polling()
