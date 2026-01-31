from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)
import os
import psycopg2
from datetime import date

TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    work_date DATE,
    a INTEGER, b INTEGER, c INTEGER, d INTEGER, x INTEGER,
    hours REAL,
    result REAL
)
""")
conn.commit()

def calculate(data):
    y = data["a"]*15 + data["b"] + data["c"]*2 + data["d"]*10 + data["x"]*80
    z = 800 * data["h"]
    i = y - z
    t = i / data["h"]
    return round(t / 100, 2), y, z, i

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    name = update.effective_user.first_name

    cur.execute("SELECT id FROM users WHERE telegram_id=%s", (tg_id,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (telegram_id, name) VALUES (%s,%s)",
            (tg_id, name)
        )
        conn.commit()

    keyboard = [["➕ Add"]]
    await update.message.reply_text(
        "Добро пожаловать 👋",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    context.user_data.clear()

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "➕ Add":
        context.user_data.clear()
        context.user_data["step"] = "a"
        await update.message.reply_text("Введите позиции:")
        return

    step = context.user_data.get("step")
    if not step:
        return

    try:
        value = float(text)
    except:
        await update.message.reply_text("Введите число")
        return

    if step == "a":
        context.user_data["a"] = int(value)
        context.user_data["step"] = "b"
        await update.message.reply_text("Введите штуки:")

    elif step == "b":
        context.user_data["b"] = int(value)
        context.user_data["step"] = "c"
        await update.message.reply_text("Введите килограммы:")

    elif step == "c":
        context.user_data["c"] = int(value)
        context.user_data["step"] = "d"
        await update.message.reply_text("Введите упаковки:")

    elif step == "d":
        context.user_data["d"] = int(value)
        context.user_data["step"] = "x"
        await update.message.reply_text("Введите заказы:")

    elif step == "x":
        context.user_data["x"] = int(value)
        context.user_data["step"] = "h"
        await update.message.reply_text("Введите часы:")

    elif step == "h":
        context.user_data["h"] = float(value)

        result, y, z, i = calculate(context.user_data)

        cur.execute(
            "SELECT id FROM users WHERE telegram_id=%s",
            (update.effective_user.id,)
        )
        user_id = cur.fetchone()[0]

        cur.execute("""
        INSERT INTO records
        (user_id, work_date, a,b,c,d,x,hours,result)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id, date.today(),
            context.user_data["a"],
            context.user_data["b"],
            context.user_data["c"],
            context.user_data["d"],
            context.user_data["x"],
            context.user_data["h"],
            result
        ))
        conn.commit()

        await update.message.reply_text(
            f"📊 Результат за {date.today()}:\n"
            f"Баллы: {y}\n"
            f"Норма: {z}\n"
            f"Разница: {i}\n"
            f"✅ Аккорд: {result} %"
        )

        context.user_data.clear()

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()
