# ui.py

import streamlit as st
from datetime import datetime, timedelta # <--- Added timedelta here
import pytz
import time as time_sleep
from config import METHOD_NAMES, REGION_RECOMMENDATIONS, METHOD_DESCRIPTIONS, PRAYER_ORDER
from geo import location_ui
from api import fetch_prayer_times
from notifier import send_sms

def render_header():
    """Sets the page config and renders the main header."""
    st.set_page_config(page_title="Islamic Prayer Times", page_icon="🕌", layout="centered")
    st.title("🕌 Islamic Prayer Times")
    st.text(
        "Welcome! This app provides accurate prayer times based on your location "
        "with a live countdown to the next prayer."
    )

def render_settings_panel():
    """Renders the collapsible settings panel for location and calculation method."""
    with st.expander("⚙️ Tap to Change Settings", expanded=False):
        st.subheader("📍 Location")
        lat, lon, city = location_ui()

        st.subheader("🕋 Calculation")
        method = st.selectbox(
            "Calculation Method",
            options=list(METHOD_NAMES.keys()),
            format_func=lambda x: METHOD_NAMES[x],
            help="Select the prayer time calculation method. ISNA is common in North America."
        )
        school = st.selectbox(
            "Asr Juristic Method (Madhab)",
            options=[0, 1],
            format_func=lambda x: "Shafi'i, Maliki, Hanbali" if x == 0 else "Hanafi",
            help="The Hanafi school observes a later time for Asr prayer."
        )
            
        if method in METHOD_DESCRIPTIONS:
            st.info(f"Method Info: {METHOD_DESCRIPTIONS[method]}", icon="ℹ️")
            
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
                continue # Skip if time format is incorrect
    
    # If all prayers are done, find Fajr of the next day
    try:
        fajr_time_str = times.get("Fajr")
        if fajr_time_str:
            fajr_time_obj = datetime.strptime(fajr_time_str, "%H:%M").time()
            tomorrow_date = now_local.date() + timedelta(days=1) # Corrected usage
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
        
        st.subheader(f"Next Prayer: {prayer_name} at {prayer_dt.strftime('%H:%M')}", anchor=False)
        
        # Live Countdown Timer
        countdown_placeholder = st.empty()
        
        while total_seconds > 0:
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # This use of st.markdown is safe and broadly compatible
            countdown_text = f"⏳ **{hours:02}:{minutes:02}:{seconds:02}**"
            countdown_placeholder.markdown(countdown_text)
            
            time_sleep.sleep(1)
            total_seconds -= 1
            if total_seconds < 1: # Loop exit condition
                countdown_placeholder.success("Prayer time has begun!", icon="🎉")
                break
    else:
        st.success("All prayers for today seem to be complete. See you tomorrow for Fajr!", icon="✅")


def render_details_tab(times):
    """Renders the secondary tab with additional times and regional recommendations."""
    st.subheader("Additional Times", anchor=False)
    
    main_prayers_and_sunrise = {"Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"}
    other_times = {k: v for k, v in times.items() if k not in main_prayers_and_sunrise}
    
    if other_times:
        st.table(other_times)
    else:
        st.info("No additional times available with the selected calculation method.")

    st.subheader("Regional Method Recommendations", anchor=False)
    for region, methods in REGION_RECOMMENDATIONS.items():
        method_list = ", ".join([METHOD_NAMES[m] for m in methods])
        st.text(f"{region}: {method_list}")

def render_footer():
    """Renders the footer using st.text for maximum compatibility."""
    st.divider()
    st.text("Data provided by Aladhan API (aladhan.com).")
    st.text("App designed to be your daily prayer companion.")

def main():
    """Main function to run the Streamlit app."""
    render_header()
    
    lat, lon, city, method, school = render_settings_panel()

    if not lat or not lon:
        st.warning("Please set your location in the settings panel above to see prayer times.", icon="☝️")
        st.stop()

    try:
        # Fetch data once
        times, timezone = fetch_prayer_times(lat, lon, method, school)
        
        # Calculate next prayer info once
        next_prayer_info = get_next_prayer(times, timezone)

        # Create tabs
        tab1, tab2 = st.tabs(["Prayer Times", "Details & Recommendations"])

        with tab1:
            render_prayer_times_tab(times, timezone, next_prayer_info)

        with tab2:
            render_details_tab(times)
            
    except Exception as e:
        st.error(f"❌ Failed to fetch prayer times: {e}", icon="🔥")
        st.warning("Please check your internet connection or try different settings.")
    
    render_footer()

if __name__ == "__main__":
    main()