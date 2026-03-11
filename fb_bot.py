import telebot
from telebot import types
import yt_dlp
import os
import time
from flask import Flask
from threading import Thread

# إعداد Flask لإبقاء السيرفر حياً
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running Perfectly!"

def run():
    app.run(host='0.0.0.0', port=7860)

# التوكن الخاص بك (أبو العصماء)
API_TOKEN = '8753502535:AAHmcXsDQnQUhL7T-Y6h_v-7v-N9-0' # تأكد من التوكن الصحيح
bot = telebot.TeleBot(API_TOKEN)

# دالة تحميل الفيديو أو الصوت
def download_content(url, mode='video'):
    if mode == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
    else:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if mode == 'audio':
            return filename.rsplit('.', 1)[0] + '.mp3'
        return filename

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت أبو العصماء المطور! 📥\nأرسل لي رابط الفيديو (فيسبوك، يوتيوب، تيك توك) وسأعطيك خيارات التحميل.")

@bot.message_handler(func=lambda m: 'http' in m.text)
def ask_format(message):
    url = message.text
    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton("فيديو 🎬", callback_data=f"vid_{url}")
    btn_audio = types.InlineKeyboardButton("صوت MP3 🎵", callback_data=f"aud_{url}")
    markup.add(btn_video, btn_audio)
    bot.reply_to(message, "كيف تريد تحميل المحتوى؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    url = call.data.split('_', 1)[1]
    mode = 'audio' if call.data.startswith('aud') else 'video'
    
    bot.edit_message_text(f"جاري التجهيز... انتظر قليلاً ⏳", call.message.chat.id, call.message.message_id)
    
    try:
        file_path = download_content(url, mode)
        with open(file_path, 'rb') as f:
            if mode == 'audio':
                bot.send_audio(call.message.chat.id, f, caption="تم استخراج الصوت بواسطة بوت أبو العصماء ✅")
            else:
                bot.send_video(call.message.chat.id, f, caption="تم التحميل بواسطة بوت أبو العصماء ✅")
        os.remove(file_path) # حذف الملف لتوفير المساحة
    except Exception as e:
        bot.send_message(call.message.chat.id, f"حدث خطأ أثناء التحميل: {str(e)}")

def start_bot():
    while True:
        try:
            bot.remove_webhook()
            print("البوت بدأ في استقبال الرسائل...")
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"خطأ في الشبكة: {e}")
            time.sleep(10)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    start_bot()
    
