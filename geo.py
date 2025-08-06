import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_user_coords():
    """Get coordinates from the browser's geolocation API."""
    print("DEBUG: Entering get_user_coords")
    try:
        coords = streamlit_geolocation()
        if coords and coords.get("latitude") is not None and coords.get("longitude") is not None:
            lat, lon = coords["latitude"], coords["longitude"]
            if lat == 0 and lon == 0:
                logging.warning("Received invalid coordinates (0, 0) from browser GPS.")
                print("DEBUG: GPS returned (0,0)")
                return None, None
            print(f"DEBUG: GPS coordinates received: {lat}, {lon}")
            return lat, lon
    except Exception as e:
        logging.error(f"An error occurred in streamlit_geolocation: {e}")
        print(f"DEBUG: Error in get_user_coords: {e}")
    print("DEBUG: Exiting get_user_coords with None")
    return None, None

def get_ip_location():
    """
    Get location from IP address using a primary and a fallback service.
    """
    print("DEBUG: Entering get_ip_location")
    # 1. Primary Service: ipapi.co
    try:
        print("DEBUG: Trying ipapi.co...")
        response = requests.get('https://ipapi.co/json/', timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('latitude') and data.get('longitude'):
            logging.info("Successfully retrieved location from ipapi.co")
            print(f"DEBUG: ipapi.co successful: {data.get('city', 'Unknown')}")
            return data['latitude'], data['longitude'], data.get('city', 'Unknown')
    except requests.exceptions.RequestException as e:
        logging.warning(f"ipapi.co failed: {e}. Trying fallback service.")
        print(f"DEBUG: ipapi.co failed: {e}")

    # 2. Fallback Service: ipinfo.io
    try:
        print("DEBUG: Trying ipinfo.io (fallback)...")
        response = requests.get('https://ipinfo.io/json', timeout=5)
        response.raise_for_status()
        data = response.json()
        if 'loc' in data:
            lat, lon = map(float, data['loc'].split(','))
            city = data.get('city', 'Unknown')
            logging.info("Successfully retrieved location from ipinfo.io")
            print(f"DEBUG: ipinfo.io successful: {city}")
            return lat, lon, city
    except requests.exceptions.RequestException as e:
        logging.error(f"Fallback service ipinfo.io also failed: {e}")
        print(f"DEBUG: ipinfo.io failed: {e}")

    print("DEBUG: Exiting get_ip_location with None")
    return None, None, None

def location_ui():
    """UI for selecting location input method."""
    print("DEBUG: Entering location_ui")
    choice = st.radio(
        "Location input:",
        ["Browser GPS", "Auto IP Location", "Manual"],
        index=1, # Changed default to Auto IP Location
        help="GPS is most accurate, IP is automatic, Manual always works"
    )

    if choice == "Browser GPS":
        print("DEBUG: Location choice: Browser GPS")
        st.warning("Browser GPS requires browser permissions and a secure connection (HTTPS). It might not work in all environments.")
        lat, lon = get_user_coords()
        if lat is None or lon is None:
            st.warning("GPS unavailable or permission denied. Try another option.")
            print("DEBUG: Browser GPS failed or denied")
            return None, None, None
        else:
            st.success(f"📍 GPS location: {lat:.4f}, {lon:.4f}")
            print("DEBUG: Browser GPS successful")
            return lat, lon, None

    elif choice == "Auto IP Location":
        print("DEBUG: Location choice: Auto IP Location")
        with st.spinner("Getting location from IP..."):
            lat, lon, city = get_ip_location()
            if lat is None or lon is None:
                st.error("Automatic IP location failed. Please use Manual input.")
                print("DEBUG: Auto IP location failed")
                return None, None, None
            else:
                st.success(f"📍 IP location: {city} ({lat:.4f}, {lon:.4f})")
                print("DEBUG: Auto IP location successful")
                return lat, lon, city

    else:  # Manual
        print("DEBUG: Location choice: Manual")
        st.info("Enter your coordinates manually:")
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, format="%.6f")
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, format="%.6f")

        if lat == 0.0 and lon == 0.0:
            st.warning("Please enter your actual coordinates.")
            print("DEBUG: Manual input (0,0) - prompting for actual coords")
            return None, None, None

        print(f"DEBUG: Manual input successful: {lat}, {lon}")
        return lat, lon, "Manual"
