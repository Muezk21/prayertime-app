import streamlit as st
import requests
import geocoder
import pytz
from datetime import datetime
from dotenv import load_dotenv
import os
from twilio.rest import Client

# --- Constants & Config ---
#Prayer calculation methods
method_names = {
    1: "Islamic Society of North America (ISNA)", 
    2: "University of Islamic Sciences, Karachi",
    3: "Muslim World League (MWL)",
    4: "Umm Al-Qura University, Makkah",
    5: "Egyptian General Authority of Survey",
    7: "Institute of Geophysics, University of Tehran",
    8: "Gulf Region",
    9: "Kuwait", 
    10: "Qatar",
    11: "Majlis Ugama Islam Singapura, Singapore",
    12: "Union Organization Islamic de France",
    14: "Spiritual Administration of Muslims of Russia",
    15: "Moonsighting Committee Worldwide (Moonsighting.com)",
    17: "Jabatan Kemajuan Islam Malaysia (JAKIM)",
    18: "Tunisia",
    19: "Algeria", 
    20: "Kementerian Agama Republik Indonesia",
    21: "Morocco",
    22: "Comunidade Islamica de Lisboa (Portugal)",
    23: "Ministry of Awqaf, Islamic Affairs and Holy Places, Jordan",
    99: "Custom (requires manual fajr/isha angles)"
}

#Regional reccommendations for better user experience
region_reccommendations = {
    "US North America": [1], #ISNA
    "🇸🇦 Saudi Arabia": [4],   # Umm Al-Qura, Makkah
    "🌍 Most Muslim Countries": [3],  # MWL
    "🇵🇰 Pakistan/India": [2], # Karachi
    "🇪🇬 Egyptian General Authority of Survey": [5],  # Egyptian
    "🇮🇷 Iran": [7],           # Tehran
    "🇦🇪 UAE": [8],            # Gulf Region
    "🇰🇼 Kuwait": [9],         # Kuwait
    "🇶🇦 Qatar": [10],         # Qatar
    "🇸🇬 Singapore": [11],     # Singapore
    "🇲🇾 Malaysia": [17],      # JAKIM
    "🇫🇷 France": [12],        # France
    "🇷🇺 Russia": [14],        # Russia
    "🇩🇿 Algeria": [19],       # Algeria
    "🇹🇳 Tunisia": [18],       # Tunisia
    "🇲🇦 Morocco": [21],       # Morocco
    "🇮🇩 Indonesia": [20],     # Kemenag
    "🇵🇹 Portugal": [22],      # Portugal
    "🇯🇴 Jordan": [23],        # Jordan
    "🌙 Moonsighting": [15],    # Moonsighting Committee
}

# Load environment variables
load_dotenv()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
your_number = os.getenv("YOUR_PHONE_NUMBER")

if account_sid and auth_token:
    client = Client(account_sid, auth_token)
else:
    client = None
    st.warning("Twilio credentials not set. SMS notifications will be disabled.")

# --- Streamlit UI: User Inputs ---
st.title("🕌 Islamic Prayer Time App")
st.write("This app shows prayer times for your location and notifies you before the next prayer.")

st.subheader("🌍 Recommended by Region")
with st.expander("Click to see recommendations for your region"):
    for region, methods in region_reccommendations.items():
        method_list = ", ".join([method_names[m] for m in methods])
        st.write(f"**{region}**: {method_list}")

method = st.selectbox(
    "Select Calculation Method",
    options=list(method_names.keys()),
    format_func=lambda x: method_names[x]
    )
