import streamlit as st
from geopy.geocoders import Nominatim
import googlemaps
import os
from dotenv import load_dotenv
from taxipred.utils.helpers import read_api_endpoint, post_api_endpoint
import pandas as pd
from datetime import datetime

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
        background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url("https://images.unsplash.com/photo-1565531152238-5f20a0f4a3f0?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown("# Uppskatta taxiresa")
st.markdown("### Beräkna pris för din resa")

col1, col2, col3 = st.columns([1, 2, 2])

with col1:
    start_address = st.text_input("Från:")
    end_address = st.text_input("Till:")

if st.button("Uppskatta pris"):
    if start_address and end_address:
        # geopy för att hämta koordinater
        try:
            start_location = geolocator.geocode(start_address)
            end_location = geolocator.geocode(end_address)

            if start_location and end_location:
                # Google Maps för att beräkna körsträckan och tid
                directions_result = gmaps.directions(
                    start_location.point,
                    end_location.point,
                    mode="driving"
                )

                distance_km = directions_result[0]['legs'][0]['distance']['value'] / 1000
                duration_minutes = directions_result[0]['legs'][0]['duration']['value'] / 60

                with col2:
                    st.write("")
                    st.success(f"Avståndet för din resa är: {distance_km:.2f} km")
                    st.write("")
                    st.success(f"Restiden är: {duration_minutes:.0f} minuter")
                
                current_time = datetime.now()

                input_data = {
                    "distance_km": distance_km,
                    "trip_duration_minutes": duration_minutes,
                    "trip_datetime": current_time.isoformat() 
                }
                
                # Anropa POST-endpoint i backend
                response = post_api_endpoint(endpoint="/predict_price/", data=input_data)
                
                # Sparar api-responsen i en variabel och skriver ut den
                predicted_prices = response.json()
                
                # Hämta priserna från den uppdaterade JSON-strukturen
                predicted_price_lr = predicted_prices.get("predicted_price_lr", 0)
                predicted_price_rf = predicted_prices.get("predicted_price_rf", 0)
                
                # Omvandla till svenska kr
                price_predicted_sek_lr = predicted_price_lr * 9.35
                price_predicted_sek_rf = predicted_price_rf * 9.35
                
                # --- Visa pris ----
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(label="Uppskattat pris (Linear Regression)", value=f"{price_predicted_sek_lr:.2f} kr")

                with col2:
                    st.metric(label="Uppskattat pris (Random Forest)", value=f"{price_predicted_sek_rf:.2f} kr")
                 
            else:
                st.error("Kunde inte hitta en eller båda adresserna. Vänligen försök igen.")
        
        except Exception as e:
            st.error(f"Ett fel uppstod: {e}")
    else:
        st.error("Fyll i både från- och till-adresserna.")


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
        st.markdown("### KPI:s")
        avg_prices = read_api_endpoint("taxi/avg_price/")         
        avg_prices_data = avg_prices.json()
        sek = 9.35
        
        price_sek_10 = avg_prices_data['10'] * sek
        price_sek_20 = avg_prices_data['20'] * sek
        price_sek_30 = avg_prices_data['30'] * sek
        
        st.metric(label="Medelpris (< 10 min)", value=f"{price_sek_10:.2f} :-")
        st.metric(label="Medelpris (< 20 min)", value=f"{price_sek_20:.2f} :-")
        st.metric(label="Medelpris (< 30 min)", value=f"{price_sek_30:.2f} :-")
        
        # Dyrast resa
        most_expensive = read_api_endpoint("taxi/most_expensive")
        most_expensive_trip = most_expensive.json()
        
        #Känns fel, men ett enkelt sätt, tar inte hänsyn till de andra
        if most_expensive_trip == "Afternoon":
            value="Eftermiddag"
        if most_expensive_trip == "Morning":
            value="Morgon"
        if most_expensive_trip == "Evening":
            value="Kväll"
        if most_expensive_trip == "Night":
            value="Natt"
        
        st.metric(label="Tidpunkt för dyrast resa: ", value=value)
        
        
        
        # Tidpunkt då flest åker
        most_customers = read_api_endpoint("/taxi/most_customers")
        most_customers_time_of_day = most_customers.json()
        
        # Kanske fel sätt, men gör de andra if-satserna också
        if most_customers_time_of_day == "Afternoon":
            value="Eftermiddag"
        if most_customers_time_of_day == "Morning":
            value="Morgon"
        if most_customers_time_of_day == "Evening":
            value="Kväll"
        if most_customers_time_of_day == "Night":
            value="Natt"
        st.metric(label="Flest resenärer: ", value=value)

        