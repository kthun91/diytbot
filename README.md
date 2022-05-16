# diytbot
Notifies Discord channel every time there is a new video uploaded on a youtube channel.
To start Bot on your server in background:
```nohup python diytbot.py API_KEY YOUTUBE_PLAYLIST_ID DISCORD_WEBHOOK_ID DISCORD_WEBHOOK_TOKEN </dev/null &>/dev/null &```

## Requirements
1. You have to install Discord.py. I recommend using pip. For example: ```python3 -m pip install discord.py```
2. You will need a API-key from google. Go get one at https://console.cloud.google.com/
3. You also need the Youtube upload playlist Id from the channel which is just the channel-id, but with a 'U' at second character position: UCXXXXX.. to UUXXXXX..
4. Discord Webhook and Tokens available at discord channel -> settings -> integration -> generate webhook

## Important note about quota
You have a quota with youtube API.
The daily quota (is for today) is 10.000 units.
The API-call we use is worth 1 unit. You should have 8560 units left per day.
