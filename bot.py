from bs4 import BeautifulSoup
import telegram
import asyncio
import schedule
import time
import os

# ─── CONFIG ───────────────────────────────────────────────
BOT_TOKEN = "8905300404:AAGDwjeOM8n5nFqZb8rC8Y2n2ri8xc4qTBE"
HTML_FILE = "/Users/wadudsium/Documents/rds3bot/Offered Courses _ North South University.html"

# ─── USERS ─────────────────────────────────────────────────
USERS = [
    {
        "chat_id": "6731734203",
        "watch_list": [
            ("CSE273", "2"),
            ("CSE299", "3"),
            ("CSE299", "13"),
            ("CSE445", "7"),
            ("CSE445", "1"),
            ("MAT350", "10"),
        ]
    },
    {
        "chat_id": "6484071956",
        "watch_list": [
            ("CSE327", "3"),
            ("CSE327", "2"),
           
        ]
    },
    {
        "chat_id": "6668774846",
        "watch_list": [
              ("CSE273", "2"),
            ("CSE299", "3"),
            ("CSE299", "13"),
            ("CSE445", "7"),
            ("CSE445", "1"),
            ("MAT350", "10"),
        ]
    },
]
# ──────────────────────────────────────────────────────────

def fetch_seats():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    seats_data = {}
    table = soup.find("table", {"id": "offeredCourseTbl"})

    if table is None:
        print("❌ Table not found!")
        return seats_data

    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = [td.text.strip() for td in row.find_all("td")]
        if len(cols) >= 7:
            course = cols[1]
            section = cols[2]
            fac = cols[3]
            times = cols[4]
            seats = cols[6]
            try:
                seats_data[(course, section)] = {
                    "seats": int(seats),
                    "faculty": fac,
                    "time": times
                }
            except ValueError:
                pass
    return seats_data

async def send_alert(chat_id, message):
    bot = telegram.Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=chat_id, text=message)

def check_seats():
    print(f"🔍 Checking seats at {time.strftime('%H:%M:%S')}...")

    if not os.path.exists(HTML_FILE):
        print("⏳ HTML file not found! Waiting for next minute...")
        return

    try:
        current = fetch_seats()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    for user in USERS:
        chat_id = user["chat_id"]
        watch_list = user["watch_list"]

        for (course, section) in watch_list:
            key = (course, section)
            data = current.get(key)

            if data is None:
                continue

            current_seats = data["seats"]
            fac = data["faculty"]
            times = data["time"]

            print(f"{course} Sec {section}: {current_seats} seats | Faculty: {fac} | Time: {times}")

            if current_seats > 0:
                msg = (
                    f"🎉 SEAT AVAILABLE!\n"
                    f"📚 Course: {course}\n"
                    f"🔢 Section: {section}\n"
                    f"💺 Seats: {current_seats}\n"
                    f"👨‍🏫 Faculty: {fac}\n"
                    f"🕐 Time: {times}\n"
                )
                asyncio.run(send_alert(chat_id, msg))
                print(f"✅ Alert sent to {chat_id} for {course} Sec {section}!")

    os.remove(HTML_FILE)
    print(f"🗑️ File deleted at {time.strftime('%H:%M:%S')}")

check_seats()
schedule.every(2).minutes.do(check_seats)

print("✅ Bot is running! Checking every 2 minute...")
while True:
    schedule.run_pending()
    time.sleep(1)
