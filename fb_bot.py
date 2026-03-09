import telebot
from telebot import types
import requests
import os
import yt_dlp

# التوكن الخاص ببوتك
API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA'
bot = telebot.TeleBot(API_TOKEN)

user_links = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton('🛡️ تفعيل الدرع')
    item2 = types.KeyboardButton('📥 تحميل فيديو/صوت')
    markup.add(item1, item2)
    bot.reply_to(message, "أهلاً بك يا صديقي! اختر من القائمة:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🛡️ تفعيل الدرع')
def ask_token(message):
    msg = bot.send_message(message.chat.id, "أرسل توكن فيسبوك (EAAB...):")
    bot.register_next_step_handler(msg, activate_shield)

@bot.message_handler(func=lambda message: message.text == '📥 تحميل فيديو/صوت')
def ask_link(message):
    msg = bot.send_message(message.chat.id, "أرسل رابط الفيديو:")
    bot.register_next_step_handler(msg, process_link)

def process_link(message):
    url = message.text
    user_links[message.chat.id] = url
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎬 فيديو (MP4)", callback_data="video"),
               types.InlineKeyboardButton("🎵 صوت (MP3)", callback_data="audio"))
    bot.send_message(message.chat.id, "اختر الصيغة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def download_choice(call):
    url = user_links.get(call.message.chat.id)
    if not url: return
    bot.edit_message_text("⏳ جاري المعالجة، انتظر قليلاً...", call.message.chat.id, call.message.message_id)
    
    ext = 'mp4' if call.data == "video" else 'mp3'
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if call.data == "video" else 'bestaudio/best',
        'outtmpl': f'file_{call.message.chat.id}.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}] if call.data == "audio" else []
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if call.data == "audio": filename = filename.rsplit('.', 1)[0] + '.mp3'

        with open(filename, 'rb') as f:
            if call.data == "video": bot.send_video(call.message.chat.id, f, caption="تم التحميل بواسطة بوت أبو العصماء")
            else: bot.send_audio(call.message.chat.id, f, caption="تم التحويل بواسطة بوت أبو العصماء")
        os.remove(filename)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ خطأ: {str(e)}")

def activate_shield(message):
    token = message.text.strip()
    res = requests.post(f"https://graph.facebook.com/me/is_shielded?is_shielded=true&access_token={token}").json()
    if res.get('is_shielded') or res.get('success'):
        bot.send_message(message.chat.id, "✅ تم تفعيل الدرع!")
    else:
        bot.send_message(message.chat.id, "❌ فشل التفعيل.")

bot.infinity_polling()
  
