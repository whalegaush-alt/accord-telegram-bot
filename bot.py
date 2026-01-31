from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")

def calculate(a, b, c, d, x, h):
    y = a*15 + b + c*2 + d*10 + x*80
    z = 800 * h
    i = y - z
    t = i / h
    return round(t / 100, 2), y, z, i

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Введи данные в формате:\n"
        "a b c d x часы\n\n"
        "Пример:\n165 1867 553 379 10 11"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        a, b, c, d, x, h = map(float, update.message.text.split())
        result, y, z, i = calculate(a, b, c, d, x, h)

        await update.message.reply_text(
            f"📊 Результат:\n"
            f"Баллы: {y}\n"
            f"Норма: {z}\n"
            f"Разница: {i}\n"
            f"Аккорд: {result} %"
        )
    except:
        await update.message.reply_text(
            "❌ Ошибка ввода\n"
            "Формат:\n"
            "a b c d x часы"
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
