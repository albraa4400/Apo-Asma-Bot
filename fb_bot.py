import telebot
from telebot import types
import yt_dlp
import os
import time
from flask import Flask
from threading import Thread
import random

# 1. إعداد Flask
app = Flask('')
@app.route('/')
def home(): return "Abu Al-Asma Bot is Ultra Active!"
def run_flask(): app.run(host='0.0.0.0', port=7860)

# 2. التوكن الجديد
API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA'
bot = telebot.TeleBot(API_TOKEN)

# 3. دالة التحميل مع "خدعة التمويه"
def download_content(url, mode='video'):
    if not os.path.exists('downloads'): os.makedirs('downloads')

    # قائمة متصفحات عشوائية للتمويه
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    ]

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'format': 'best' if mode == 'video' else 'bestaudio/best',
        # --- بداية الخدعة ---
        'user_agent': random.choice(user_agents),
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_color': True,
        'geo_bypass': True, # خدعة لتجاوز الحظر الجغرافي
        'referer': 'https://www.google.com/',
        # -------------------
    }

    if mode == 'audio':
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if not info: raise Exception("لم أتمكن من جلب بيانات الرابط")
        filename = ydl.prepare_filename(info)
        return filename.rsplit('.', 1)[0] + '.mp3' if mode == 'audio' else filename

# 4. الأوامر
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "حبابك عشرة بلا كشره في بوت 'أبو العصماء الخارق'! 📥\nأرسل الرابط وسأقوم بالالتفاف على الحظر فوراً.")

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    url = message.text.strip()
    if url.startswith('http'):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("فيديو 🎬", callback_data=f"vid_{url}"),
                   types.InlineKeyboardButton("صوت MP3 🎵", callback_data=f"aud_{url}"))
        bot.reply_to(message, "تم رصد الرابط! اختر الصيغة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    try:
        data = call.data.split('_', 1)
        mode = 'audio' if data[0] == 'aud' else 'video'
        url = data[1]
        bot.edit_message_text("جاري استخدام 'خدعة التمويه' للتحميل... ⏳", call.message.chat.id, call.message.message_id)
        
        file_path = download_content(url, mode)
        with open(file_path, 'rb') as f:
            if mode == 'audio': bot.send_audio(call.message.chat.id, f)
            else: bot.send_video(call.message.chat.id, f)
        os.remove(file_path)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"فشلت الخدعة هذه المرة! يوتيوب ما زال يرفض الـ IP.\nالخطأ: {str(e)}")

# 5. التشغيل
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    print("البوت بدأ العمل بخدع التمويه!")
    bot.polling(none_stop=True)
    
