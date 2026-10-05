import os
import json
from urllib.request import Request, urlopen

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

payload = {
    "embeds": [
        {
            "title": "📚 NEW ASSIGNMENT LH11",
            "description": "**TEST — EBP SESSION - Expenditure Cycle**",
            "fields": [
                {
                    "name": "📅 Status",
                    "value": "Testing Kenn → Discord"
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
