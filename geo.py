import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_user_coords():
    """Get coordinates from the browser's geolocation API."""
    try:
        coords = streamlit_geolocation()
        if coords and coords.get("latitude") is not None and coords.get("longitude") is not None:
            lat, lon = coords["latitude"], coords["longitude"]
            # Treat (0, 0) as an invalid location, as it's a common default/error value
            if lat == 0 and lon == 0:
                logging.warning("Received invalid coordinates (0, 0) from browser GPS.")
                return None, None
            return lat, lon
    except Exception as e:
        logging.error(f"An error occurred in streamlit_geolocation: {e}")
    return None, None

def get_ip_location():
    """
    Get location from IP address using a primary and a fallback service.
    """
    # 1. Primary Service: ipapi.co
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('latitude') and data.get('longitude'):
            logging.info("Successfully retrieved location from ipapi.co")
            return data['latitude'], data['longitude'], data.get('city', 'Unknown')
    except requests.exceptions.RequestException as e:
        logging.warning(f"ipapi.co failed: {e}. Trying fallback service.")

    # 2. Fallback Service: ipinfo.io
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        response.raise_for_status()
        data = response.json()
        if 'loc' in data:
            lat, lon = map(float, data['loc'].split(','))
            city = data.get('city', 'Unknown')
            logging.info("Successfully retrieved location from ipinfo.io")
            return lat, lon, city
    except requests.exceptions.RequestException as e:
        logging.error(f"Fallback service ipinfo.io also failed: {e}")

    # Return None if all services fail
    return None, None, None

def location_ui():
    """UI for selecting location input method."""
    choice = st.radio(
        "Location input:",
        ["Browser GPS", "Auto IP Location", "Manual"],
        index=0,
        help="GPS is most accurate, IP is automatic, Manual always works"
    )

    if choice == "Browser GPS":
        lat, lon = get_user_coords()
        if lat is None or lon is None:
            st.warning("GPS unavailable or permission denied. Try another option.")
            return None, None, None
        else:
            st.success(f"📍 GPS location: {lat:.4f}, {lon:.4f}")
            return lat, lon, None

    elif choice == "Auto IP Location":
        with st.spinner("Getting location from IP..."):
            lat, lon, city = get_ip_location()
            if lat is None or lon is None:
                st.error("Automatic IP location failed. Please use Manual input.")
                return None, None, None
            else:
                st.success(f"📍 IP location: {city} ({lat:.4f}, {lon:.4f})")
                return lat, lon, city

    else:  # Manual
        st.info("Enter your coordinates manually:")
        # Using a default that is clearly not a real location for prayer times
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, format="%.6f")
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, format="%.6f")

        if lat == 0.0 and lon == 0.0:
            st.warning("Please enter your actual coordinates.")
            return None, None, None

        return lat, lon, "Manual"
