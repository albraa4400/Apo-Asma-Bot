import telebot
from telebot import types
import yt_dlp
import os
import uuid
import time
from flask import Flask
from threading import Thread

# 1. إعداد Flask لإبقاء السيرفر حياً على Render
app = Flask('')
@app.route('/')
def home(): return "Abu Al-Asma Bot is Active!"

def run_flask(): app.run(host='0.0.0.0', port=7860)

# 2. إعدادات البوت (التوكن الخاص بك)
API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA'
bot = telebot.TeleBot(API_TOKEN)

# مخزن الروابط لتجاوز مشكلة الـ 64 بايت في تلجرام
url_storage = {}

# 3. دالة التحميل الاحترافية مع تمويه الهوية لتجنب الحظر
def download_content(url, mode='video'):
    if not os.path.exists('downloads'): os.makedirs('downloads')
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'format': 'best' if mode == 'video' else 'bestaudio/best',
        # انتحال صفحة متصفح حقيقي لتجنب رسائل "Sign in"
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
    }
    if mode == 'audio':
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename.rsplit('.', 1)[0] + '.mp3' if mode == 'audio' else filename

# 4. رسالة الترحيب والترويج (عند الضغط على /start)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    # الروابط الخاصة بك التي زودتني بها
    fb_button = types.InlineKeyboardButton("تابعنا على فيسبوك 👍", url="https://www.facebook.com/wad.alnor2")
    contact_button = types.InlineKeyboardButton("تواصل مع المطور (أبو العصماء) 💬", url="https://t.me/albraamohamed12")
    markup.add(fb_button, contact_button)
    
    promo_msg = (
        "مرحباً بك في بوت 'أبو العصماء الخارق'! 🚀\n\n"
        "أنا جاهز لتحميل الفيديوهات من مختلف المنصات.\n"
        "فقط أرسل الرابط الآن وابدأ التحميل! 👇"
    )
    bot.reply_to(message, promo_msg, reply_markup=markup)

# 5. استقبال الروابط ومعالجتها بمعرفات قصيرة
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    url = message.text.strip()
    if url.startswith('http'):
        link_id = str(uuid.uuid4())[:8]
        url_storage[link_id] = url
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("فيديو 🎬", callback_data=f"v_{link_id}"),
                   types.InlineKeyboardButton("صوت 🎵", callback_data=f"a_{link_id}"))
        
        bot.reply_to(message, "تم استلام الرابط بنجاح! اختر الصيغة:", reply_markup=markup)

# 6. تنفيذ عملية التحميل بعد اختيار الصيغة
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    try:
        prefix, link_id = call.data.split('_')
        url = url_storage.get(link_id)
        
        if not url:
            bot.answer_callback_query(call.id, "عذراً، الرابط قديم. أرسله مرة أخرى.")
            return

        mode = 'audio' if prefix == 'a' else 'video'
        bot.edit_message_text("جاري التحميل بأقصى سرعة... ⏳", call.message.chat.id, call.message.message_id)
        
        file_path = download_content(url, mode)
        with open(file_path, 'rb') as f:
            caption = "تم التحميل بواسطة بوت أبو العصماء الخارق ✅"
            if mode == 'audio': bot.send_audio(call.message.chat.id, f, caption=caption)
            else: bot.send_video(call.message.chat.id, f, caption=caption)
        
        os.remove(file_path) # حذف الملف بعد الإرسال لتوفير مساحة السيرفر
    except Exception as e:
        bot.send_message(call.message.chat.id, f"حدث خطأ: {str(e)}")

# 7. تشغيل البوت مع ميزة الحماية من التوقف
def start_bot():
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception:
            time.sleep(10) # إعادة التشغيل بعد 10 ثوانٍ في حال الانقطاع

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    start_bot()
    
