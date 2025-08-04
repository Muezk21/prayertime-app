import requests
from streamlit import cache_data


@cache_data(ttl=3600)
def fetch_prayer_times(lat, lon, method, school):
    url = (
      f"https://api.aladhan.com/v1/timings"
      f"?latitude={lat}&longitude={lon}"
      f"&method={method}&school={school}"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    raw = resp.json()  # DEBUG: show the entire response
    print("🛠️ Raw Aladhan response:", raw)
    
    data = raw["data"]
    print("🔑 Keys in data:", list(data.keys()))
    print("⏲️ Keys in timings:", list(data["timings"].keys()))
    print("🌐 Keys in meta:", list(data["meta"].keys()))

   
    

    return data["timings"], data["meta"]["timezone"]
