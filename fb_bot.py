import telebot
import os
import yt_dlp
import sqlite3
from flask import Flask
from threading import Thread
from telebot import types

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

# 2. إعداد قاعدة البيانات والمدير
ADMIN_ID = 1201544149  # الـ ID الخاص بك يا أبو العصماء

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, downloads INTEGER)''')
    c.execute('''INSERT OR IGNORE INTO stats (id, downloads) VALUES (1, 0)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

# 3. إعداد البوت
API_TOKEN = '8753502535:AAHmcXsDQnQUhW9rAdGERO2-L0rlIjDQJMA'
bot = telebot.TeleBot(API_TOKEN)
init_db()

# 4. لوحة المفاتيح (الأزرار)
def main_markup():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("👨‍💻 المطور", url="https://t.me/albraamohamed12")
    btn2 = types.InlineKeyboardButton("📢 قناة التحديثات", url="https://facebook.com/ApoAsma") # يمكنك تغيير الرابط
    markup.add(btn1, btn2)
    return markup

# 5. الأوامر
@bot.message_handler(commands=['start'])
def welcome(message):
    add_user(message.chat.id)
    bot.send_message(message.chat.id, 
                     f"مرحباً بك {message.from_user.first_name} في بوت أبو العصماء الخارق! 🤖\n\nأرسل رابط الفيديو الآن واستلم التحميل فوراً.",
                     reply_markup=main_markup())

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.chat.id == ADMIN_ID:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        u_count = c.fetchone()[0]
        c.execute("SELECT downloads FROM stats WHERE id = 1")
        d_count = c.fetchone()[0]
        conn.close()
        bot.reply_to(message, f"📊 إحصائيات الإدارة:\n👥 المستخدمين: {u_count}\n📥 التحميلات: {d_count}")
    else:
        bot.reply_to(message, "عذراً، هذا الأمر للمدير فقط.")

# ميزة الإذاعة (للمدير فقط)
@bot.message_handler(commands=['send'])
def broadcast(message):
    if message.chat.id == ADMIN_ID:
        text = message.text.replace('/send ', '')
        if text == '/send':
            bot.reply_to(message, "يرجى كتابة نص الرسالة بعد الأمر. مثال:\n`/send مرحبا بكم`")
            return
            
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        users = c.fetchall()
        conn.close()
        
        success = 0
        for user in users:
            try:
                bot.send_message(user[0], text)
                success += 1
            except:
                continue
        bot.reply_to(message, f"✅ تمت الإذاعة بنجاح لـ {success} مستخدم.")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_download(message):
    add_user(message.chat.id)
    msg = bot.reply_to(message, "⏳ جاري التحميل...")
    try:
        if os.path.exists('video.mp4'): os.remove('video.mp4')
        
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message.text])
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="تم التحميل بواسطة بوت أبو العصماء ✅")
        
        # زيادة عداد التحميلات
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE stats SET downloads = downloads + 1 WHERE id = 1")
        conn.commit()
        conn.close()
        
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: تأكد من الرابط.", message.chat.id, msg.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
        
