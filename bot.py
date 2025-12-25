import os
import json
from telegram.ext import Updater, CommandHandler
from syllabus import syllabus

TOKEN = os.environ.get("BOT_TOKEN")
PROGRESS_FILE = "progress.json"

# ---------- SAFE LOAD / SAVE ----------

def load_data():
    if not os.path.exists(PROGRESS_FILE):
        return {}

    try:
        with open(PROGRESS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except Exception:
        return {}


def save_data(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def ensure_user(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"index": 0}
    return data


# ---------- COMMANDS ----------

def start(update, context):
    user_id = update.effective_user.id
    data = ensure_user(load_data(), user_id)
    save_data(data)

    index = data[str(user_id)]["index"]
    update.message.reply_text(
        f"📚 GATE Planner – Step 4\n\n"
        f"📌 Current Topic:\n➡️ {syllabus[index]}\n\n"
        f"Commands:\n"
        f"/today – show current topic\n"
        f"/done – mark completed\n"
        f"/status – progress summary"
    )


def today_cmd(update, context):
    user_id = update.effective_user.id
    data = ensure_user(load_data(), user_id)

    index = data[str(user_id)]["index"]
    update.message.reply_text(
        f"📌 Today's Topic:\n➡️ {syllabus[index]}"
    )


def done(update, context):
    user_id = update.effective_user.id
    data = ensure_user(load_data(), user_id)

    index = data[str(user_id)]["index"] + 1

    if index >= len(syllabus):
        update.message.reply_text("🎉 Syllabus completed!")
        return

    data[str(user_id)]["index"] = index
    save_data(data)

    update.message.reply_text(
        f"✅ Completed!\n\n"
        f"➡️ Next Topic:\n{syllabus[index]}"
    )


def status(update, context):
    user_id = update.effective_user.id
    data = ensure_user(load_data(), user_id)

    completed = data[str(user_id)]["index"]
    total = len(syllabus)

    update.message.reply_text(
        f"📊 Progress Status\n\n"
        f"✅ Completed Topics: {completed}/{total}\n"
        f"📘 Current Topic:\n➡️ {syllabus[completed]}"
    )


# ---------- BOT START ----------

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("today", today_cmd))
    dp.add_handler(CommandHandler("done", done))
    dp.add_handler(CommandHandler("status", status))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
