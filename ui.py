import streamlit as st
from datetime import datetime, timedelta
import pytz
import time as time_sleep
from config import METHOD_NAMES, REGION_RECOMMENDATIONS, METHOD_DESCRIPTIONS, PRAYER_ORDER
from geo import location_ui
from api import fetch_prayer_times
from notifier import send_sms

def render_header():
    """Renders the main header and sets page config."""
    st.set_page_config(page_title="Islamic Prayer Times", page_icon="🕌", layout="centered")
    st.title("🕌 Islamic Prayer Times")
    st.text(
        "Welcome! This app provides accurate prayer times based on your location "
        "with a live countdown to the next prayer."
    )

def render_settings_in_sidebar():
    """Renders all settings (location, calculation, madhab) in the Streamlit sidebar."""
    st.sidebar.title("⚙️ Settings")
    st.sidebar.markdown("Adjust your location and prayer calculation preferences here.")

    st.sidebar.subheader("📍 Location")
    lat, lon, city = location_ui() # geo.py handles location UI

    st.sidebar.subheader("🕋 Calculation Method")
    method = st.sidebar.selectbox(
        "Select a method:",
        options=list(METHOD_NAMES.keys()),
        format_func=lambda x: METHOD_NAMES[x],
        help="Choose the prayer time calculation method. ISNA is common in North America."
    )
    school = st.sidebar.selectbox(
        "Asr Juristic Method (Madhab):",
        options=[0, 1],
        format_func=lambda x: "Shafi'i, Maliki, Hanbali" if x == 0 else "Hanafi",
        help="The Hanafi school observes a later time for Asr prayer."
    )
        
    if method in METHOD_DESCRIPTIONS:
        st.sidebar.info(f"**Method Info:** {METHOD_DESCRIPTIONS[method]}", icon="ℹ️")
        
    return lat, lon, city, method, school

def get_next_prayer(times, timezone):
    """Calculates the next prayer, its time, and the remaining time in seconds."""
    user_tz = pytz.timezone(timezone)
    now_utc = datetime.now(pytz.utc)
    now_local = now_utc.astimezone(user_tz)

    for prayer in PRAYER_ORDER:
        if prayer in times:
            try:
                prayer_time_obj = datetime.strptime(times[prayer], "%H:%M").time()
                prayer_datetime = user_tz.localize(datetime.combine(now_local.date(), prayer_time_obj))

                if prayer_datetime > now_local:
                    time_diff_seconds = (prayer_datetime - now_local).total_seconds()
                    return prayer, prayer_datetime, int(time_diff_seconds)
            except ValueError:
                continue
    
    # If all prayers are done, find Fajr of the next day
    try:
        fajr_time_str = times.get("Fajr")
        if fajr_time_str:
            fajr_time_obj = datetime.strptime(fajr_time_str, "%H:%M").time()
            tomorrow_date = now_local.date() + timedelta(days=1)
            fajr_datetime = user_tz.localize(datetime.combine(tomorrow_date, fajr_time_obj))
            time_diff_seconds = (fajr_datetime - now_local).total_seconds()
            return "Fajr (Tomorrow)", fajr_datetime, int(time_diff_seconds)
    except (ValueError, KeyError):
        pass

    return None, None, 0

