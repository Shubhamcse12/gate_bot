import os
import json
from datetime import datetime, date
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters
)
from telegram import ReplyKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
from syllabus import syllabus

# ---------------- CONFIG ----------------

TOKEN = os.environ.get("BOT_TOKEN")
PROGRESS_FILE = "progress.json"
GATE_EXAM_DATE = date(2026, 2, 5)

SUBJECT_DAYS = {
    "Maths": 6,
    "DSA": 7,
    "C": 4,
    "Digital Logic": 6,
    "OS": 7,
    "DBMS": 6,
    "CN": 6,
    "TOC": 5,
    "Compiler": 5,
    "Revision & PYQs": 6
}

# ---------------- UTILITIES ----------------

def load_data():
    if not os.path.exists(PROGRESS_FILE):
        return {}
    try:
        with open(PROGRESS_FILE, "r") as f:
            text = f.read().strip()
            if not text:
                return {}
            return json.loads(text)
    except Exception:
        return {}

def save_data(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def detect_subject(topic):
    return topic.split(":")[0]

def ensure_user(user_id):
    data = load_data()
    uid = str(user_id)

    if uid not in data:
        subject = detect_subject(syllabus[0])
        data[uid] = {
            "index": 0,
            "subject": subject,
            "subject_days_used": 0,
            "last_update": None
        }
        save_data(data)

    return data

def keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📌 Today", "✅ Done"],
            ["📊 Status", "🔄 Reset"]
        ],
        resize_keyboard=True
    )

# ---------------- COMMANDS ----------------

def start(update, context):
    user_id = update.effective_user.id
    data = ensure_user(user_id)
    user = data[str(user_id)]

    topic = syllabus[user["index"]]
    subject = user["subject"]

    days_exam = (GATE_EXAM_DATE - date.today()).days
    days_subject = SUBJECT_DAYS[subject] - user["subject_days_used"]

    update.message.reply_text(
        f"📚 *GATE Planner*\n\n"
        f"📌 *Today's Topic:*\n➡️ {topic}\n\n"
        f"📘 Subject: {subject}\n"
        f"⏳ Subject days left: {days_subject}\n"
        f"🗓️ Days left for GATE: {days_exam}",
        reply_markup=keyboard(),
        parse_mode="Markdown"
    )

def today(update, context):
    start(update, context)

def done(update, context):
    user_id = update.effective_user.id
    data = ensure_user(user_id)
    user = data[str(user_id)]

    user["index"] += 1
    user["subject_days_used"] += 1
    user["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    if user["index"] >= len(syllabus):
        save_data(data)
        update.message.reply_text(
            "🎉 *Syllabus Completed!*\nNow focus on revision & mocks 🔥",
            parse_mode="Markdown"
        )
        return

    next_topic = syllabus[user["index"]]
    next_subject = detect_subject(next_topic)

    if next_subject != user["subject"]:
        user["subject"] = next_subject
        user["subject_days_used"] = 0

    save_data(data)

    update.message.reply_text(
        f"✅ *Completed!*\n\n"
        f"➡️ *Next Topic:*\n{next_topic}",
        reply_markup=keyboard(),
        parse_mode="Markdown"
    )

def status(update, context):
    user_id = update.effective_user.id
    data = ensure_user(user_id)
    user = data[str(user_id)]

    days_exam = (GATE_EXAM_DATE - date.today()).days
    days_subject = SUBJECT_DAYS[user["subject"]] - user["subject_days_used"]

    update.message.reply_text(
        f"📊 *Progress Status*\n\n"
        f"📘 Subject: {user['subject']}\n"
        f"📌 Topic: {syllabus[user['index']]}\n"
        f"⏳ Subject days left: {days_subject}\n"
        f"🗓️ Days left for GATE: {days_exam}\n"
        f"🕒 Last update: {user['last_update']}",
        reply_markup=keyboard(),
        parse_mode="Markdown"
    )

def reset(update, context):
    data = load_data()
    uid = str(update.effective_user.id)

    subject = detect_subject(syllabus[0])
    data[uid] = {
        "index": 0,
        "subject": subject,
        "subject_days_used": 0,
        "last_update": None
    }
    save_data(data)

    update.message.reply_text(
        "🔄 *Planner reset successfully!*",
        reply_markup=keyboard(),
        parse_mode="Markdown"
    )

# ---------------- BUTTON HANDLER ----------------

def button_handler(update, context):
    text = update.message.text
    if text == "📌 Today":
        today(update, context)
    elif text == "✅ Done":
        done(update, context)
    elif text == "📊 Status":
        status(update, context)
    elif text == "🔄 Reset":
        reset(update, context)

# ---------------- DAILY REMINDER ----------------

def daily_reminder(bot):
    data = load_data()
    for uid in data:
        index = data[uid]["index"]
        topic = syllabus[index]

        bot.send_message(
            chat_id=int(uid),
            text=f"⏰ Daily Reminder\n\n📌 Today's Topic:\n➡️ {topic}"
        )


# ---------------- BOT START ----------------

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("today", today))
    dp.add_handler(CommandHandler("done", done))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))

    scheduler = BackgroundScheduler()
    scheduler.add_job(
    daily_reminder,
    "cron",
    hour=7,
    minute=0,
    args=[updater.bot]
    )
    scheduler.start()


if __name__ == "__main__":
    main()
