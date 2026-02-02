import os
import psycopg2
from datetime import date
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def calculate(data):
    y = data["a"] * 15 + data["b"] + data["c"] * 2 + data["d"] * 10 + data["x"] * 80
    z = 800 * data["h"]
    i = y - z
    t = i / data["h"]
    result = round(t / 100, 2)
    return result, y, z, i


def get_or_create_user(telegram_id, name):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE telegram_id = %s",
        (telegram_id,)
    )
    row = cur.fetchone()

    if row:
        user_id = row[0]
    else:
        cur.execute(
            "INSERT INTO users (telegram_id, name) VALUES (%s, %s) RETURNING id",
            (telegram_id, name)
        )
        user_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return user_id


def save_record(user_id, data, result):
    print("👉 SAVE_RECORD CALLED")
    print("👉 DATABASE_URL =", DATABASE_URL)

    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cur = conn.cursor()

    cur.execute("SELECT current_database(), current_schema();")
    print("👉 DB INFO =", cur.fetchone())

    cur.execute("""
        INSERT INTO records
        (user_id, work_date, a, b, c, d, x, hours, result)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        date.today(),
        data["a"],
        data["b"],
        data["c"],
        data["d"],
        data["x"],
        data["h"],
        result
    ))

    conn.commit()
    print("✅ COMMIT DONE")

    cur.close()
    conn.close()

# ---------- ХЕНДЛЕРЫ ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["➕ Add"]]
    await update.message.reply_text(
        "Добро пожаловать 👋\nНажмите ➕ Add для ввода данных",
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
    except ValueError:
        await update.message.reply_text("❌ Введите число")
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

        user_id = get_or_create_user(
            update.effective_user.id,
            update.effective_user.first_name
        )

        save_record(user_id, context.user_data, result)

        await update.message.reply_text(
            f"📊 Результат за {date.today()}:\n"
            f"Баллы: {y}\n"
            f"Норма: {z}\n"
            f"Разница: {i}\n"
            f"✅ Аккорд: {result} %"
        )

        context.user_data.clear()

# ---------- ЗАПУСК ----------

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()


if __name__ == "__main__":
    main()
