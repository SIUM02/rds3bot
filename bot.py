import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import schedule
import time
import os



# ─── CONFIG ───────────────────────────────────────────────
BOT_TOKEN = "8905300404:AAGDwjeOM8n5nFqZb8rC8Y2n2ri8xc4qTBE"   # From @BotFather
CHAT_ID   = "6731734203"              # Your Telegram chat ID
URL = "https://raw.githubusercontent.com/SIUM02/NSU4/main/Offered%20Courses%20_%20North%20South%20University.html"


WATCH_LIST = [
    ("CSE273", "1"),
    ("CSE273", "2"),
    ("CSE299", "3"),
    ("CSE299", "13"),
    ("CSE299", "6"),
    ("CSE299", "7"),
    ("CSE331/EEE332/EEE453/ETE332", "1"),
    ("CSE445", "7"),
    ("CSE445", "6"),
    ("MAT350", "10"),
    ("MAT350", "11"),
    ("MAT350", "14"),
]
# ──────────────────────────────────────────────────────────

last_seats = {}

def fetch_seats():
    response = requests.get(URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    seats_data = {}

    table = soup.find("table", {"id": "offeredCourseTbl"})
    if table is None:
        print("Table not found!")
        return seats_data

    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 7:
            course = cols[1].text.strip()
            section = cols[2].text.strip()
            fac = cols[3].text.strip()
            times = cols[4].text.strip()
            seats = cols[6].text.strip()
            try:
                seats_data[(course, section)] = {
                    "seats": int(seats),
                    "faculty": fac,
                    "time": times
                }
            except ValueError:
                pass
    return seats_data

async def send_alert(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

def check_seats():
    global last_seats
    print("🔍 Checking seats...")

    try:
        current = fetch_seats()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    for (course, section) in WATCH_LIST:
        key = (course, section)
        data = current.get(key)

        if data is None:
            continue

        current_seats = data["seats"]
        fac = data["faculty"]
        times = data["time"]
        prev_seats = last_seats.get(key, None)

        if prev_seats is not None and current_seats > 0:
            msg = (
                f"🎉 SEAT AVAILABLE!\n"
                f"📚 Course: {course}\n"
                f"🔢 Section: {section}\n"
                f"💺 Seats: {current_seats}\n"
                f"👨‍🏫 Faculty: {fac}\n"
                f"🕐 Time: {times}\n"
                f"🔗 {URL}"
            )
            asyncio.run(send_alert(msg))
            print(f"Alert sent for {course} Section {section}!")

        elif prev_seats is not None and current_seats > prev_seats:
            msg = (
                f"📈 Seats Increased!\n"
                f"📚 Course: {course}\n"
                f"🔢 Section: {section}\n"
                f"💺 Seats: {prev_seats} → {current_seats}\n"
                f"👨‍🏫 Faculty: {fac}\n"
                f"🕐 Time: {times}\n"
                f"🔗 {URL}"
            )
            asyncio.run(send_alert(msg))
            print(f"Increase alert sent for {course} Section {section}!")

        last_seats[key] = current_seats
        print(f"{course} Sec {section}: {current_seats} seats | Faculty: {fac} | Time: {times}")

check_seats()
schedule.every(1).minutes.do(check_seats)

print("✅ Bot is running! Checking every 1 minute...")
while True:
    schedule.run_pending()
    time.sleep(1)