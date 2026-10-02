import os
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from urllib.request import Request, urlopen

NOTION_URL = os.environ["NOTION_URL"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

STATE_FILE = Path("assignments.json")


def load_state():
    if not STATE_FILE.exists():
        return {}
    
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def send_discord(task):
    payload = {
        "embeds": [
            {
                "title": "📚 NEW ASSIGNMENT",
                "description": f"**{task['text']}**",
                "url": NOTION_URL,
                "footer": {
                    "text": "Automatically detected from Notion"
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


def get_tasks():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 1200
            }
        )

        print("Opening Notion...")

        page.goto(
            NOTION_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(10000)

        print("Page title:", page.title())

        # Scroll through the page so lazy-loaded content appears.
        for _ in range(12):
            page.mouse.wheel(0, 1200)
            page.wait_for_timeout(700)

        # Get all visible text from the rendered page.
        body_text = page.locator("body").inner_text()

        print("Page text length:", len(body_text))
        print("----- NOTION TEXT START -----")
        print(body_text[:10000])
        print("----- NOTION TEXT END -----")

        tasks = []

        # Look for lines that resemble the assignment checklist.
        lines = [
            line.strip()
            for line in body_text.splitlines()
            if line.strip()
        ]

        for line in lines:
            # Ignore headings and obvious navigation text.
            if len(line) < 5:
                continue

            lower = line.lower()

            ignored = [
                "list tugas oktober",
                "tugas dan deadline",
                "student information",
                "share",
                "search",
                "comments"
            ]

            if any(x in lower for x in ignored):
                continue

            # Look for the actual assignment names from the page.
            assignment_keywords = [
                "ebp",
                "ux lab",
                "cb:",
            ]

            if any(keyword in lower for keyword in assignment_keywords):
                tasks.append({
                    "text": line,
                    "checked": False
                })

        # Remove duplicates.
        unique = {}

        for task in tasks:
            key = task["text"].lower()
            unique[key] = task

        print("Assignments detected:", len(unique))

        return list(unique.values())


def main():
    print("=== BINUS NOTION ASSIGNMENT CHECKER ===")

    old_state = load_state()
    current_tasks = get_tasks()

    print("Tasks detected:", len(current_tasks))

    if not current_tasks:
        print("No checkbox tasks detected.")
        return

    current_state = {}

    for task in current_tasks:
        key = task["text"].lower()

        current_state[key] = {
            "text": task["text"],
            "checked": task["checked"]
        }

    # First run:
    # Save existing assignments as baseline.
    # Do NOT spam Discord with all existing tasks.
    if not old_state:
        print("First run detected.")
        print("Saving existing tasks as baseline.")

        save_state(current_state)
        return

    # Find genuinely new tasks.
    new_tasks = []

    for key, task in current_state.items():
        if key not in old_state:
            new_tasks.append(task)

    print("New tasks:", len(new_tasks))

    for task in new_tasks:
        # Only announce unchecked/new assignments.
        if not task["checked"]:
            print("NEW ASSIGNMENT:", task["text"])
            send_discord(task)

    save_state(current_state)

    print("Finished.")


if __name__ == "__main__":
    main()
