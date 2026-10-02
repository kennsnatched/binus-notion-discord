import os
import json
from urllib.request import Request, urlopen

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

payload = {
    "embeds": [
        {
            "title": "📚 NEW ASSIGNMENT",
            "description": "**TEST — Tugas Baru Discord**",
            "fields": [
                {
                    "name": "📅 Status",
                    "value": "Testing GitHub → Discord"
                }
            ],
            "footer": {
                "text": "BINUS Assignment Bot • TEST"
            }
        }
    ]
}

data = json.dumps(payload).encode("utf-8")

request = Request(
    DISCORD_WEBHOOK_URL,
    data=data,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "BINUS-Assignment-Bot"
    },
    method="POST"
)

with urlopen(request, timeout=20) as response:
    print("Discord response:", response.status)

print("TEST MESSAGE SENT SUCCESSFULLY")
