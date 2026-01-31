from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os

TOKEN = os.getenv("BOT_TOKEN")

# ====== ФОРМУЛА ======
def calculate(data):
    y = (
        data["a"] * 15 +
        data["b"] +
        data["c"] * 2 +
        data["d"] * 10 +
        data["x"] * 80
    )
    z = 800 * data["h"]
    i = y - z
    t = i / data["h"]
    return round(t / 100, 2), y, z, i


# ====== /START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["➕ Add"]]
    await update.message.reply_text(
        "Добро пожаловать 👋\nНажми кнопку, чтобы добавить данные",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    context.user_data.clear()


# ====== ОБРАБОТКА ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Нажали ADD
    if text == "➕ Add":
        context.user_data.clear()
        context.user_data["step"] = "a"
        await update.message.reply_text("Введите количество позиций:")
        return

    step = context.user_data.get("step")

    try:
        value = float(text)
    except:
        await update.message.reply_text("❌ Введите число")
        return

    if step == "a":
        context.user_data["a"] = value
        context.user_data["step"] = "b"
        await update.message.reply_text("Введите штуки:")
    
    elif step == "b":
        context.user_data["b"] = value
        context.user_data["step"] = "c"
        await update.message.reply_text("Введите килограммы:")
    
    elif step == "c":
        context.user_data["c"] = value
        context.user_data["step"] = "d"
        await update.message.reply_text("Введите упаковки:")
    
    elif step == "d":
        context.user_data["d"] = value
        context.user_data["step"] = "x"
        await update.message.reply_text("Введите заказы:")
    
    elif step == "x":
        context.user_data["x"] = value
        context.user_data["step"] = "h"
        await update.message.reply_text("Введите отработанные часы:")
    
    elif step == "h":
        context.user_data["h"] = value

        result, y, z, i = calculate(context.user_data)

        await update.message.reply_text(
            f"📊 Результат:\n"
            f"Баллы: {y}\n"
            f"Норма: {z}\n"
            f"Разница: {i}\n"
            f"Аккорд: {result} %"
        )

        context.user_data.clear()


# ====== ЗАПУСК ======
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
