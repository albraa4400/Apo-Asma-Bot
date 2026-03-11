import telebot
from telebot import types
import yt_dlp
import os
import time
from flask import Flask
from threading import Thread

# 1. إعداد Flask لإبقاء السيرفر حياً على Render
app = Flask('')

@app.route('/')
def home():
    return "Abu Al-Asma Bot is Running Perfectly!"

def run_flask():
    # المنفذ الافتراضي لـ Render
    app.run(host='0.0.0.0', port=7860)

# 2. التوكن الجديد الخاص بك
API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA'
bot = telebot.TeleBot(API_TOKEN)

# 3. دالة التحميل الموحدة (فيديو وصوت)
def download_content(url, mode='video'):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'format': 'best' if mode == 'video' else 'bestaudio/best',
    }

    if mode == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if mode == 'audio':
            return filename.rsplit('.', 1)[0] + '.mp3'
        return filename

# 4. استقبال الأوامر والروابط
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "حبابك في بوت 'أبو العصماء الخارق' ! 📥\n\n"
        "أرسل لي أي رابط من (فيسبوك، تيك توك، يوتيوب، إنستغرام) "
        "وسأقوم بتحميله لك فوراً."
    )
    bot.reply_to(message, welcome_msg)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    url = message.text.strip()
    
    # التحقق من وجود رابط في الرسالة
    if url.startswith('http'):
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_video = types.InlineKeyboardButton("فيديو 🎬", callback_data=f"vid_{url}")
        btn_audio = types.InlineKeyboardButton("صوت MP3 🎵", callback_data=f"aud_{url}")
        markup.add(btn_video, btn_audio)
        
        bot.reply_to(message, "تم استلام الرابط بنجاح! اختر الصيغة:", reply_markup=markup)
    else:
        bot.reply_to(message, "يا بطل، أرسل رابطاً صحيحاً يبدأ بـ http لكي أتمكن من مساعدتك.")

# 5. معالجة ضغطات الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    url = ""
    try:
        # تقسيم البيانات للحصول على الوضع والرابط
        data_parts = call.data.split('_', 1)
        mode_key = data_parts[0]
        url = data_parts[1]
        
        mode = 'audio' if mode_key == 'aud' else 'video'
        status_text = "جاري استخراج الصوت... 🎵" if mode == 'audio' else "جاري تحميل الفيديو... 🎬"
        
        bot.edit_message_text(status_text, call.message.chat.id, call.message.message_id)
        
        # تنفيذ التحميل
        file_path = download_content(url, mode)
        
        # إرسال الملف للمستخدم
        with open(file_path, 'rb') as f:
            if mode == 'audio':
                bot.send_audio(call.message.chat.id, f, caption="تم استخراج الصوت بواسطة بوت أبو العصماء ✅")
            else:
                bot.send_video(call.message.chat.id, f, caption="تم التحميل بواسطة بوت أبو العصماء ✅")
        
        # تنظيف الذاكرة
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        bot.send_message(call.message.chat.id, f"عذراً، تعذر التحميل. تأكد من أن الرابط عام وليس خاص.\nالخطأ: {str(e)}")

# 6. تشغيل البوت والسيرفر معاً
def start_bot():
    print("البوت يعمل الآن ويستقبل الروابط...")
    bot.polling(none_stop=True, timeout=60)

if __name__ == "__main__":
    # تشغيل Flask في الخلفية لإبقاء الخدمة تعمل
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # تشغيل البوت في الواجهة الأساسية
    start_bot()
    
