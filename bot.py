import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import schedule
import time

# ─── CONFIG ───────────────────────────────────────────────
BOT_TOKEN = "8905300404:AAGDwjeOM8n5nFqZb8rC8Y2n2ri8xc4qTBE"   # From @BotFather
CHAT_ID   = "6731734203"              # Your Telegram chat ID
URL       = "https://nihalxx3.github.io/rds2.northsouth.edu-Fall2025/"

# Add the courses you want to watch: ("COURSE_CODE", "SECTION")
WATCH_LIST = [
    ("CSE115", "1"),
    ("CSE115", "2"),
    ("BUS112", "8"),
    # Add more as needed...
]
# ──────────────────────────────────────────────────────────

# Store last known seat counts to detect changes
last_seats = {}

def fetch_seats():
    """Scrape the NSU course table and return a dict of {(course, section): seats}"""
    response = requests.get(URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    seats_data = {}
    table = soup.find("table")
    rows = table.find_all("tr")[1:]  # Skip header row
    
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 7:
            course  = cols[1].text.strip()
            section = cols[2].text.strip()
            seats   = cols[6].text.strip()
            try:
                seats_data[(course, section)] = int(seats)
            except ValueError:
                pass
    
    return seats_data

async def send_alert(message):
    """Send a Telegram message"""
    bot = telegram.Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

def check_seats():
    """Main check — compares current seats to last known state"""
    global last_seats
    print("🔍 Checking seats...")
    
    try:
        current = fetch_seats()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
    
    for (course, section) in WATCH_LIST:
        key = (course, section)
        current_seats = current.get(key)
        
        if current_seats is None:
            continue  # Course not found on page
        
        prev_seats = last_seats.get(key, None)
        
        # Alert if seats opened up (was 0 or less, now more than 0)
        if prev_seats is not None and prev_seats == current_seats :
            msg = (
                f"🎉 SEAT AVAILABLE!\n"
                f"📚 Course: {course}\n"
                f"🔢 Section: {section}\n"
                f"💺 Seats: {current_seats}\n"
                f"🔗 {URL}"
            )
            asyncio.run(send_alert(msg))
            print(f"Alert sent for {course} Section {section}!")
        
        # Also alert if seats increased from a previous low count
        elif prev_seats is not None and current_seats > prev_seats:
            msg = (
                f"📈 Seats Increased!\n"
                f"📚 Course: {course}\n"
                f"🔢 Section: {section}\n"
                f"💺 Seats: {prev_seats} → {current_seats}\n"
                f"🔗 {URL}"
            )
            asyncio.run(send_alert(msg))
        
        last_seats[key] = current_seats
        print(f"{course} Sec {section}: {current_seats} seats")

# Run immediately, then every 6 minutes (matches site refresh rate)
check_seats()
schedule.every(1).minutes.do(check_seats)

print("✅ Bot is running! Checking every 1 minutes...")
while True:
    schedule.run_pending()
    time.sleep(1)