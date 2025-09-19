import streamlit as st
from geopy.geocoders import Nominatim
import googlemaps
import os
from dotenv import load_dotenv
import requests
from taxipred.utils.helpers import read_api_endpoint, post_api_endpoint
import pandas as pd
from datetime import datetime

load_dotenv()

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
geolocator = Nominatim(user_agent="taxi_app")

# --- Streamlit ---
st.set_page_config(layout="wide", page_title="Taxi-prediction")
st.markdown(
    """
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url("https://images.unsplash.com/photo-1565531152238-5f20a0f4a3f0?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    st.markdown("# Taxi Prediction Dashboard")
    st.markdown("### Beräkna pris för din resa")

    start_address = st.text_input("Från:")
    end_address = st.text_input("Till:")

    if st.button("Beräkna pris"):
        if start_address and end_address:
            # Använd geopy för att hämta koordinater
            try:
                start_location = geolocator.geocode(start_address)
                end_location = geolocator.geocode(end_address)

                if start_location and end_location:
                    # Använd Google Maps för att beräkna körsträckan och tid
                    directions_result = gmaps.directions(
                        start_location.point,
                        end_location.point,
                        mode="driving"
                    )

                    if directions_result:
                        distance_meters = directions_result[0]['legs'][0]['distance']['value']
                        distance_km = distance_meters / 1000
                        duration_seconds = directions_result[0]['legs'][0]['duration']['value']
                        duration_minutes = duration_seconds / 60
                        st.success(f"Avståndet för din resa är: {distance_km:.2f} km")
                        st.success(f"Restiden är: {duration_minutes:.0f} minuter")
                        
                        # --- För beräkning av tidpunkt och dag ---
                        current_time = datetime.now()

                        # Skapa din enkla payload
                        payload = {
                            "distance_km": distance_km,
                            "trip_duration_minutes": duration_minutes,
                            "trip_datetime": current_time.isoformat() # Konvertera till en ISO-formaterad sträng
                        }
                        
                        # Anropa POST-endpoint i backend för att få prediktionen
                        response = post_api_endpoint(endpoint="/predict_price/", data=payload)
                        
                        if response and response.status_code == 200:
                            predicted_price = response.json()["predicted_price"]
                            st.metric(label="Predikterat pris", value=f"{predicted_price} kr")
                        else:
                            st.error(f"Kunde inte hämta pris. Kontrollera att din FastAPI-server körs.")

                    else:
                        st.error("Kunde inte beräkna en rutt mellan adresserna.")
                else:
                    st.error("Kunde inte hitta en eller båda adresserna. Vänligen försök igen.")
            
            except Exception as e:
                st.error(f"Ett fel uppstod: {e}")
        else:
            st.error("Vänligen fyll i både från- och till-adress.")

    
    data = read_api_endpoint("taxi")
    if data:
        df = pd.DataFrame(data.json())
        col_1, col_2, col_kpis = st.columns([3, 3, 2])
        
        with col_1:
            st.markdown("### Resedata")
            st.dataframe(df)
            
        with col_2:
            st.markdown("### Charts")
        
        with col_kpis:
            st.markdown("### KPI:er")
            avg_prices = read_api_endpoint("taxi/avg_price/")
            if avg_prices:
                avg_prices_data = avg_prices.json()
                st.metric(label="Medelpris (< 10 min)", value=f"{avg_prices_data['10']:.2f} $")
                st.metric(label="Medelpris (< 20 min)", value=f"{avg_prices_data['20']:.2f} $")
                st.metric(label="Medelpris (< 30 min)", value=f"{avg_prices_data['30']:.2f} $")
            else:
                st.error("Kunde inte ansluta till API:et.")
                
if __name__ == "__main__":
    main()