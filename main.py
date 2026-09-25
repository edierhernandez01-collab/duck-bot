import logging
import os

import requests
import telebot


DUCK_API_URL = "https://quack.duckduckgo.com/api/email/addresses"
REQUEST_TIMEOUT_SECONDS = 15


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


BOT_TOKEN = required_env("BOT_TOKEN")
DUCK_TOKEN = required_env("DUCK_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


def generate_duck_email() -> str:
    response = requests.post(
        DUCK_API_URL,
        headers={
            "Authorization": f"Bearer {DUCK_TOKEN}",
            "Accept": "application/json",
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    payload = response.json()
    address = payload.get("address")
    if not isinstance(address, str) or not address.strip():
        raise ValueError("DuckDuckGo returned an unexpected response")

    address = address.strip()
    return address if "@" in address else f"{address}@duck.com"


@bot.message_handler(commands=["start"])
def handle_start(message: telebot.types.Message) -> None:
    bot.reply_to(
        message,
        "Hi! I can generate a random DuckDuckGo private email address for you.\n"
        "Use /email to get one.",
    )


@bot.message_handler(commands=["email"])
def handle_email(message: telebot.types.Message) -> None:
    try:
        email = generate_duck_email()
    except requests.RequestException:
        logging.exception("DuckDuckGo API request failed")
        bot.reply_to(
            message,
            "I couldn't generate an email address right now. Please try again later.",
        )
    except (ValueError, TypeError):
        logging.exception("DuckDuckGo API returned an invalid response")
        bot.reply_to(
            message,
            "DuckDuckGo returned an invalid response. Please try again later.",
        )
    else:
        bot.reply_to(message, f"Your random Duck address is:\n\n{email}")


if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.info("Starting Telegram bot")
    bot.infinity_polling()