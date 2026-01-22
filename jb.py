import os
import time
import json
import requests
from datetime import datetime, timezone

TEAM_ID = os.environ.get("TEAM_ID", "chess-blasters-2")
TOKEN_NAMES = ["LICHESS_KEY", "LICHESS_KEYS", "T", "L"]
TOKENS = []
for name in TOKEN_NAMES:
    val = os.environ.get(name)
    if val:
        if "," in val:
            TOKENS.extend([t.strip().strip('"').strip("'") for t in val.split(",")])
        else:
            TOKENS.append(val.strip('"').strip("'"))

if not TOKENS:
    raise SystemExit("No tokens found.")

API_ROOT = "https://lichess.org/api"

def now_ms():
    return int(time.time() * 1000)

def get_username(token):
    try:
        r = requests.get(f"{API_ROOT}/account", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if r.status_code == 200:
            return r.json().get("username")
    except Exception:
        pass
    return None

def get_upcoming_swisses(token, team_id):
    headers = {"Accept": "application/x-ndjson", "Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{API_ROOT}/team/{team_id}/swiss", headers=headers, timeout=15)
        if res.status_code != 200:
            return []
        
        swisses = []
        now = now_ms()
        for line in res.iter_lines(decode_unicode=True):
            if not line: continue
            obj = json.loads(line)
            starts = obj.get("startsAt")
            if not starts: continue
            
            start_ms = int(datetime.strptime(starts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() * 1000)
            
            if start_ms > now:
                obj["_startsMs"] = start_ms
                swisses.append(obj)
        return sorted(swisses, key=lambda s: s["_startsMs"])
    except Exception:
        return []

def withdraw(token, swiss_id, username):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        requests.post(f"{API_ROOT}/swiss/{swiss_id}/withdraw", headers=headers, timeout=15)
    except Exception:
        pass

usernames = {}
for t in TOKENS:
    u = get_username(t)
    if u:
        usernames[t] = u

if not usernames:
    raise SystemExit("No valid accounts.")

while True:
    for token, uname in usernames.items():
        swisses = get_upcoming_swisses(token, TEAM_ID)
        now = now_ms()
        
        for s in swisses:
            sid = s["id"]
            start = s["_startsMs"]
            mins_left = (start - now) / 60000

            if 1.5 <= mins_left <= 3.5:
                withdraw(token, sid, uname)
                time.sleep(1)

        time.sleep(5)
    time.sleep(30)
