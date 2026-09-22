import os 
import time
import requests


TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL = os.environ["DISCORD_CHANNEL_ID"]
API = f"https://discord.com/api/v10/channels/{CHANNEL}/messages"
HEADERS = {"Authorization": f"Bot {TOKEN}"}



def send_captcha(png_path):
    with open(png_path,"rb") as fh:
        resp = requests.post(
            API,
            headers=HEADERS,
            data={"content": "Captcha — reply with the 6 characters (case matters)"},
            files={"file": ("captcha.png", fh, "image/png")},
            timeout=30,
        )

    if resp.status_code >= 400:
        raise RecursionError(f"discord send failed {resp.status_code}: {resp.text}")

    return resp.json()["id"]






def wait_for_reply(after_id, timeout_s=180,poll_s=4):

    deadline = time.monotonic() + timeout_s

    while time.monotonic() < deadline:
        resp = requests.get(
            API, headers=HEADERS,
            params={"after": after_id, "limit": 20},
            timeout=30,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"discord read failed {resp.status_code}:{resp.text}")

        human = [m for m in resp.json() if not m.get("author", {}).get("bot")]

        if human:
            newest = max(human, key=lambda m: int(m["id"]))
            return newest['content'].strip()

        time.sleep(poll_s)


    raise TimeoutError(f"no captcha reply within {timeout_s}s")



