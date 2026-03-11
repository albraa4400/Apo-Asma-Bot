import telebot
from telebot import types
import yt_dlp
import os
import time
from flask import Flask
from threading import Thread

# 1. إعداد Flask لإبقاء السيرفر حياً (Keep-Alive)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running Perfectly! - Abu Al-Asma"

def run_flask():
    # Render يتطلب المنفذ 7860 أو 10000
    app.run(host='0.0.0.0', port=7860)

# 2. إعداد البوت (التوكن الخاص بك)
API_TOKEN = '8753502535:AAHmcXsDQnQUhL7T-Y6h_v-7v-N9-0'
bot = telebot.TeleBot(API_TOKEN)

# 3. دالة تحميل المحتوى (فيديو أو صوت)
def download_content(url, mode='video'):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    if mode == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True
        }
    else:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if mode == 'audio':
            # التأكد من الامتداد الصحيح للملف الصوتي
            return filename.rsplit('.', 1)[0] + '.mp3'
        return filename

# 4. التعامل مع الأوامر والرسائل
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "مرحباً بك في بوت أبو العصماء المطور! 📥\n\n"
        "أرسل لي أي رابط (فيسبوك، يوتيوب، تيك توك) "
        "وسأقوم بتحميله لك كفيديو أو استخراج الصوت منه بجودة عالية."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda m: 'http' in m.text)
def ask_format(message):
    url = message.text
    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton("فيديو 🎬", callback_data=f"vid_{url}")
    btn_audio = types.InlineKeyboardButton("صوت MP3 🎵", callback_data=f"aud_{url}")
    markup.add(btn_video, btn_audio)
    bot.reply_to(message, "وصل الرابط! اختر الصيغة المطلوبة:", reply_markup=markup)

# 5. التعامل مع خيارات المستخدم (أزرار)
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    try:
        data_parts = call.data.split('_', 1)
        mode_key = data_parts[0]
        url = data_parts[1]
        
        mode = 'audio' if mode_key == 'aud' else 'video'
        status_msg = "جاري استخراج الصوت... 🎵" if mode == 'audio' else "جاري تحميل الفيديو... 🎬"
        
        bot.edit_message_text(status_msg, call.message.chat.id, call.message.message_id)
        
        file_path = download_content(url, mode)
        
        with open(file_path, 'rb') as f:
            if mode == 'audio':
                bot.send_audio(call.message.chat.id, f, caption="تم استخراج الصوت بواسطة بوت أبو العصماء ✅")
            else:
                bot.send_video(call.message.chat.id, f, caption="تم التحميل بواسطة بوت أبو العصماء ✅")
        
        if os.path.exists(file_path):
            os.remove(file_path) # مسح الملف لتوفير مساحة السيرفر
            
    except Exception as e:
        bot.send_message(call.message.chat.id, f"عذراً، حدث خطأ: {str(e)}")

# 6. تشغيل البوت مع خاصية إعادة التشغيل التلقائي عند الخطأ
def start_bot():
    print("البوت بدأ في استقبال الرسائل الآن...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"خطأ في الاتصال: {e}")
            time.sleep(10)
if __name__ == "__main__":
    # تشغيل Flask في خيط منفصل (Daemon) لضمان عدم توقف الكود الرئيسي
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # تشغيل البوت في الخيط الرئيسي
    start_bot()
    
