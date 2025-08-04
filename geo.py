import streamlit as st
from streamlit_geolocation import streamlit_geolocation 
import requests

def get_user_coords():
    coords = streamlit_geolocation.geolocation(timeout=10_000)
    # Fix the 0 coordinate bug
    if coords and coords.get("lat") is not None and coords.get("lon") is not None:
        return coords["lat"], coords["lon"]
    return None, None

def get_ip_location():
    """Automatic IP-based location as fallback"""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        response.raise_for_status()
        data = response.json()
        
        lat = data.get('latitude')
        lon = data.get('longitude')
        city = data.get('city', 'Unknown')
        
        if lat is not None and lon is not None:
            return lat, lon, city
        return None, None, None
    except:
        return None, None, None

def location_ui():
    # Add IP geolocation as middle option
    choice = st.radio(
        "Location input:", 
        ["Browser GPS", "Auto IP Location", "Manual"], 
        index=0,
        help="GPS is most accurate, IP is automatic, Manual always works"
    )
    
    if choice == "Browser GPS":
        lat, lon = get_user_coords()
        if lat is None:
            st.warning("GPS unavailable. Try 'Auto IP Location' or switch to Manual.")
            # Don't stop - let user choose different option
            return None, None
        else:
            st.success(f"📍 GPS location: {lat:.4f}, {lon:.4f}")
            
    elif choice == "Auto IP Location":
        with st.spinner("Getting location from IP..."):
            lat, lon, city = get_ip_location()
            if lat is None:
                st.error("IP location failed. Please use Manual input.")
                return None, None
            else:
                st.success(f"📍 IP location: {city} ({lat:.4f}, {lon:.4f})")
                
    else:  # Manual
        st.info("Enter your coordinates manually:")
        lat = st.number_input("Latitude", format="%.6f", help="Example: 40.7128 for New York")
        lon = st.number_input("Longitude", format="%.6f", help="Example: -74.0060 for New York")
        
        if lat == 0.0 and lon == 0.0:
            st.warning("Please enter your actual coordinates")
            return None, None
    
    return lat, lon