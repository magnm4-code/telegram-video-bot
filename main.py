import telebot
import yt_dlp
import os
import threading
from flask import Flask

# --- 1. The Dummy Web Server ---
app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "Bot is awake and running!"

def run_server():
    # Render assigns a specific port, so we must use it
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. The Telegram Bot ---
# Pulls the token securely from Render's environment variables
TOKEN = os.environ.get('BOT_TOKEN') 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a video URL, and I will download it.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if not url.startswith('http'):
        bot.reply_to(message, "Please send a valid URL.")
        return

    bot.reply_to(message, "Processing your link... This might take a moment.")
    
 ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['android']}}
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info_dict)
            
        with open(video_file, 'rb') as video:
            bot.send_video(message.chat.id, video)
            
        os.remove(video_file) 
        
    except Exception as e:
        bot.reply_to(message, "Sorry, I couldn't download that video. It might be too large or private.")
        print(f"Error: {e}")

if __name__ == "__main__":
    # Start the web server in the background
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    # Start the bot
    print("Bot is running...")

    bot.infinity_polling()

