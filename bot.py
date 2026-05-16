import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters

TOKEN = os.environ.get("TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "Кредитный бот работает!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ========== КОД БОТА ==========
SUMMA, SROK, PROCENT = range(3)

async def start(update, context):
    await update.message.reply_text("🏦 Введи сумму кредита (руб):")
    return SUMMA

async def summa_handler(update, context):
    try:
        suma = float(update.message.text.replace(" ", ""))
        context.user_data['summa'] = suma
        await update.message.reply_text(f"✅ Сумма: {suma:,.0f} руб\n\nВведи срок (месяцев):")
        return SROK
    except:
        await update.message.reply_text("❌ Введи число!")
        return SUMMA

async def srok_handler(update, context):
    try:
        srok = int(update.message.text)
        context.user_data['srok'] = srok
        await update.message.reply_text(f"✅ Срок: {srok} мес\n\nВведи процентную ставку (%):")
        return PROCENT
    except:
        await update.message.reply_text("❌ Введи число!")
        return SROK

async def proce_handler(update, context):
    try:
        proce = float(update.message.text.replace(",", "."))
        suma = context.user_data['summa']
        srok = context.user_data['srok']
        
        a = proce / 12 / 100
        b = (1 + a) ** srok
        c = a * b
        c_1 = b - 1
        f = c / c_1
        ezhe = suma * f
        
        result = f"🏦 РЕЗУЛЬТАТ\n💰 Сумма: {suma:,.0f} руб\n📅 Срок: {srok} мес\n📈 Ставка: {proce}%\n📊 Платёж: {round(ezhe, 1)} руб"
        
        await update.message.reply_text(result)
        await update.message.reply_text("🔄 /start - новый расчёт")
        return ConversationHandler.END
    except:
        await update.message.reply_text("❌ Ошибка! /start")
        return PROCENT

async def cancel(update, context):
    await update.message.reply_text("❌ Отменено. /start")
    return ConversationHandler.END

def run_bot():
    application = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SUMMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, summa_handler)],
            SROK: [MessageHandler(filters.TEXT & ~filters.COMMAND, srok_handler)],
            PROCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, proce_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv)
    print("✅ Кредитный бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()