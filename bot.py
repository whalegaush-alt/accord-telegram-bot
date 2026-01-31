from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import os
import sqlite3
from datetime import date

TOKEN = os.getenv("BOT_TOKEN")

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect("firm.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    work_date TEXT,
    a INTEGER, b INTEGER, c INTEGER, d INTEGER, x INTEGER,
    hours REAL,
    result REAL
)
""")
conn.commit()

# --- ФОРМУЛА ---
def calculate(a, b, c, d, x, h):
    y = a*15 + b + c*2 + d*10 + x*80
    z = 800 * h
    i = y - z
    t = i / h
    return round(t / 100, 2), y, z, i

# --- КОМАНДЫ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    name = update.effective_user.first_name

    cur.execute("SELECT id FROM users WHERE telegram_id=?", (tg_id,))
    user = cur.fetchone()

    if not user:
        cur.execute(
            "INSERT INTO users (telegram_id, name) VALUES (?,?)",
            (tg_id, name)
        )
        conn.commit()
        await update.message.reply_text(
            f"👋 Привет, {name}\nТы зарегистрирован как сотрудник.\n\n"
            "Ввод данных:\n/add a b c d x часы"
        )
    else:
        await update.message.reply_text(
            "👋 Ты уже зарегистрирован.\n"
            "Ввод данных:\n/add a b c d x часы"
        )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        a, b, c, d, x, h = map(float, context.args)
        result, y, z, i = calculate(a, b, c, d, x, h)

        cur.execute(
            "SELECT id FROM users WHERE telegram_id=?",
            (update.effective_user.id,)
        )
        user_id = cur.fetchone()[0]

        cur.execute("""
        INSERT INTO records
        (user_id, work_date, a, b, c, d, x, hours, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, str(date.today()),
            a, b, c, d, x, h, result
        ))
        conn.commit()

        await update.message.reply_text(
            f"📅 Дата: {date.today()}\n"
            f"Баллы: {y}\n"
            f"Норма: {z}\n"
            f"Разница: {i}\n"
            f"✅ Аккорд: {result} %"
        )
    except:
        await update.message.reply_text(
            "❌ Формат неверный\n"
            "Используй:\n/add a b c d x часы"
        )

async def my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur.execute("""
    SELECT work_date, result
    FROM records r
    JOIN users u ON r.user_id = u.id
    WHERE u.telegram_id=?
    ORDER BY work_date DESC
    LIMIT 7
    """, (update.effective_user.id,))

    rows = cur.fetchall()

    if not rows:
        await update.message.reply_text("📭 Пока нет данных")
        return

    text = "📊 Последние дни:\n"
    for d, r in rows:
        text += f"{d} → {r} %\n"

    await update.message.reply_text(text)

# --- ЗАПУСК ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("my", my))
    app.run_polling()

if __name__ == "__main__":
    main()
