import os
import requests
from datetime import datetime
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.environ.get("TOKEN")  # Токен из переменных окружения

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Твои функции бота
def get_currency_rates():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data["Valute"], None
    except Exception as e:
        return None, str(e)

async def start(update, context):
    await update.message.reply_text("💱 Валютный бот работает!\nКоманда /course")

async def course(update, context):
    valutes, error = get_currency_rates()
    if error:
        await update.message.reply_text(f"❌ {error}")
        return
    
    usd = valutes["USD"]
    eur = valutes["EUR"]
    
    await update.message.reply_text(
        f"🏦 КУРС ВАЛЮТ\n\n"
        f"💵 Доллар: {usd['Value']:.2f} ₽\n"
        f"💶 Евро: {eur['Value']:.2f} ₽\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("course", course))
    application.run_polling()

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке (для Render)
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    # Запускаем бота
    run_bot()