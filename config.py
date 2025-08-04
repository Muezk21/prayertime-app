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

prayer_order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]