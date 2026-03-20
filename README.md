# Discord Daily Self-Bot

A lightweight Python script that sends a message to a Discord channel at a random time within a configured daily window. Designed to run on a Raspberry Pi via cron.

---

## How it works

1. Cron triggers the script once a day, just before your time window opens
2. The script picks a random time within your configured window
3. It sleeps until that time, then sends your message via Discord's API
4. Everything is logged to a file for easy debugging

---

## Requirements

- Python 3.7+
- `python-dotenv` package

```bash
pip3 install python-dotenv
```

---

## Setup

### 1. Clone / copy the files

```bash
mkdir ~/discord-bot && cd ~/discord-bot
# Place daily_quesy.py and .env here
cp .env.example .env
```

### 2. Get your Discord user token

1. Open Discord in a **browser** (not the app)
2. Press `F12` to open DevTools → go to the **Network** tab
3. Send any message in any channel
4. Find the `messages` POST request in the network log
5. Under **Request Headers**, copy the `Authorization` value
6. Paste it into `.env` as `DISCORD_TOKEN`

> ⚠️ Your user token is sensitive — treat it like a password. Never share it or commit it to git.

### 3. Get your Channel ID

1. In Discord, go to **Settings → Advanced** and enable **Developer Mode**
2. Right-click the target channel → **Copy Channel ID**
3. Paste it into `.env` as `DISCORD_CHANNEL_ID`

### 4. Configure `.env`

```env
DISCORD_TOKEN=your_user_token_here
DISCORD_CHANNEL_ID=123456789012345678
DISCORD_MESSAGE=Good morning everyone! 👋
TIME_START=09:00
TIME_END=12:00
```

Protect the file so only your user can read it:

```bash
chmod 600 .env
```

---

## Testing

Set a narrow window around the current time to trigger a send immediately:

```bash
TIME_START=09:00 TIME_END=09:01 python3 daily_quesy.py
```

If the randomly chosen time has already passed, the script will send immediately rather than skipping.

---

## Cron setup

Schedule the script to run once a day, a few minutes before your window opens:

```bash
crontab -e
```

```cron
# Runs at 08:55 every day (window opens at 09:00)
55 8 * * * cd /home/pi/discord-bot && python3 daily_quesy.py >> /home/pi/discord-bot/bot.log 2>&1
```

Check the log at any time:

```bash
tail -f ~/discord-bot/bot.log
```

---

## Configuration reference

| Variable            | Required | Description                                      | Example                  |
|---------------------|----------|--------------------------------------------------|--------------------------|
| `DISCORD_TOKEN`     | ✅       | Your personal Discord user token                 | `mfa.xxxxxxxxxxxx`       |
| `DISCORD_CHANNEL_ID`| ✅       | ID of the channel to send the message in         | `123456789012345678`      |
| `DISCORD_MESSAGE`   | ✅       | The message to send                              | `Good morning! 👋`       |
| `TIME_START`        | ✅       | Start of the daily send window (24h format)      | `09:00`                  |
| `TIME_END`          | ✅       | End of the daily send window (24h format)        | `12:00`                  |

---

## Security notes

- **Never commit `.env` to git.** Add it to `.gitignore`:
  ```bash
  echo ".env" >> .gitignore
  ```
- Your Discord token grants full access to your account. Keep it private.
- Discord's ToS prohibits automated user accounts (self-bots). Low-frequency, human-like usage is very unlikely to cause issues, but be aware of the risk.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Missing env vars` error | `.env` not filled in or not found | Check the file exists in the same directory as the script |
| `HTTP 401` error | Invalid token | Re-copy your token from the browser DevTools |
| `HTTP 403` error | Bot lacks permission in that channel | Check your Discord role permissions for that channel |
| Message never sends | Cron not firing, or window already passed | Check `bot.log` and verify cron with `crontab -l` |
| Script exits immediately | Time window already passed for today | Normal — cron should fire before the window opens |
