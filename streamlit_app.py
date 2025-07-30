import streamlit as st
import requests
import geocoder
import pytz
from datetime import datetime
from dotenv import load_dotenv
import os
from twilio.rest import Client

# Load environment variables
load_dotenv()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
your_number = os.getenv("YOUR_PHONE_NUMBER")

client = Client(account_sid, auth_token)

# --- Core Functions ---
def get_current_location():
    g = geocoder.ip('me')
    if g.ok:
        return g.latlng
    else:
        raise Exception("Could not determine current location")

def fetch_prayer_times(lat, lon, method=2):
    url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method={method}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["data"]["timings"], data["data"]["meta"]["timezone"]
    else:
        raise Exception(f"API error: {response.status_code}")

def get_next_prayer(times, timezone):
    user_tz = pytz.timezone(timezone)
    now = datetime.now(user_tz)

    next_prayer = None
    min_diff = None

    for prayer, time_str in times.items():
        if prayer.lower() in ["imsak", "midnight", "sunset", "firstthird", "lastthird"]:
            continue
        prayer_time = datetime.strptime(time_str, "%H:%M")
        prayer_time = user_tz.localize(datetime.combine(now.date(), prayer_time.time()))
        if prayer_time > now:
            time_diff = (prayer_time - now).total_seconds()
            if min_diff is None or time_diff < min_diff:
                min_diff = time_diff
                next_prayer = (prayer, time_str)

    return next_prayer, int(min_diff / 60) if min_diff else None

def send_sms(prayer, time_str):
    sms_body = f"Reminder: {prayer} prayer is at {time_str}. Wudhu and prepare for prayer."
    message = client.messages.create(
        body=sms_body,
        from_=twilio_number,
        to=your_number
    )
    return message.sid

# --- Streamlit UI ---
st.title("🕌 Islamic Prayer Time App")
st.write("This app shows prayer times for your location and notifies you before the next prayer.")

# Fetch data
try:
    latitude, longitude = get_current_location()
    times, timezone = fetch_prayer_times(latitude, longitude)

    st.subheader("📍 Location")
    st.write(f"Latitude: {latitude}, Longitude: {longitude}")
    st.write(f"Timezone: {timezone}")

    st.subheader("🕐 Today's Prayer Times")
    for prayer, time_str in times.items():
        st.write(f"{prayer}: {time_str}")

    next_prayer, minutes_remaining = get_next_prayer(times, timezone)

    if next_prayer:
        st.subheader("🕓 Next Prayer")
        st.write(f"{next_prayer[0]} at {next_prayer[1]} ({minutes_remaining} minutes from now)")

        if minutes_remaining <= 5:
            if st.button("Send SMS Reminder"):
                sms_id = send_sms(next_prayer[0], next_prayer[1])
                st.success(f"SMS sent successfully! Message SID: {sms_id}")
        else:
            st.info("SMS button will appear when the next prayer is within 5 minutes.")
    else:
        st.success("✅ All prayers for today are complete.")

except Exception as e:
    st.error(f"Something went wrong: {e}")
