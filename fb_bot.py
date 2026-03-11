import telebot
from telebot import types
import yt_dlp
import os
import uuid # لاستخدامه في توليد معرفات قصيرة للروابط
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run_flask(): app.run(host='0.0.0.0', port=7860)

API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA'
bot = telebot.TeleBot(API_TOKEN)

# مخزن مؤقت للروابط الطويلة لتفادي مشكلة الـ 64 بايت في تلجرام
url_storage = {}

def download_content(url, mode='video'):
    if not os.path.exists('downloads'): os.makedirs('downloads')
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best' if mode == 'video' else 'bestaudio/best',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    if mode == 'audio':
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename.rsplit('.', 1)[0] + '.mp3' if mode == 'audio' else filename

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    url = message.text.strip()
    if url.startswith('http'):
        # توليد معرف فريد وقصير للرابط (مثل: a1b2c3)
        link_id = str(uuid.uuid4())[:8]
        url_storage[link_id] = url # حفظ الرابط الطويل في الذاكرة
        
        markup = types.InlineKeyboardMarkup()
        # نضع المعرف القصير فقط في الزر
        markup.add(types.InlineKeyboardButton("فيديو 🎬", callback_data=f"v_{link_id}"),
                   types.InlineKeyboardButton("صوت 🎵", callback_data=f"a_{link_id}"))
        
        bot.reply_to(message, "تم استلام الرابط! اختر الصيغة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    try:
        prefix, link_id = call.data.split('_')
        url = url_storage.get(link_id) # استعادة الرابط من الذاكرة
        
        if not url:
            bot.answer_callback_query(call.id, "عذراً، انتهت صلاحية هذا الرابط. أرسله مجدداً.")
            return

        mode = 'audio' if prefix == 'a' else 'video'
        bot.edit_message_text("جاري التحميل بأقصى سرعة... ⏳", call.message.chat.id, call.message.message_id)
        
        file_path = download_content(url, mode)
        with open(file_path, 'rb') as f:
            if mode == 'audio': bot.send_audio(call.message.chat.id, f)
            else: bot.send_video(call.message.chat.id, f)
        
        os.remove(file_path)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
    
