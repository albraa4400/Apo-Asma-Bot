import telebot
import os
import yt_dlp
import sqlite3
from flask import Flask
from threading import Thread

# 1. إعداد السيرفر للبقاء حياً
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, downloads INTEGER)''')
    # إدخال قيمة أولية للعداد إذا لم توجد
    c.execute('''INSERT OR IGNORE INTO stats (id, downloads) VALUES (1, 0)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def increment_downloads():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE stats SET downloads = downloads + 1 WHERE id = 1")
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT downloads FROM stats WHERE id = 1")
    total_downloads = c.fetchone()[0]
    conn.close()
    return total_users, total_downloads

# 3. إعداد البوت
API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA'
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 123456789  # ضع هنا الـ ID الخاص بك لتتمكن من رؤية الإحصائيات (اختياري)

init_db()

# 4. دالة التحميل
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# 5. الأوامر والمعالجة
@bot.message_handler(commands=['start'])
def welcome(message):
    add_user(message.chat.id)
    bot.reply_to(message, "أهلاً بك في بوت أبو العصماء! أرسل لي أي رابط فيديو وسأقوم بتحميله.")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    # يمكنك إضافة شرط ليظهر لك أنت فقط
    u_count, d_count = get_stats()
    bot.reply_to(message, f"📊 إحصائيات البوت:\n\n👥 عدد المستخدمين: {u_count}\n📥 عدد التحميلات الناجحة: {d_count}")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_download(message):
    add_user(message.chat.id)
    msg = bot.reply_to(message, "⏳ جاري المعالجة...")
    try:
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')
            
        download_video(message.text)
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="تم التحميل بواسطة بوت أبو العصماء 🚀")
        
        increment_downloads() # زيادة العداد بعد النجاح
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"حدث خطأ: {str(e)}", message.chat.id, msg.message_id)

if __name__ == "__main__":
    keep_alive()
    print("البوت يعمل بنظام قاعدة البيانات...")
    bot.infinity_polling()
    
