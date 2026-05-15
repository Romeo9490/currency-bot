import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

TOKEN = os.environ.get("TOKEN")
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def home():
    return "Кредитный бот работает!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Этапы разговора
SUMMA, SROK, PROCENT = range(3)

async def start(update: Update, context):
    await update.message.reply_text(
        "🏦 <b>Кредитный калькулятор</b>\n\n"
        "Введи сумму кредита (руб):",
        parse_mode="HTML"
    )
    return SUMMA

async def summa_handler(update: Update, context):
    try:
        suma = float(update.message.text.replace(" ", ""))
        context.user_data['summa'] = suma
        await update.message.reply_text(
            f"✅ Сумма: {suma:,.0f} руб\n\n"
            "Введи срок кредита (месяцев):"
        )
        return SROK
    except:
        await update.message.reply_text("❌ Ошибка! Введи число")
        return SUMMA

async def srok_handler(update: Update, context):
    try:
        srok = int(update.message.text)
        context.user_data['srok'] = srok
        await update.message.reply_text(
            f"✅ Срок: {srok} мес\n\n"
            "Введи процентную ставку (%):"
        )
        return PROCENT
    except:
        await update.message.reply_text("❌ Ошибка! Введи целое число")
        return SROK

async def proce_handler(update: Update, context):
    try:
        proce = float(update.message.text.replace(",", "."))
        suma = context.user_data['summa']
        srok = context.user_data['srok']
        
        # Расчёт
        a = proce / 12 / 100
        b = (1 + a) ** srok
        c = a * b
        c_1 = b - 1
        f = c / c_1
        ezhe = suma * f
        
        nach_proc = suma * proce / 100 / 12
        osnov = ezhe - nach_proc
        perep = ezhe * srok
        vse = perep - suma
        
        result = f"🏦 <b>РЕЗУЛЬТАТ</b>\n\n"
        result += f"💰 Сумма: {suma:,.0f} руб\n"
        result += f"📅 Срок: {srok} мес\n"
        result += f"📈 Ставка: {proce}%\n"
        result += f"📊 Платёж: {round(ezhe, 1)} руб\n"
        result += f"📉 Переплата: {vse:.1f} руб\n"
        result += f"💰 Всего: {perep:.1f} руб"
        
        await update.message.reply_text(result, parse_mode="HTML")
        await update.message.reply_text("🔄 /start - новый расчёт")
        return ConversationHandler.END
        
    except:
        await update.message.reply_text("❌ Ошибка! Попробуй ещё")
        return PROCENT

async def cancel(update: Update, context):
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
    print("🏦 Кредитный бот запущен!")
    application.run_polling()

# ГЛАВНОЕ — ПРАВИЛЬНАЯ строчка с двумя подчёркиваниями!
if name == "__main__":
    Thread(target=run_flask).start()
    run_bot()
