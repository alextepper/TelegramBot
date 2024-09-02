import os
from flask import Flask, request
import telebot

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found. Set the BOT_TOKEN environment variable.")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)


@app.route("/" + BOT_TOKEN, methods=["POST"])
def get_message():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/", methods=["GET"])
def index():
    return "Hello, this is the bot server!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
