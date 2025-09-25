import streamlit as st
from geopy.geocoders import Nominatim
import googlemaps
import os
from dotenv import load_dotenv
from taxipred.utils.helpers import read_api_endpoint, post_api_endpoint
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import json

# --- Setup ---
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
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("https://images.unsplash.com/photo-1565531152238-5f20a0f4a3f0?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Input & KPI:er ---

col_left, col_right = st.columns([3, 2])

with col_left:
    st.title("Uppskatta pris på taxiresa")
    st.header("Beräkna pris för din resa")
    start_address = st.text_input("Från:")
    end_address = st.text_input("Till:")

    if st.button("Uppskatta pris"):
        if start_address and end_address:
            try:
                start_location = geolocator.geocode(start_address)
                end_location = geolocator.geocode(end_address)

                if start_location and end_location:
                    directions_result = gmaps.directions(
                        start_location.point,
                        end_location.point,
                        mode="driving"
                    )

                    distance_km = directions_result[0]['legs'][0]['distance']['value'] / 1000
                    duration_minutes = directions_result[0]['legs'][0]['duration']['value'] / 60

                    st.success(f"Avstånd: {distance_km:.2f} km")
                    st.success(f"Restid: {duration_minutes:.0f} minuter")

                    current_time = datetime.now()
                    input_data = {
                        "distance_km": distance_km,
                        "trip_duration_minutes": duration_minutes,
                        "trip_datetime": current_time.isoformat()
                    }

                    response = post_api_endpoint(endpoint="/predict_price/", data=input_data)
                    predicted_prices = response.json()
                    predicted_price_lr = predicted_prices.get("predicted_price_lr", 0)
                    predicted_price_rf = predicted_prices.get("predicted_price_rf", 0)
                    price_predicted_sek_lr = predicted_price_lr * 9.35
                    price_predicted_sek_rf = predicted_price_rf * 9.35

                    st.metric("Uppskattat pris (Linear Regression)", f"{price_predicted_sek_lr:.2f} kr")
                    st.metric("Uppskattat pris (Random Forest)", f"{price_predicted_sek_rf:.2f} kr")

                else:
                    st.error("Kunde inte hitta adresserna.")
            except Exception as e:
                st.error(f"Ett fel uppstod: {e}")
        else:
            st.error("Fyll i både från- och till-adresserna.")

with col_right:
    st.header("KPI:s")
    avg_prices = read_api_endpoint("taxi/avg_price/").json()
    sek = 9.35
    
    col_kpi_left, col_kpi_right = st.columns(2)
    
    with col_kpi_left:
        st.metric("Medelpris (<10 min)", f"{avg_prices['10']*sek:.2f} :-")
        st.metric("Medelpris (<20 min)", f"{avg_prices['20']*sek:.2f} :-")
        st.metric("Medelpris (<30 min)", f"{avg_prices['30']*sek:.2f} :-")

    with col_kpi_right:
        # Skapar dicten mapping för att mappa engelska namn med svenska 
        mapping = {"Afternoon": "Eftermiddag", "Morning": "Morgon", "Evening": "Kväll", "Night": "Natt"}
        most_expensive = read_api_endpoint("taxi/most_expensive").json()
        st.metric("Tidpunkt för dyrast resa", mapping.get(most_expensive, most_expensive))

        most_customers = read_api_endpoint("/taxi/most_customers").json()
        st.metric("Flest resenärer", mapping.get(most_customers, most_customers))

# ---Resedata & Plot ---

col_data, col_plot = st.columns([3, 3])

with col_data:
    st.header("Resedata")
    data = read_api_endpoint("taxi")
    if data:
        df = pd.DataFrame(data.json())
        st.dataframe(df)

with col_plot:
    st.header("Fördelning av resor per tid på dygnet")
    response = read_api_endpoint("/taxi/distribution_plot")
    if response.status_code == 200:
        fig_json = response.json()
        fig = go.Figure(json.loads(fig_json))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Fel från API: {response.status_code}")
