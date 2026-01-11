#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime as dt
import pathlib
import requests
from zoneinfo import ZoneInfo

TOKEN = os.environ["LICHESS_KEY"].strip('"')
TEAM = "chess-blasters-2"
ROUNDS = 7
IST = ZoneInfo("Asia/Kolkata")
DELAY_DAYS = 3

headers = {"Authorization": f"Bearer {TOKEN}"}
URL = f"https://lichess.org/api/swiss/new/{TEAM}"

DESC_FILE = pathlib.Path(__file__).with_name("description.txt")
try:
    LONG_DESC = DESC_FILE.read_text(encoding="utf-8").strip()
except FileNotFoundError:
    raise SystemExit("❌ description.txt not found!")

SCHEDULE = [
    ("00:00", "Cash Tournament Qualifier", 10, 0),
    ("00:30", "Cash Tournament Qualifier", 7, 2),
    ("01:00", "Cash Tournament Qualifier", 3, 2),
    ("01:30", "Cash Tournament Qualifier", 3, 0),
    ("02:00", "Cash Tournament Qualifier", 5, 0),
    ("02:30", "Cash Tournament Qualifier", 10, 5),
    ("03:00", "Cash Tournament Qualifier", 10, 0),
    ("03:30", "Cash Tournament Qualifier", 7, 2),
    ("04:00", "Cash Tournament Qualifier", 3, 2),
    ("04:30", "Cash Tournament Qualifier", 3, 0),
    ("05:00", "Cash Tournament Qualifier", 5, 0),
    ("05:30", "Cash Tournament Qualifier", 3, 1),
    ("06:00", "Cash Tournament Qualifier", 10, 0),
    ("06:30", "Cash Tournament Qualifier", 7, 2),
    ("07:00", "Cash Tournament Qualifier", 3, 2),
    ("07:30", "Cash Tournament Qualifier", 3, 0),
    ("08:00", "Cash Tournament Qualifier", 5, 0),
    ("08:30", "Cash Tournament Qualifier", 10, 5),
    ("09:00", "Cash Tournament Qualifier", 10, 0),
    ("09:30", "Cash Tournament Qualifier", 7, 2),
    ("10:00", "Cash Tournament Qualifier", 3, 2),
    ("10:30", "Cash Tournament Qualifier", 3, 0),
    ("11:00", "Cash Tournament Qualifier", 5, 0),
    ("11:30", "Cash Tournament Qualifier", 3, 0),
    ("12:00", "Cash Tournament Qualifier", 3, 1),
    ("12:30", "Cash Tournament Qualifier", 10, 0),
    ("13:00", "Cash Tournament Qualifier", 7, 2),
    ("13:30", "Cash Tournament Qualifier", 3, 2),
    ("14:00", "Cash Tournament Qualifier", 3, 0),
    ("14:30", "Cash Tournament Qualifier", 5, 0),
    ("15:00", "Cash Tournament Qualifier", 10, 5),
    ("15:30", "Cash Tournament Qualifier", 10, 0),
    ("16:00", "Cash Tournament Qualifier", 7, 2),
    ("16:30", "Cash Tournament Qualifier", 3, 2),
    ("17:00", "Cash Tournament Qualifier", 3, 0),
    ("17:30", "Cash Tournament Qualifier", 5, 0),
    ("18:00", "Cash Tournament Qualifier", 3, 1),
    ("18:30", "Cash Tournament Qualifier", 10, 0),
    ("19:00", "Cash Tournament Qualifier", 7, 2),
    ("19:30", "Cash Tournament Qualifier", 3, 2),
    ("20:00", "Cash Tournament Qualifier", 3, 0),
    ("20:30", "Cash Tournament Qualifier", 5, 0),
    ("21:00", "Cash Tournament Qualifier", 10, 5),
    ("21:30", "Cash Tournament Qualifier", 10, 0),
    ("22:00", "Cash Tournament Qualifier", 7, 2),
    ("22:30", "Cash Tournament Qualifier", 3, 2),
    ("23:00", "Cash Tournament Qualifier", 3, 1),
    ("23:30", "Cash Tournament Qualifier", 5, 0),
]

def scheduled_time_utc(time_str: str) -> dt.datetime:
    hh, mm = map(int, time_str.split(":"))
    now_ist = dt.datetime.now(IST)
    target_date = (now_ist + dt.timedelta(days=DELAY_DAYS)).date()
    start_ist = dt.datetime.combine(
        target_date,
        dt.time(hh, mm),
        tzinfo=IST
    )
    return start_ist.astimezone(dt.timezone.utc)

def create_tmt(name: str, minutes: int, inc: int, start_utc: dt.datetime) -> None:
    payload = {
        "name": name[:30],
        "clock.limit": minutes * 60,
        "clock.increment": inc,
        "startsAt": start_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nbRounds": ROUNDS,
        "variant": "standard",
        "rated": "true",
        "description": LONG_DESC,
        "conditions.playYourGames": "true",
    }

    r = requests.post(URL, headers=headers, data=payload, timeout=15)

    if r.status_code == 200:
        print(f"✅ {name:<25} → {r.json().get('url')}")
    else:
        print(f"❌ {name:<25} ({r.status_code}) {r.text[:120]}")

if __name__ == "__main__":
    for time_str, title, mins, inc in SCHEDULE:
        start = scheduled_time_utc(time_str)
        create_tmt(title, mins, inc, start)
