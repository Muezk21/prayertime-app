import streamlit as st
from datetime import datetime
import pytz
from config import METHOD_NAMES, REGION_RECOMMENDATIONS, METHOD_DESCRIPTIONS
from geo import location_ui
from api import fetch_prayer_times
from notifier import send_sms

def show_region_recommendations():
    """Display regional calculation method recommendations"""
    st.subheader("🌍 Recommended by Region")
    with st.expander("Click to see recommendations for your region"):
        for region, methods in REGION_RECOMMENDATIONS.items():
            method_list = ", ".join([METHOD_NAMES[m] for m in methods])
            st.write(f"**{region}**: {method_list}")

def show_method_info(method):
    """Show description for selected calculation method"""
    if method in METHOD_DESCRIPTIONS:
        st.info(f"ℹ️ {METHOD_DESCRIPTIONS[method]}")

def display_prayer_times(times, timezone):
    """Display prayer times in a formatted grid"""
    st.subheader("🕐 Today's Prayer Times")
    
    main_prayers = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    prayer_icons = {
        "Fajr": "🌅", "Sunrise": "☀️", "Dhuhr": "🌞", 
        "Asr": "🌇", "Maghrib": "🌆", "Isha": "🌙"
    }
    
    cols = st.columns(2) if st.session_state.get('mobile', False) else st.columns(3)
    col_idx = 0
    
    for prayer in main_prayers:
        if prayer in times:
            with cols[col_idx % 3]:
                icon = prayer_icons.get(prayer, "🕌")
                st.metric(f"{icon} {prayer}", times[prayer])
                col_idx += 1

def get_next_prayer(times, timezone):
    """Calculate next prayer and time remaining"""
    try:
        user_tz = pytz.timezone(timezone)
        now = datetime.now(user_tz)
        prayer_order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

        for prayer in prayer_order:
            if prayer in times:
                time_str = times[prayer]
                try:
                    prayer_time = datetime.strptime(time_str, "%H:%M")
                    prayer_time = user_tz.localize(datetime.combine(now.date(), prayer_time.time()))

                    if prayer_time > now:
                        time_diff = (prayer_time - now).total_seconds()
                        minutes_remaining = int(time_diff / 60)
                        return (prayer, time_str), minutes_remaining
                except ValueError:
                    continue
        return None, None
    except Exception as e:
        st.error(f"Error calculating next prayer: {str(e)}")
        return None, None

def show_next_prayer(next_prayer, minutes_remaining):
    """Display next prayer information and handle SMS"""
    if not next_prayer:
        st.success("✅ All prayers for today are complete. May Allah accept all your prayers!")
        return

    st.subheader("🕓 Next Prayer")
    
    col1, col2 = st.columns(2)
    with col1:
        prayer_name, time_str = next_prayer
        st.write(f"**{prayer_name}** at {time_str}")
        
        if minutes_remaining <= 60:
            st.write(f"⏳ {minutes_remaining} minutes remaining")
        else:
            hours = minutes_remaining // 60
            mins = minutes_remaining % 60
            st.write(f"⏰ **{hours}h {mins}m** remaining")

    with col2:
        if minutes_remaining <= 5:
            st.success("🔔 Prayer time approaching!")
            if st.button("Send SMS Reminder", type="primary", use_container_width=True):
                with st.spinner("Sending SMS..."):
                    result = send_sms(prayer_name, time_str)
                    if result.startswith("SMS_ERROR"):
                        st.error(f"❌ {result}")
                    elif result == "SMS_NOT_CONFIGURED":
                        st.error("SMS not configured")
                    else:
                        st.success(f"✅ SMS sent! ID: {result}")
        elif minutes_remaining <= 15:
            st.warning("⏳ Prayer time approaching soon.")
        else:
            st.info("SMS button will appear when prayer is within 5 minutes.")

def main():
    st.title("🕌 Islamic Prayer Time App")
    st.write("This app shows prayer times for your location and notifies you before the next prayer.")
    
    # Mobile layout toggle for testing
    st.session_state['mobile'] = st.checkbox ("Mobile Layout", help="Toggle to test mobile view")
    
    # Region recommendations
    show_region_recommendations()
    
    # Location input
    lat, lon, city = location_ui()
    if lat is None:
        st.error("Please select a location method above")
        st.stop()
    
    # Method selection
    method = st.selectbox(
        "Select Calculation Method",
        options=list(METHOD_NAMES.keys()),
        format_func=lambda x: METHOD_NAMES[x]
    )
    show_method_info(method)
    
    # School selection
    school = st.selectbox(
        "Select Madhab for Asr", 
        options=[0, 1], 
        format_func=lambda x: "Shafi'i/Maliki/Hanbali" if x == 0 else "Hanafi"
    )
    
    try:
        # Fetch prayer times
        with st.spinner("Fetching prayer times..."):
            times, timezone = fetch_prayer_times(lat, lon, method, school)
        
        # Display location info
        if st.session_state.get('mobile', False):
            st.metric("📍 Latitude", f"{lat:.4f}")
            st.metric("📍 Longitude", f"{lon:.4f}")
            current_time = datetime.now(pytz.timezone(timezone)).strftime("%H:%M:%S")
            st.metric("🕐 Current Time", current_time)
        
        else:
            col1, col2, col3 = st.columns(3)      
            with col1:
                st.metric("📍 Latitude", f"{lat:.4f}")
            with col2:
                st.metric("📍 Longitude", f"{lon:.4f}")
            with col3:
                current_time = datetime.now(pytz.timezone(timezone)).strftime("%H:%M:%S")
                st.metric("🕐 Current Time", current_time)
        
        st.write(f"**Timezone:** {timezone}")
        st.write(f"**Calculation Method:** {METHOD_NAMES[method]}")
        
        # Display prayer times
        display_prayer_times(times, timezone)
        
        # Next prayer section
        next_prayer, minutes_remaining = get_next_prayer(times, timezone)
        show_next_prayer(next_prayer, minutes_remaining)
        
        # Additional times
        with st.expander("📊 Additional Islamic Times"):
            main_prayers = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
            other_times = {k: v for k, v in times.items() if k not in main_prayers}
            for time_name, time_value in other_times.items():
                st.write(f"**{time_name}:** {time_value}")
        
    except Exception as e:
        st.error(f"❌ Something went wrong: {str(e)}")
        st.info("💡 Please try refreshing the page or check your internet connection.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "📚 Data Source: "
        "<a href='https://aladhan.com/prayer-times-api' target='_blank'>"
        "Aladhan Prayer Times API</a>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()