import os
from telegram.ext import Updater, CommandHandler
from syllabus import syllabus

TOKEN = os.environ.get("BOT_TOKEN")

def start(update, context):
    update.message.reply_text(
        "📚 GATE Planner – Step 2\n\n"
        "Here is TODAY'S topic:\n\n"
        f"➡️ {syllabus[0]}\n\n"
        "Progress tracking will be added next."
    )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
