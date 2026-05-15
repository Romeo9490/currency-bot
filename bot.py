import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
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

# Кнопка отмены
cancel_keyboard = ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True)

async def start(update, context):
    await update.message.reply_text(
        "🏦 <b>Кредитный калькулятор</b>\n\n"
        "Введи сумму кредита (руб):",
        parse_mode="HTML",
        reply_markup=cancel_keyboard
    )
    return SUMMA

async def summa_handler(update, context):
    if update.message.text == "❌ Отмена":
        await cancel(update, context)
        return ConversationHandler.END
    
    try:
        suma = float(update.message.text.replace(" ", ""))
        context.user_data['summa'] = suma
        await update.message.reply_text(
            f"✅ Сумма: {suma:,.0f} руб\n\n"
            "Введи срок кредита (месяцев):"
        )
        return SROK
    except:
        await update.message.reply_text("❌ Ошибка! Введи число, например: 1000000")
        return SUMMA

async def srok_handler(update, context):
    if update.message.text == "❌ Отмена":
        await cancel(update, context)
        return ConversationHandler.END
    
    try:
        srok = int(update.message.text)
        context.user_data['srok'] = srok
        await update.message.reply_text(
            f"✅ Срок: {srok} мес\n\n"
            "Введи процентную ставку (%):"
        )
        return PROCENT
    except:
        await update.message.reply_text("❌ Ошибка! Введи целое число, например: 12")
        return SROK

async def proce_handler(update, context):
    if update.message.text == "❌ Отмена":
        await cancel(update, context)
        return ConversationHandler.END
    
    try:
        proce = float(update.message.text.replace(",", "."))
        suma = context.user_data['summa']
        srok = context.user_data['srok']
        
        # ТВОЯ ФОРМУЛА (полностью скопирована из твоего кода)
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
        
        result = f"🏦 <b>РЕЗУЛЬТАТ РАСЧЁТА</b>\n\n"
        result += f"💰 Сумма: {suma:,.0f} руб\n"
        result += f"📅 Срок: {srok} мес\n"
        result += f"📈 Ставка: {proce}%\n\n"
        result += f"📊 <b>Ежемесячный платёж:</b> {round(ezhe, 1)} руб\n\n"
        result += f"📋 <b>Первый платёж:</b>\n"
        result += f"   Проценты: {nach_proc:.1f} руб\n"
        result += f"   Погашение долга: {osnov:.1f} руб\n\n"
        result += f"📉 <b>Переплата по процентам:</b> {vse:.1f} руб\n"
        result += f"💰 <b>Всего выплачено:</b> {perep:.1f} руб"
        
        await update.message.reply_text(result, parse_mode="HTML")
        await update.message.reply_text(
            "🔄 Новый расчёт: /start",
            reply_markup=ReplyKeyboardMarkup.remove_keyboard()
        )
        return ConversationHandler.END
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка! Попробуй ещё раз")
        return PROCENT

async def cancel(update, context):
    await update.message.reply_text(
        "❌ Расчёт отменён.\nДля нового расчёта /start",
        reply_markup=ReplyKeyboardMarkup.remove_keyboard()
    )
    return ConversationHandler.END

async def help_command(update, context):
    await update.message.reply_text(
        "🏦 <b>Кредитный калькулятор</b>\n\n"
        "/start - начать новый расчёт\n"
        "/help - эта справка\n\n"
        "Бот рассчитывает аннуитетные платежи по кредиту.",
        parse_mode="HTML"
    )

def run_bot():
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SUMMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, summa_handler)],
            SROK: [MessageHandler(filters.TEXT & ~filters.COMMAND, srok_handler)],
            PROCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, proce_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    print("🏦 Кредитный бот запущен!")
    application.run_polling()

if name == "__main__":
    from threading import Thread
    Thread(target=run_flask).start()
    run_bot()
