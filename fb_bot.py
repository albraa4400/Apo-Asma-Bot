import telebot
import yt_dlp
import os
import uuid
from flask import Flask
from threading import Thread

# --- [1] إعدادات الهوية والتوكن ---
API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA' 
MY_ID = 1201544149  # معرف القائد أبو العصماء ✅
bot = telebot.TeleBot(API_TOKEN)

# --- [2] نظام منع الخمول (Keep Alive) متوافق مع Render ---
app = Flask('')

@app.route('/')
def home():
    return "الجيش التقني يعمل بكفاءة! 🚀"

def run():
    # إصلاح المنفذ ليعمل تلقائياً مع Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- [3] نظام إدارة المستخدمين ---
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
    bot.reply_to(message, "🚀 مرحباً بك في بوت أبو العصماء الخارق!\n\nأرسل رابط الفيديو من (يوتيوب، تيك توك، فيسبوك) وسأقوم بالتحميل فوراً.")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id == MY_ID:
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                count = len(f.read().splitlines())
            bot.reply_to(message, f"📊 **تقرير الأداء يا قائد:**\n\nعدد المستخدمين: {count}")
        else:
            bot.reply_to(message, "📊 لا يوجد مستخدمين بعد.")
    else:
        bot.reply_to(message, "⚠️ هذا الأمر للمطور فقط.")

# --- [جديد] خاصية الإذاعة (Broadcast) ---
@bot.message_handler(commands=['send'])
def broadcast(message):
    if message.from_user.id == MY_ID:
        text = message.text.replace('/send', '').strip()
        if not text:
            bot.reply_to(message, "يرجى كتابة الرسالة بعد الأمر، مثال:\n`/send نعتذر عن العطل`")
            return
        
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                users = f.read().splitlines()
            
            success = 0
            for user in users:
                try:
                    bot.send_message(user, text)
                    success += 1
                except:
                    continue
            bot.reply_to(message, f"✅ تمت الإذاعة بنجاح لـ {success} مستخدم.")
    else:
        bot.reply_to(message, "⚠️ هذا الأمر للمطور فقط.")

# --- [5] محرك التحميل ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "http" in url:
        sent_msg = bot.reply_to(message, "⏳ جاري التحميل... انتظر قليلاً.")
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"video_{unique_id}.mp4"

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_filename,
            'quiet': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'nocheckcertificate': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if os.path.exists(output_filename):
                with open(output_filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, caption="✅ تم التحميل بواسطة بوت أبو العصماء")
                os.remove(output_filename)
                bot.delete_message(message.chat.id, sent_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ خطأ فني، يرجى المحاولة لاحقاً.", message.chat.id, sent_msg.message_id)
            if os.path.exists(output_filename): os.remove(output_filename)
    else:
        bot.reply_to(message, "أرسل رابطاً صحيحاً يا بطل!")

# --- [6] التشغيل ---
if __name__ == "__main__":
    keep_alive()
    print("البوت انطلق الآن...")
    bot.polling(none_stop=True)
    
