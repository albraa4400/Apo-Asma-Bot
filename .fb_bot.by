import telebot
import os
import yt_dlp
from flask import Flask
from threading import Thread

# 1. السيرفر الوهمي للبقاء حياً على Render
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعداد البوت
API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA'
bot = telebot.TeleBot(API_TOKEN)

# 3. دالة التحميل
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# 4. الأوامر
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "أهلاً يا أبو الأسماء! أرسل لي رابط الفيديو (تيك توك، فيسبوك، يوتيوب) وسأقوم بتحميله لك فوراً.")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_download(message):
    msg = bot.reply_to(message, "⏳ جاري المعالجة والتحميل، انتظر قليلاً...")
    try:
        # حذف الفيديو القديم إذا وجد
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')
            
        download_video(message.text)
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="تم التحميل بواسطة بوتك الخارق 🚀")
        
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"حدث خطأ أثناء التحميل: {str(e)}", message.chat.id, msg.message_id)

if __name__ == "__main__":
    keep_alive()
    print("البوت انطلق بنجاح...")
    bot.infinity_polling()
