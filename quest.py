#!/usr/bin/env python3
"""
Discord Daily Self-Bot
Sends a message to a specific channel at a random time within a configured window.
Designed to be run once per day via cron.
"""

import os
import sys
import time
import random
import datetime
import urllib.request
import urllib.error
import json
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
TOKEN      = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
MESSAGE    = os.getenv("DISCORD_MESSAGE")
TIME_START = os.getenv("TIME_START", "09:00")   # e.g. "09:00"
TIME_END   = os.getenv("TIME_END",   "17:00")   # e.g. "17:00"
# ─────────────────────────────────────────────────────────────────────────────

def validate_config():
    missing = [k for k, v in {
        "DISCORD_TOKEN": TOKEN,
        "DISCORD_CHANNEL_ID": CHANNEL_ID,
        "DISCORD_MESSAGE": MESSAGE,
    }.items() if not v]
    if missing:
        print(f"[ERROR] Missing env vars: {', '.join(missing)}")
        sys.exit(1)

def parse_time(t_str):
    h, m = map(int, t_str.strip().split(":"))
    return datetime.time(h, m)

def seconds_until(target_time):
    now = datetime.datetime.now()
    target = datetime.datetime.combine(now.date(), target_time)
    if target < now:
        # Already past — target is tomorrow
        target += datetime.timedelta(days=1)
    return (target - now).total_seconds()

def random_delay_seconds(start_str, end_str):
    start = parse_time(start_str)
    end   = parse_time(end_str)
    now   = datetime.datetime.now()

    start_dt = datetime.datetime.combine(now.date(), start)
    end_dt   = datetime.datetime.combine(now.date(), end)

    if end_dt <= start_dt:
        print("[ERROR] TIME_END must be after TIME_START")
        sys.exit(1)

    # Pick a random moment within the window
    window_seconds = int((end_dt - start_dt).total_seconds())
    offset = random.randint(0, window_seconds)
    send_at = start_dt + datetime.timedelta(seconds=offset)

    print(f"[INFO] Scheduled to send at: {send_at.strftime('%H:%M:%S')}")

    delay = (send_at - now).total_seconds()
    return delay

def send_message(channel_id, token, message):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    payload = json.dumps({"content": message}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": token,          # Personal token — no "Bot " prefix
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",     # Mimic browser behaviour
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                print("[OK] Message sent successfully.")
            else:
                print(f"[WARN] Unexpected status: {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[ERROR] HTTP {e.code}: {body}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[ERROR] Network error: {e.reason}")
        sys.exit(1)

def main():
    validate_config()

    delay = random_delay_seconds(TIME_START, TIME_END)

    if delay < 0:
        print("[WARN] Chosen time already passed — sending immediately.")
        delay = 0

    print(f"[INFO] Waiting {int(delay)} seconds ({delay/60:.1f} min)…")
    time.sleep(delay)

    send_message(CHANNEL_ID, TOKEN, MESSAGE)

if __name__ == "__main__":
    main()
