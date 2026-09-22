import os
import sys 
import requests


TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL = os.environ["DISCORD_CHANNEL_ID"]
PNG  = "failures/captcha.png"


url = f"https://discord.com/api/v10/channels/{CHANNEL}/messages"


with open(PNG, 'rb') as fh:
    resp = requests.post(
        url,
        headers={"Authorization": f"Bot {TOKEN}"},
        data={"content": "captcha test"},
        files={"file": ("captcha.png", fh,"image/png")},
        timeout=30
    )


if resp.status_code >= 400:
    print(f"FAILED {resp.status_code}")
    print(resp.text)
    sys.exit(1)

print("sent OK")
print("message id:", resp.json()["id"])

