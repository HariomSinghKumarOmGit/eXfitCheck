# Twitter Unfollow Checker Bot

A Telegram bot that tells you which Twitter/X accounts you follow but don't follow you back.
Send `/check` in Telegram and get the full list instantly.

---

## File Structure

```
twitter-unfollow-bot/
├── main.py           # Bot logic
├── requirements.txt  # Python dependencies
├── Procfile          # Railway deployment config
├── .env.example      # Template for environment variables
└── README.md
```

---

## Step 1 — Get Your Twitter/X API Keys

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Sign in with your Twitter/X account.
3. Click **"Sign up for Free Account"** if you don't have a developer account yet.
   - Fill in the use-case form (say something like "personal project to manage my own follows").
   - Accept the terms and submit.
4. Once approved, you land on the **Developer Portal Dashboard**.
5. Click **"+ Create Project"**:
   - Project name: `unfollow-checker` (or anything)
   - Use case: **Exploring the API**
   - Description: "Check my own following/followers lists"
6. Inside the project, click **"+ Add App"** → give it a name → click **"Create".
7. On the next screen you'll see your keys. Copy and save:
   - **Bearer Token** → this is your `TWITTER_BEARER_TOKEN`
8. ✅ That's all you need for read-only access to your own lists.

> **Note:** The Free tier allows reading your own followers/following. No credit card needed.

---

## Step 2 — Find Your Twitter Numeric User ID

Your user ID is a long number (e.g. `783214`), completely different from your @username.

**Easiest method — use tweeterid.com:**
1. Go to https://tweeterid.com
2. Type your @username and click **Convert**.
3. Copy the number shown — that's your `TWITTER_MY_USER_ID`.

**Alternative — Twitter API itself:**
```bash
curl -s "https://api.twitter.com/2/users/by/username/YOUR_USERNAME" \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN"
```
The `id` field in the JSON response is your numeric user ID.

---

## Step 3 — Create a Telegram Bot & Get Its Token

1. Open Telegram and search for **@BotFather** (it has a blue verified checkmark).
2. Start a chat and send `/newbot`.
3. BotFather asks for:
   - **A name** for your bot (e.g. `My Unfollow Checker`)
   - **A username** ending in `bot` (e.g. `myunfollowchecker_bot`)
4. BotFather replies with a **token** that looks like:
   ```
   123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
   ```
5. Copy that — it's your `TELEGRAM_BOT_TOKEN`.
6. Click the link BotFather gives you to open your new bot, then send `/start` to activate it.

---

## Step 4 — Local Testing (Optional)

```bash
# Clone / create the project folder, then:
cd twitter-unfollow-bot

# Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the example env file and fill in your values
cp .env.example .env
nano .env   # or open in any editor

# Run the bot
python main.py
```

Open Telegram, find your bot, and send `/check`.

---

## Step 5 — Deploy on Railway (Free Tier)

Railway gives you a free hobby plan with enough hours to run this bot continuously.

### 5.1 — Push your code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
# Create a repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/twitter-unfollow-bot.git
git push -u origin main
```

> **Important:** Make sure `.env` is in your `.gitignore` so you never push secrets.
> Create `.gitignore` with this content:
> ```
> .env
> venv/
> __pycache__/
> *.pyc
> ```

### 5.2 — Create a Railway Project

1. Go to https://railway.app and sign in with GitHub.
2. Click **"New Project"** → **"Deploy from GitHub repo"**.
3. Select your `twitter-unfollow-bot` repo.
4. Railway detects the `Procfile` automatically.

### 5.3 — Add Environment Variables

1. Inside your Railway project, click on the service card.
2. Go to the **"Variables"** tab.
3. Add each variable:

   | Variable | Value |
   |---|---|
   | `TWITTER_BEARER_TOKEN` | your bearer token |
   | `TWITTER_MY_USER_ID` | your numeric user ID |
   | `TELEGRAM_BOT_TOKEN` | your Telegram bot token |

4. Click **"Deploy"** (or Railway will auto-deploy on save).

### 5.4 — Verify It's Running

- Go to the **"Deployments"** tab and watch the build logs.
- You should see: `Bot is running …`
- Open Telegram and send `/check` to your bot.

---

## Usage

| Command | What it does |
|---|---|
| `/start` | Shows welcome message |
| `/check` | Runs the full check and replies with the list of non-followers |

---

## How It Works

1. Uses Tweepy's `Paginator` to fetch all accounts you follow (handles 1000+ follows automatically).
2. Does the same for your followers list.
3. Computes the set difference: `following - followers`.
4. Resolves those IDs to @usernames in batches of 100.
5. Formats and sends the result to you via Telegram.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `Forbidden 403` | Your Twitter app doesn't have the right permissions. Make sure it has **Read** access in the developer portal under *App Settings → User authentication settings*. |
| `Unauthorized 401` | Your Bearer Token is wrong or expired. Regenerate it in the developer portal. |
| `Telegram bot not responding` | Check that `TELEGRAM_BOT_TOKEN` is correct and only one instance of the bot is running. |
| Long wait on `/check` | Normal — the free Twitter tier rate-limits to 15 requests per 15 minutes. Tweepy handles this automatically with `wait_on_rate_limit=True`. |
