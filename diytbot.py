#!/usr/bin/env python3
"""Meldet neue YouTube-Videos einer Playlist in Discord.
Konfiguration über Umgebungsvariablen (siehe .env.example)."""
import json
import os
import time
import traceback
from datetime import datetime

import requests


def env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"{name} ist nicht gesetzt (siehe .env.example).")
    return value


# Google-API-Key von https://console.cloud.google.com/
YOUTUBE_API_KEY = env("YOUTUBE_API_KEY")
# Uploads-Playlist = Kanal-ID mit "UU…" statt "UC…" am Anfang
YOUTUBE_PLAYLIST_ID = env("YOUTUBE_PLAYLIST_ID")
DISCORD_WEBHOOK_ID = env("DISCORD_WEBHOOK_ID")
DISCORD_WEBHOOK_TOKEN = env("DISCORD_WEBHOOK_TOKEN")

DATA_DIR = os.environ.get("DATA_DIR", ".")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
API_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="
DISCORD_MESSAGE = "Hey what's up guys, new video uploaded. Go check it out ! \n"
TIME_INTERVAL = 60  # Sekunden zwischen zwei Abfragen
TIMEOUT = 15  # Sekunden – verhindert endloses Hängen
KEEP_SEEN = 50  # so viele bereits gemeldete Video-IDs merken


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def redact(text):
    """Geheimnisse aus Fehlermeldungen entfernen (requests nennt sonst die URL inkl. Key)."""
    text = str(text)
    for secret in (YOUTUBE_API_KEY, DISCORD_WEBHOOK_TOKEN):
        text = text.replace(secret, "***")
    return text


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)


def get_latest_video_id():
    r = requests.get(
        API_URL,
        params={
            "part": "snippet",
            "playlistId": YOUTUBE_PLAYLIST_ID,
            "maxResults": 1,
            "key": YOUTUBE_API_KEY,
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None
    return items[0]["snippet"]["resourceId"]["videoId"]


def send_discord(text):
    r = requests.post(
        f"https://discord.com/api/v10/webhooks/{DISCORD_WEBHOOK_ID}/{DISCORD_WEBHOOK_TOKEN}",
        json={"content": text},
        timeout=TIMEOUT,
    )
    r.raise_for_status()


def check(state):
    video_id = get_latest_video_id()
    if not video_id:
        return
    seen = state.setdefault("seen", [])
    if video_id in seen:
        return

    if not seen:
        # Allererster Start: aktuelles Video nur merken, nicht erneut posten.
        log(f"Initialisiert, aktuelles Video: {video_id}")
    else:
        log(f"Neues Video: {video_id}")
        send_discord(DISCORD_MESSAGE + YOUTUBE_VIDEO_URL + video_id)
        log("In Discord gemeldet.")

    seen.append(video_id)
    del seen[:-KEEP_SEEN]
    save_state(state)


def main():
    log(f"ytBot gestartet, Intervall {TIME_INTERVAL} s")
    state = load_state()
    while True:
        try:
            check(state)
        except Exception:
            log("Fehler – nächster Versuch im normalen Intervall:")
            print(redact(traceback.format_exc()), flush=True)
        time.sleep(TIME_INTERVAL)


if __name__ == "__main__":
    main()
