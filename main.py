import logging
import os
import threading
from flask import Flask
import requests
import telebot

DUCK_API_URL = "https://quack.duckduckgo.com/api/email/addresses"
REQUEST_TIMEOUT_SECONDS = 15

# Para que UptimeRobot pueda mantenerlo prendido
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot DESTROYER Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

BOT_TOKEN = required_env("BOT_TOKEN")
DUCK_TOKEN = os.getenv("DUCK_TOKEN") # Ya no es obligatorio para que no se caiga
bot = telebot.TeleBot(BOT_TOKEN)

def authorization_header(token: str) -> str:
    if not token:
        return ""
    token = token.strip().strip("\"'")
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return f"Bearer {token}"

def generate_duck_email():
    if not DUCK_TOKEN:
        return None
    try:
        response = requests.post(
            DUCK_API_URL,
            headers={
                "Authorization": authorization_header(DUCK_TOKEN),
                "Accept": "application/json",
                "Origin": "https://duckduckgo.com",
                "Referer": "https://duckduckgo.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        address = payload.get("address")
        if not isinstance(address, str) or not address.strip():
            return None
        address = address.strip()
        return address if "@" in address else f"{address}@duck.com"
    except Exception as e:
        logging.error(f"DUCK CAIDO: {e}")
        return None

@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.reply_to(message, "Hi! I can generate a random DuckDuckGo private email address for you.\nUse /email to get one.")

@bot.message_handler(commands=["email"])
def handle_email(message):
    email = generate_duck_email()
    if email is None:
        bot.reply_to(message, "⚠️ La página de Duck está en mantenimiento ahora, intenta en 10 min profe. El bot sigue prendido en verde, cuando Duck se arregle solo te da el correo.")
    else:
        bot.reply_to(message, f"Your random Duck address is:\n\n{email}")

if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="%(asctime)s %(levelname)s %(message)s")
    # Prende el servidor web para UptimeRobot
    threading.Thread(target=run_flask, daemon=True).start()
    logging.info("Starting Telegram bot")
    bot.infinity_polling()
