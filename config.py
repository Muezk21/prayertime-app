METHOD_NAMES = {
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

#Regional recommendations for better user experience
REGION_RECOMMENDATIONS = {
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


prayer_order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]