method_descriptions = {
    1: "Standard in USA and Canada. Conservative approach. Fajr: 15°, Isha: 15°.",
    2: "Used widely in Pakistan, India, Bangladesh, and Afghanistan. Fajr: 18°, Isha: 18°.",
    3: "Used in Europe, Far East, and parts of America. Most widely accepted. Fajr: 18°, Isha: 17°.",
    4: "Used in Saudi Arabia for Hajj and Umrah. Fajr: 18.5°, Isha: 90 minutes after Maghrib.",
    5: "Used in Egypt, Syria, Lebanon, and parts of Asia. Fajr: 19.5°, Isha: 17.5°.",
    7: "Used in Iran and surrounding regions. Fajr: 17.7°, Isha: 14°.",
    8: "Used in UAE and other Gulf states. Fajr: 19.5°, Isha: 90 minutes after Maghrib.",
    9: "Official method for Kuwait. Fajr: 18°, Isha: 17.5°.",
    10: "Official method for Qatar. Fajr: 18°, Isha: 90 minutes after Maghrib.",
    11: "Official method for Singapore. Fajr: 20°, Isha: 18°.",
    12: "Used by Muslim communities in France. Fajr: 12°, Isha: 12°.",
    14: "Used in Russia and surrounding regions. Fajr: 16°, Isha: 15°.",
    15: "Based on actual moon sighting reports worldwide. Uses general Shafaq.",
    17: "Official method for Malaysia. Fajr: 20°, Isha: 18°.",
    18: "Official method for Tunisia. Fajr: 18°, Isha: 18°.",
    19: "Official method for Algeria. Fajr: 18°, Isha: 17°.",
    20: "Official method for Indonesia. Fajr: 20°, Isha: 18°.",
    21: "Official method for Morocco. Fajr: 19°, Isha: 17°.",
    22: "Used in Portugal. Fajr: 18°, Maghrib: +3 min, Isha: +77 min.",
    23: "Official method for Jordan. Fajr: 18°, Maghrib: +5 min, Isha: 18°.",
    99: "Allows custom Fajr and Isha angles (advanced users only)."
}

if method in method_descriptions:
    st.info(f"ℹ️ {method_descriptions[method]}")

# Select Madhab for Asr
school = st.selectbox(
    "Select Madhab for Asr", 
    options=[0, 1], 
    format_func=lambda x: "Shafi'i/Maliki/Hanbali" if x == 0 else "Hanafi"
)

if school == 0:
    st.info("You are following the Shafi’i method for Asr.")
else:
    st.info("You are following the Hanafi method for Asr (Asr starts later).")

# --- Core Functions ---
def get_current_location():
    st.subheader("📍 Get Current Location")

    city = st.text_input(
        "Enter your city",
        placeholder="e.g. New York, Riyadh, Karachi",
        help="Enter city name or 'City, Country' for better accuracy"
    )

    if city:
        with st.spinner("Finding your city..."):
            try:
                g = geocoder.osm(city) # Use OpenStreetMap
                if g.ok:
                    st.success(f"✅ Found: {g.address}")
                    st.info(f"📍 Coordinates: {g.latlng[0]:.4f}, {g.latlng[1]:.4f}")
                    return g.latlng
                else:
                    st.error("Could not determine current location. Please check spelling or try 'City, Country' format.")
                    st.stop()
            except Exception as e:
                st.error(f"Error fetching location: {str(e)}")
                st.stop()
    else:
        st.info("Please enter your city to get prayer times.")
        st.write("**Example:** 'New York, USA' or 'Karachi, Pakistan'")
        st.stop()

