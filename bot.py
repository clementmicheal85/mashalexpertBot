import os
import logging
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# --- CONFIGURATION ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", "8080"))

# Define Conversation States
QUESTION_STAGE = range(1)

# The 7 Digital Marketing Questions
MARKETING_QUESTIONS = [
    "1. What does SEO stand for?",
    "2. True or False: Email marketing has the highest ROI of any digital channel.",
    "3. Which social platform is best for B2B lead generation?",
    "4. What is a 'Call to Action' (CTA)?",
    "5. What is the main purpose of a 'Landing Page'?",
    "6. What does PPC stand for in advertising?",
    "7. Final Question: Which tool is most commonly used for website analytics?"
]

# Simple In-memory storage
user_progress = {}

# --- WEB SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web_server():
    app.run(host='0.0.0.0', port=PORT)

# --- BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Updated: Specific message requested by the user
    await update.message.reply_text("this bot is built by clement so it will work on render")

    # Initialize user data if not exists
    if user_id not in user_progress:
        user_progress[user_id] = {"count": 0}

    count = user_progress[user_id]["count"]

    if count >= 7:
        await update.message.reply_text(
            "🚀 You have completed all 7 questions for this week!\n\n"
            "Please come back next week for a new challenge. Stay tuned!"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        f"Welcome to the Digital Marketing Challenge! 🎯\n\nQuestion {count + 1}:\n{MARKETING_QUESTIONS[count]}"
    )
    return QUESTION_STAGE

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_progress:
        user_progress[user_id] = {"count": 0}
        
    user_data = user_progress[user_id]
    
    # Move to next question
    user_data["count"] += 1
    count = user_data["count"]

    if count < 7:
        await update.message.reply_text(
            f"Got it! Next one...\n\nQuestion {count + 1}:\n{MARKETING_QUESTIONS[count]}"
        )
        return QUESTION_STAGE
    else:
        await update.message.reply_text(
            "✅ That was the 7th question! You are all done for now.\n\n"
            "Come back next week for a brand new set of challenges! Goodbye!"
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Challenge cancelled. Type /start to try again.")
    return ConversationHandler.END

def main():
    # Start the web server in a background thread
    Thread(target=run_web_server).start()

    # Build the Telegram Application
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUESTION_STAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
