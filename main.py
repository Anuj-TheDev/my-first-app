import streamlit as st
from google import genai
from dotenv import load_dotenv
import time
import requests
import pandas as pd


client = genai.Client()
# st.title("🌍✈️AS Travel Assistant")
st.markdown("""
<style>
.banner {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #0f2027, #1565c0, #00b4ff);
    border-radius: 20px;
    padding: 40px 20px 30px 20px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0, 120, 255, 0.35);
    margin-bottom: 20px;
}
.banner-title {
    position: relative;
    z-index: 2;
    color: white;
    font-size: 3rem;
    font-weight: 800;
    margin: 0;
}
.marquee {
    position: relative;
    z-index: 2;
    overflow: hidden;
    white-space: nowrap;
    margin-top: 12px;
    background: rgba(255, 255, 255, 0.12);
    border-radius: 30px;
    padding: 6px 0;
}
.marquee span {
    display: inline-block;
    padding-left: 100%;
    color: #d6ecff;
    font-size: 1.2rem;
    animation: scrollText 14s linear infinite;
}
.marquee:hover span {
    animation-play-state: paused;
}
.plane-fly {
    position: absolute;
    top: 12px;
    left: -60px;
    font-size: 2.5rem;
    z-index: 3;
    animation: fly 7s linear infinite, bob 1.5s ease-in-out infinite;
}
.cloud {
    position: absolute;
    font-size: 2.5rem;
    opacity: 0.35;
    z-index: 1;
    animation: drift 18s linear infinite;
}
.cloud.c1 { top: 55%; left: 100%; }
.cloud.c2 { top: 15%; left: 100%; animation-duration: 25s; animation-delay: -8s; }
@keyframes scrollText {
    0% { transform: translateX(0); }
    100% { transform: translateX(-100%); }
}
@keyframes fly {
    0% { left: -60px; }
    100% { left: 100%; }
}
@keyframes bob {
    0%, 100% { margin-top: 0; }
    50% { margin-top: 12px; }
}
@keyframes drift {
    0% { transform: translateX(0); }
    100% { transform: translateX(-130vw); }
}
</style>
<div class="banner">
<div class="plane-fly">✈️</div>
<div class="cloud c1">☁️</div>
<div class="cloud c2">☁️</div>
<div class="banner-title">AS Travel Assistant</div>
<div class="marquee"><span>🌍 Plan your dream trip in seconds... ✨ Pick a destination, days and budget... 🏖️ Get your itinerary, photo, weather and map! 🧳</span></div>
</div>
""", unsafe_allow_html=True)



st.caption("24/7 Planning trips  !!!")
location=st.text_input("Where do you want to Escape?")
days=st.number_input("How many days of Trip", min_value=1, max_value=30)
budget=st.selectbox("Select  Budget",["Luxury","Moderate","Budgeted"])
travel_type=st.radio("Who are you travelling with",["Family","Solo","Friends"])
language = st.selectbox("Language", ["English", "Hindi", "Marathi"])

def get_place_image(location):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": location,
        "gsrlimit": 1,
        "prop": "pageimages",
        "piprop": "thumbnail",
        "pithumbsize": 800,
        "format": "json",
    }
    wiki_headers = {"User-Agent": "TravelAssistantApp/1.0"}
    try:
        r = requests.get(url, params=params, headers=wiki_headers, timeout=5)
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            return page.get("thumbnail", {}).get("source")
    except Exception:
        pass
    return None


def get_weather(location):
    try:
        g = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                         params={"name": location, "count": 1}, timeout=5).json()
        loc = g["results"][0]
        w = requests.get("https://api.open-meteo.com/v1/forecast",
                         params={"latitude": loc["latitude"],
                                 "longitude": loc["longitude"],
                                 "current_weather": True}, timeout=5).json()
        return loc["latitude"], loc["longitude"], w["current_weather"]
    except Exception:
        return None

    
def get_bot_response(location):
    return f"Here are the travel details about {location}..."





prompt=f"""You are a travel planner and for eg if user ask you he want to go to {location} and he is on the budget on the type {budget} and he is travelling with {travel_type} then you should plan trip for {days} days and also you have to give the image of the {location} which is given by user and show picture and give the answer in the user selected {language} give answer in bullet points"""
if st.button("Plan Trip !"):
    with st.spinner("Planning Trip...", show_time=True):
            time.sleep(3)

    interaction = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt
    )

    if location:
        bot_response = get_bot_response(location)

        with st.expander("Show details"):
            st.write(bot_response)

            image_url = get_place_image(location)
            if image_url:
                st.image(image_url, caption=location)
            else:
                st.write("No image available")

            weather = get_weather(location)
            if weather:
                lat, lon, cw = weather
                col1, col2 = st.columns(2)
                col1.metric("🌡️ Temperature", f"{cw['temperature']} °C")
                col2.metric("💨 Wind", f"{cw['windspeed']} km/h")
                st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
            else:
                st.write("Weather and map not available")    
    st.success("Happy vacations Mate!!")
    st.write(interaction.output_text)
    st.snow()
    st.download_button(
    "📥 Download itinerary",
    interaction.output_text,
    file_name=f"{location}_trip_plan.txt"
)














    