def fetch_prayer_times(lat, lon, method=2, school=0):
    try:
        url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method={method}&school={school}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["timings"], data["data"]["meta"]["timezone"]
        else:
            raise Exception(f"API error: {response.status_code}")           
        
    ## Attempt to fetch prayer times from Aladhan API and handle possible errors gracefully
    except requests.exceptions.Timeout:
        raise Exception("API request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(f"API error: {str(e)}")

def get_next_prayer(times, timezone):
    try:        #<--protect against missing timezone
        user_tz = pytz.timezone(timezone)
        now = datetime.now(user_tz)
        prayer_order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

        next_prayer = None
        min_diff = None
        
        for prayer in prayer_order:
            if prayer in times:
                time_str = times[prayer]
                try:
                    prayer_time = datetime.strptime(time_str, "%H:%M")
                    prayer_time = user_tz.localize(datetime.combine(now.date(), prayer_time.time()))

                    if prayer_time > now:
                        time_diff = (prayer_time - now).total_seconds()
                        if min_diff is None or time_diff < min_diff:
                            min_diff = time_diff
                            next_prayer = (prayer, time_str)
                            break #Found the next prayer, no need to check further 
                except ValueError:           
                    continue  # Skip if time format is invalid

        return next_prayer, int(min_diff / 60) if min_diff else None
    
    except Exception as e:
        st.error(f"Error calculating next prayer: {str(e)}")
        return None, None
    
def send_sms(prayer, time_str):
    if not client:
        return "SMS_NOT_CONFIGUERED"
    
    try:
        sms_body = f"Reminder: {prayer} prayer is at {time_str}. Wudhu and prepare for prayer."
        message = client.messages.create(
            body=sms_body,
            from_=twilio_number,
            to=your_number
        )
        return message.sid
    except Exception as e:
        return f"SMS-ERROR: {str(e)}"

# --- Main App Logic ---
try:
    with st.spinner("Fetching prayer times..."):
        latitude, longitude = get_current_location()
        times, timezone = fetch_prayer_times(latitude, longitude, method=method, school=school)

    #Display location info
    col1, col2, col3 =st.columns(3)
    with col1:
        st.metric("📍 Latitude", f"{latitude:.4f}")
    with col2:
        st.metric("📍 Longitude", f"{longitude:.4f}")
    with col3:
        current_time = datetime.now(pytz.timezone(timezone)).strftime("%H:%M:%S")
        st.metric("🕐 Current Time", current_time)
   
    st.write(f"**Timezone:** {timezone}")
    st.write(f"**Calculation Method:** {method_names[method]}")

    # Display prayer times in a nice format
    st.subheader("🕐 Today's Prayer Times")

    #Filter out non-prayer times for display
    main_prayers = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]

    cols = st.columns(3)
    col_idx = 0
    
    for prayer in main_prayers:
        if prayer in times:
            with cols[col_idx % 3]:
                #Add emoji for each prayer
                prayer_icons = {
                    "Fajr": "🌅", "Sunrise": "☀️", "Dhuhr": "🌞", 
                    "Asr": "🌇", "Maghrib": "🌆", "Isha": "🌙"
                }
                icon = prayer_icons.get(prayer, "🕌")
                st.metric(f"{icon} {prayer}", times[prayer])
                col_idx += 1
    
    #Next prayer section
    next_prayer, minutes_remaining = get_next_prayer(times, timezone)

    if next_prayer:
        st.subheader("🕓 Next Prayer")

        # Prominent display for next prayer
        col1, col2 =st.columns ([2, 1])
        with col1:
            st.write(f"***{next_prayer[0]}** at {next_prayer[1]}")
            if minutes_remaining <= 60:
                st.write(f"⏳ {minutes_remaining} minutes remaining")
            else:
                hours = minutes_remaining // 60
                mins = minutes_remaining % 60
                st.write(f"⏰ **{hours}h {mins}m** remaining")

        with col2:
            if minutes_remaining <= 5:
                st.success("🔔 Prayer time approaching!")
                if st.button("Send SMS Reminder", typw="primary"):
                    with st.spinner("Sending SMS..."):
                        sms_result = send_sms(next_prayer[0], next_prayer[1])

                        if sms_result == "SMS_NOT_CONFIGUERED":
                            st.error("SMS notifications are not configured. Please set up Twilio credentials or check your .env file.")
                        elif sms_result.startswith("SMS-ERROR:"):
                            st.error(f" ❌ {sms_result}")
                        else:
                            st.success(f"✅ SMS sent successfully! Message ID: {sms_result}")
            elif minutes_remaining <= 15:
                st.warning("⏳ Prayer time approaching soon.")
            else:
                st.info("SMS button will appear when the next prayer is within 5 minutes.")
    else:
        st.success("✅ All prayers for today are complete. May Allah accept all your prayers!")
    
    # Additional Islamic times (optional display)
    with st.expander("📊 Additional Islamic Times"):
        other_times = {k: v for k, v in times.items() if k not in main_prayers}
        for time_name, time_value in other_times.items():
            st.write(f"**{time_name}:** {time_value}")  

except Exception as e:
    st.error(f"❌ Something went wrong: {str(e)}")
    st.info("💡 Please try refreshing the page or check your internet connection.")

     # Provide some debugging info
    with st.expander("🔧 Technical Details"):
        st.write("If this error persists, please check:")
        st.write("- Internet connection")
        st.write("- API service availability") 
        st.write("- Selected calculation method compatibility")
        st.write(f"- Method selected: {method} - {method_names.get(method, 'Unknown')}")

# Footer
st.markdown("---")
st.write("**📚 Data Source:** [Aladhan Prayer Times API](https://aladhan.com/prayer-times-api)")