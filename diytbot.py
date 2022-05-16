#!/usr/bin/env python3
# python diytbot.py API_KEY YOUTUBE_PLAYLIST_ID DISCORD_WEBHOOK_ID DISCORD_WEBHOOK_TOKEN

import time
import sys
import requests
from discord import Webhook, RequestsWebhookAdapter

#Discord configuration
WEBHOOK_ID = sys.argv[3]
WEBHOOK_TOKEN = sys.argv[4]

# google api key from https://console.cloud.google.com/
API_KEY = sys.argv[1]
YOUTUBE_PLAYLIST_ID = sys.argv[2] # playlist id of youtube uploads is channel id with UU.. instead of UC in the beginning

API_URL = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={YOUTUBE_PLAYLIST_ID}&maxResults=1&key={API_KEY}'
YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='

TIME_INTERVAL = 60 # script executed every x seconds
RECENT_STATE = 1 # initial state
currentVideoId = ''

DISCORD_MESSAGE = "Hey what's up guys, new video uploaded. Go check it out ! \n"

def getVideoData():
    jData = None
    try:
        r = requests.get(API_URL, timeout=15)
        r.raise_for_status()
        jData = r.json()
    except requests.exceptions.ConnectionError as cone:
        print("Connection Error:", cone)
    except requests.exceptions.Timeout as et:
        print("Timeout Error:", et)
    except requests.exceptions.RequestException as re:
        print("Error message:", re)
    return jData

def getNewVideoId(jData):
    return jData['items'][0]['snippet']['resourceId']['videoId']

def main():
    global currentVideoId
    while True:
        time.sleep(TIME_INTERVAL)
        jData = getVideoData()
        if getNewVideoId(jData) != currentVideoId:
            currentVideoId = getNewVideoId(jData)
            webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
            webhook.send(DISCORD_MESSAGE+YOUTUBE_VIDEO_URL+currentVideoId)

if __name__ == "__main__":
    main()

