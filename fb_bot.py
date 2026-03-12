import telebot
import yt_dlp
import os
import uuid
from flask import Flask
from threading import Thread

# --- [1] إعدادات الهوية والتوكن ---
# التوكن الخاص ببوت أبو العصماء تم وضعه هنا ✅
API_TOKEN = '7611599818:AAFlWnQ3AInwW63O_B_O0l-w_D8t66E_D68' 
MY_ID = 1201544149  # معرف القائد أبو العصماء 👤
bot = telebot.TeleBot(API_TOKEN)

# --- [2] نظام منع الخمول (Keep Alive) لـ Render ---
app = Flask('')

@app.route('/')
def home():
    return "الجيش التقني يعمل بكفاءة! 🚀"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- [3] نظام إدارة وإحصائيات المستخدمين ---
def save_user(user_id):
    filename = "users.txt"
    if not os.path.exists(filename):
        with open(filename, "w") as f: pass
    
    with open(filename, "r") as f:
        users = f.read().splitlines()
    
    if str(user_id) not in users:
        with open(filename, "a") as f:
            f.write(str(user_id) + "\n")

# --- [4] الأوامر البرمجية ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.from_user.id)
    welcome_text = (
        "🚀 مرحباً بك في بوت أبو العصماء الخارق!\n\n"
        "أرسل رابط الفيديو من (يوتيوب، تيك توك، فيسبوك) وسأقوم بالتحميل فوراً."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id == MY_ID:
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                count = len(f.read().splitlines())
            bot.reply_to(message, f"📊 **تقرير الأداء يا قائد:**\n\nعدد المستخدمين الفعليين: {count}")
        else:
            bot.reply_to(message, "📊 لا يوجد مستخدمين بعد.")
    else:
        bot.reply_to(message, "⚠️ هذا الأمر مخصص للمطور فقط.")

# --- [5] محرك التحميل (إصلاح يوتيوب وتجاوز الحظر) ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "http" in url:
        sent_msg = bot.reply_to(message, "⏳ جاري المعالجة والتحميل... انتظر قليلاً.")
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"video_{unique_id}.mp4"

        # إعدادات متطورة لتجاوز حماية يوتيوب ومنصات التواصل
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_filename,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'geo_bypass': True,
            'extract_flat': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if os.path.exists(output_filename):
                with open(output_filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, caption="✅ تم التحميل بواسطة بوت أبو العصماء")
                os.remove(output_filename)
                bot.delete_message(message.chat.id, sent_msg.message_id)
            else:
                bot.edit_message_text("❌ عذراً، تعذر العثور على ملف الفيديو. حاول مرة أخرى.", message.chat.id, sent_msg.message_id)
        
        except Exception as e:
            bot.edit_message_text(f"❌ خطأ فني: يرجى التأكد من الرابط أو المحاولة لاحقاً.", message.chat.id, sent_msg.message_id)
            if os.path.exists(output_filename): os.remove(output_filename)
    else:
        bot.reply_to(message, "أرسل رابطاً صحيحاً يا بطل! 🔗")

# --- [6] التشغيل ---
if __name__ == "__main__":
    keep_alive() # تشغيل سيرفر الاستيقاظ
    print("البوت انطلق الآن...")
    bot.polling(none_stop=True)
            
