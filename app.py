import requests
import geocoder
import schedule
import time
import pytz
from datetime import datetime
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



# Twilio credentials (loaded securely)
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
your_number = os.getenv("YOUR_PHONE_NUMBER")

client = Client(account_sid, auth_token)

# Get the user's current location
def get_current_location():
    g = geocoder.ip('me')
    if g.ok:
        return g.latlng
    else:
        raise Exception("Could not determine current location")
    
# Fetch prayer times from Aladhan API
def fetch_prayer_times(lat, lon, method=2):
    url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method={method}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data["data"]["timings"], data["data"]["meta"]["timezone"]
    else:
        raise Exception(f"API call failed with status code {response.status_code}")

# Check and notify logic
def check_and_notify():
    latitude, longitude = get_current_location()
    times, timezone = fetch_prayer_times(latitude, longitude)

    print("Prayer times for today:")
    for prayer, time in times.items():
        print(f"{prayer}: {time}")

    # Get current time in the user's timezone
    user_tz = pytz.timezone(timezone)
    now = datetime.now(user_tz)

    # Prepare prayer times as datetime objects
    next_prayer = None
    min_diff = None

    for prayer, time_str in times.items():
        # Ignore non-prayer times
        if prayer.lower() in ["imsak", "midnight", "sunset", "firstthird", "lastthird"]:
            continue

        # Combine date and time
        prayer_time = datetime.strptime(time_str, "%H:%M")
        prayer_time = user_tz.localize(prayer_time.combine(now.date(), prayer_time.time()))

        # Compare with current time
        if prayer_time > now:
            time_diff = (prayer_time - now).total_seconds()
            if min_diff is None or time_diff < min_diff:
                min_diff = time_diff
                next_prayer = (prayer, time_str)

    # Time difference in minutes
    if next_prayer:
        minutes_remaining = int(min_diff / 60) 

        if minutes_remaining <= 5:
            sms_body = f"Reminder: {next_prayer[0]} prayer is at {next_prayer[1]}. Wudhu and prepare for prayer."
            message = client.messages.create(
                body=sms_body,
                from_=twilio_number,
                to=your_number
            )
            print(f"📩 SMS sent: {sms_body}")
        else:
            print(f"⏳ {minutes_remaining} minutes left until {next_prayer[0]}. SMS will be sent 5 minutes before.")
        
        print(f"\n🕓 Next prayer is {next_prayer[0]} at {next_prayer[1]}")
    else:
        print("\n✅ All prayers for today are complete.")

   
#Schdule the function to run every 1 minute
schedule.every(1).minutes.do(check_and_notify)

print("📡 Prayer time notifier is running. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)


