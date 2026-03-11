import telebot
from telebot import types
import yt_dlp
import os
import time
from flask import Flask
from threading import Thread

# 1. إعداد Flask (المنقذ لـ Render)
app = Flask('')

@app.route('/')
def home():
    return "Abu Al-Asma Bot is Alive!"

def run_flask():
    app.run(host='0.0.0.0', port=7860)

# 2. التوكن الجديد (الذي أرسلته أنت للتو)
API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA'
bot = telebot.TeleBot(API_TOKEN)

# 3. دالة التحميل الموحدة
def download_content(url, mode='video'):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    if mode == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = 'best'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if mode == 'audio':
            return filename.rsplit('.', 1)[0] + '.mp3'
        return filename

# 4. الأوامر
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في نسخة 'أبو العصماء الخارق' الجديدة! 📥\nأرسل الرابط واختر الصيغة.")

@bot.message_handler(func=lambda m: 'http' in m.text)
def ask_format(message):
    url = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("فيديو 🎬", callback_data=f"vid_{url}"),
               types.InlineKeyboardButton("صوت MP3 🎵", callback_data=f"aud_{url}"))
    bot.reply_to(message, "كيف تريد التحميل؟", reply_markup=markup)

# 5. معالجة الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    try:
        data = call.data.split('_', 1)
        mode = 'audio' if data[0] == 'aud' else 'video'
        url = data[1]
        
        bot.edit_message_text("جاري المعالجة... ⏳", call.message.chat.id, call.message.message_id)
        
        file_path = download_content(url, mode)
        
        with open(file_path, 'rb') as f:
            if mode == 'audio':
                bot.send_audio(call.message.chat.id, f)
            else:
                bot.send_video(call.message.chat.id, f)
        
        os.remove(file_path)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"خطأ: {e}")

# 6. التشغيل (المسافات من الحافة تماماً)
def start_bot():
    print("البوت بدأ العمل بالتوكن الجديد!")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    start_bot()
    