def render_prayer_times_tab(times, timezone, next_prayer_info):
    """Renders the main tab with prayer times and the next prayer countdown."""
    st.header("Today's Prayer Schedule", anchor=False)
    
    prayer_icons = {"Fajr": "🌅", "Sunrise": "☀️", "Dhuhr": "🌞", "Asr": "🌇", "Maghrib": "🌆", "Isha": "🌙"}
    main_prayers = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    
    # Using 3 columns for desktop, wraps for mobile automatically with Streamlit
    cols = st.columns(3)
    for i, prayer in enumerate(main_prayers):
        col = cols[i % 3]
        if prayer in times:
            is_next = next_prayer_info and prayer == next_prayer_info[0]
            with col:
                st.metric(
                    label=f"{prayer_icons.get(prayer, '🕌')} {prayer}",
                    value=times[prayer]
                )
                if is_next:
                    st.success("Up next!", icon="✅")

    st.divider()

    # --- Next Prayer Countdown ---
    if next_prayer_info and next_prayer_info[2] > 0:
        prayer_name, prayer_dt, total_seconds = next_prayer_info
        
        # Display next prayer info prominently
        st.subheader(f"Next Prayer: {prayer_name} at {prayer_dt.strftime('%H:%M')}", anchor=False)
        
        # Live Countdown Timer (fixed size, takes less vertical space)
        countdown_col, sms_col = st.columns([0.7, 0.3]) # Adjust column ratio
        
        with countdown_col:
            countdown_placeholder = st.empty()
            
            while total_seconds > 0:
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                # Make countdown large and clear
                countdown_text = f"<h2 style='text-align: center; color: #4CAF50;'>⏳ {hours:02}:{minutes:02}:{seconds:02}</h2>"
                countdown_placeholder.markdown(countdown_text, unsafe_allow_html=True)
                
                time_sleep.sleep(1)
                total_seconds -= 1
                if total_seconds < 1:
                    countdown_placeholder.success("Prayer time has begun! Refresh for new times.", icon="🎉")
                    break
        with sms_col:
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True) # Spacer
            if next_prayer_info[2] <= 5 * 60: # within 5 minutes
                if st.button("Send SMS Reminder", type="primary", use_container_width=True):
                    with st.spinner("Sending SMS..."):
                        result = send_sms(prayer_name, prayer_dt.strftime('%H:%M'))
                        if "Error" in result:
                            st.error(result)
                        else:
                            st.success(f"✅ SMS sent successfully! SID: {result}")
            else:
                st.info("SMS option appears 5 min before prayer.", icon="⏱️")
    else:
        st.success("All prayers for today seem to be complete. See you tomorrow for Fajr!", icon="✅")


def render_details_tab(times):
    """Renders the secondary tab with additional times and regional recommendations."""
    st.subheader("Additional Times", anchor=False)
    
    # Filter out main prayers and sunrise from additional times
    main_prayers_and_sunrise = {"Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"}
    other_times = {k: v for k, v in times.items() if k not in main_prayers_and_sunrise}
    
    if other_times:
        # Display as a table for better readability
        st.table(other_times)
    else:
        st.info("No additional times available with the selected calculation method or API response.", icon="💡")

    st.subheader("Regional Method Recommendations", anchor=False)
    for region, methods in REGION_RECOMMENDATIONS.items():
        method_list = ", ".join([METHOD_NAMES[m] for m in methods])
        st.text(f"**{region}:** {method_list}")

def render_footer():
    """Renders the footer."""
    st.divider()
    st.markdown(
        "<div style='text-align: center; font-size: small; color: grey;'>"\
        "Data provided by <a href='https://aladhan.com/prayer-times-api'>Aladhan API</a>. "\
        "App designed to be your daily prayer companion."\
        "</div>",
        unsafe_allow_html=True # Small, centered footer HTML is generally safe
    )

def main():
    """Main function to run the Streamlit app."""
    render_header() # Renders main title and intro

    # Render settings in the sidebar and get inputs
    lat, lon, city, method, school = render_settings_in_sidebar()

    if not lat or not lon:
        st.warning("Please select a location in the sidebar settings to see prayer times.", icon="☝️")
        st.stop()

    try:
        # Fetch prayer times and timezone once
        with st.spinner("Fetching prayer times..."):
            times, timezone = fetch_prayer_times(lat, lon, method, school)
        
        # Display current location and time at the top of the main content
        st.markdown(f"### Prayer times for **{city or 'Your Location'}** ({timezone})")
        
        current_time_display = datetime.now(pytz.timezone(timezone)).strftime("%H:%M:%S")
        st.metric("Current Local Time", current_time_display, help=f"Your device's local time: {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown(f"Calculation Method: **{METHOD_NAMES[method]}**")
        st.divider() # Visual separation

        # Create tabs for content organization
        tab1, tab2 = st.tabs(["Prayer Times", "Details & Recommendations"])

        with tab1:
            render_prayer_times_tab(times, timezone, get_next_prayer(times, timezone))

        with tab2:
            render_details_tab(times)
            
    except Exception as e:
        st.error(f"❌ Failed to fetch prayer times: {e}", icon="🔥")
        st.warning("Please check your internet connection or try different settings in the sidebar.", icon="💡")
    
    render_footer() # Renders footer
