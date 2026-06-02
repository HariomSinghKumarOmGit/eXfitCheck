"""
Deployment Notes:
- This bot uses twscrape which requires no Twitter API key.
- Set all 5 env vars on Railway under the Variables tab.
- The bot runs as a worker (not a web service) — use the Procfile.
- accounts.db is created automatically on first run and stores the session.
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from twscrape import AccountsPool, API

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME")
TWITTER_PASSWORD = os.environ.get("TWITTER_PASSWORD")
TWITTER_EMAIL = os.environ.get("TWITTER_EMAIL", "")
TWITTER_EMAIL_PASSWORD = os.environ.get("TWITTER_EMAIL_PASSWORD", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def post_init(application: Application) -> None:
    """Initialize twscrape pool and login on bot startup."""
    logger.info("Initializing twscrape accounts...")
    pool = AccountsPool()
    await pool.add_account(
        TWITTER_USERNAME,
        TWITTER_PASSWORD,
        TWITTER_EMAIL,
        TWITTER_EMAIL_PASSWORD
    )
    await pool.login_all()
    application.bot_data["api"] = API(pool)
    logger.info("twscrape initialization complete.")

async def get_non_followers(api: API) -> list[dict]:
    """Fetch following and followers, return list of non-followers."""
    # Get user's numeric ID
    user_info = await api.user_by_login(TWITTER_USERNAME)
    if not user_info:
        raise ValueError(f"Could not find Twitter user: {TWITTER_USERNAME}")
    
    user_id = user_info.id
    
    logger.info(f"Fetching following for {TWITTER_USERNAME} ({user_id})...")
    # limit=5000 handles pagination automatically. Increase if you follow >5000 users.
    following_dict = {}
    async for user in api.following(user_id, limit=5000):
        following_dict[user.id] = user.username
    
    logger.info(f"Fetching followers for {TWITTER_USERNAME} ({user_id})...")
    follower_ids = set()
    async for user in api.followers(user_id, limit=5000):
        follower_ids.add(user.id)
    
    non_follower_ids = set(following_dict.keys()) - follower_ids
    
    non_followers = [
        {"id": str(uid), "username": following_dict[uid]}
        for uid in non_follower_ids
    ]
    
    non_followers.sort(key=lambda u: u["username"].lower())
    return non_followers

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /check command."""
    await update.message.reply_text("⏳ Fetching your Twitter data, please wait...")
    
    try:
        api = context.bot_data["api"]
        non_followers = await get_non_followers(api)
        
        count = len(non_followers)
        if count == 0:
            reply = "✅ Everyone you follow also follows you back!"
        else:
            lines = [f"🔍 Non-followers found: {count}\n"]
            for user in non_followers:
                lines.append(f"@{user['username']} (id: {user['id']})")
            
            reply = "\n".join(lines)
            if len(reply) > 4000:
                reply = reply[:4000] + "\n\n... (truncated)"
                
        await update.message.reply_text(reply)
        
    except Exception as exc:
        logger.exception("Error during /check command")
        await update.message.reply_text(f"❌ An error occurred while fetching data:\n{exc}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /start command."""
    welcome_text = (
        "👋 Welcome to the Twitter Unfollow Checker Bot!\n\n"
        "Send /check to see which accounts you follow but don't follow you back."
    )
    await update.message.reply_text(welcome_text)

def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("check", check_command))
    
    logger.info("Starting Telegram bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
