import os
import json
from datetime import datetime, date
from telegram.ext import Updater, CommandHandler
from syllabus import syllabus

# ---------------- CONFIG ----------------

TOKEN = os.environ.get("BOT_TOKEN")
PROGRESS_FILE = "progress.json"
EXAM_DATE = date(2026, 2, 5)

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
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_subject(topic):
    return topic.split(":")[0]


def get_user(user_id):
    data = load_data()
    uid = str(user_id)

    if uid not in data:
        first_subject = get_subject(syllabus[0])
        data[uid] = {
            "current_index": 0,
            "current_subject": first_subject,
            "subject_day_used": 0,
            "completed": [],
            "last_updated": None
        }
        save_data(data)

    return data


# ---------------- COMMANDS ----------------

def start(update, context):
    user_id = update.effective_user.id
    data = get_user(user_id)
    user = data[str(user_id)]

    today = date.today()
    days_left_exam = (EXAM_DATE - today).days
    topic = syllabus[user["current_index"]]
    subject = user["current_subject"]

    update.message.reply_text(
        f"📚 GATE Planner Started\n\n"
        f"📌 Today's Topic:\n➡️ {topic}\n\n"
        f"📘 Subject: {subject}\n"
        f"⏳ Days left for subject: {SUBJECT_DAYS[subject] - user['subject_day_used']}\n"
        f"🗓️ Days left for GATE: {days_left_exam}\n\n"
        f"Use /done after completion."
    )


def today_cmd(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data[str(user_id)]

    today = date.today()
    subject = user["current_subject"]

    update.message.reply_text(
        f"📌 Current Topic:\n➡️ {syllabus[user['current_index']]}\n\n"
        f"📘 Subject: {subject}\n"
        f"⏳ Days left for subject: {SUBJECT_DAYS[subject] - user['subject_day_used']}\n"
        f"🗓️ Days left for GATE: {(EXAM_DATE - today).days}"
    )


def done(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data[str(user_id)]

    if user["current_index"] >= len(syllabus):
        update.message.reply_text("🎉 Syllabus already completed!")
        return

    completed_topic = syllabus[user["current_index"]]
    current_subject = get_subject(completed_topic)

    user["completed"].append(completed_topic)
    user["current_index"] += 1
    user["subject_day_used"] += 1
    user["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    if user["current_index"] < len(syllabus):
        next_topic = syllabus[user["current_index"]]
        next_subject = get_subject(next_topic)

        if next_subject != current_subject:
            user["current_subject"] = next_subject
            user["subject_day_used"] = 0

        save_data(data)

        update.message.reply_text(
            f"✅ Completed:\n{completed_topic}\n\n"
            f"➡️ Next Topic:\n{next_topic}\n"
            f"⏳ Days left for {user['current_subject']}: "
            f"{SUBJECT_DAYS[user['current_subject']] - user['subject_day_used']}"
        )
    else:
        save_data(data)
        update.message.reply_text("🎯 Syllabus Completed!\nNow focus on revision & mocks 🔥")


def status(update, context):
    user_id = update.effective_user.id
    data = load_data()
    user = data[str(user_id)]

    today = date.today()

    update.message.reply_text(
        f"📊 Progress Status\n\n"
        f"✅ Completed Topics: {len(user['completed'])}/{len(syllabus)}\n"
        f"📘 Current Subject: {user['current_subject']}\n"
        f"⏳ Subject Days Left: "
        f"{SUBJECT_DAYS[user['current_subject']] - user['subject_day_used']}\n"
        f"🗓️ Days Left for GATE: {(EXAM_DATE - today).days}\n"
        f"🕒 Last Update: {user['last_updated']}"
    )


def reset(update, context):
    user_id = update.effective_user.id
    data = load_data()

    first_subject = get_subject(syllabus[0])
    data[str(user_id)] = {
        "current_index": 0,
        "current_subject": first_subject,
        "subject_day_used": 0,
        "completed": [],
        "last_updated": None
    }
    save_data(data)

    update.message.reply_text("🔄 Planner reset successfully!")


# ---------------- BOT INIT ----------------

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("today", today_cmd))
dp.add_handler(CommandHandler("done", done))
dp.add_handler(CommandHandler("status", status))
dp.add_handler(CommandHandler("reset", reset))

updater.start_polling()
updater.idle()
