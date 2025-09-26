import streamlit as st
import googlemaps
import os
from dotenv import load_dotenv
from datetime import datetime 
from taxipred.utils.helpers import read_api_endpoint, post_api_endpoint
import pandas as pd
import plotly.graph_objects as go
import plotly_express as px
import json


# --- Setup ---
load_dotenv()
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# --- Streamlit ---
st.set_page_config(layout="wide", page_title="Taxi-prediction")
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
        url("https://images.unsplash.com/photo-1565531152238-5f20a0f4a3f0?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    </style>
""", unsafe_allow_html=True)

# --- Input & KPI:er ---
col_left, col_right = st.columns([3,2])

with col_left:
    st.title("🚖 Uppskatta pris på taxiresa")
    st.header("Beräkna pris för din resa")
    start_address = st.text_input("Från:")
    end_address = st.text_input("Till:")

    if st.button("Uppskatta pris"):
        # --- Hämta avstånd och tid från backend ---
        params = {"start_address": start_address, "end_address": end_address}
        with st.spinner("Hämtar avstånd och restid..."):
            response = read_api_endpoint("/taxi/distance_duration/", params=params)

        if response.status_code == 200:
            data = response.json()
            distance_km = data["distance_km"]
            duration_minutes = data["duration_minutes"]
            
            st.success(f"Avstånd: {distance_km:.2f} km")
            st.success(f"Restid: {duration_minutes:.0f} minuter")
            
            current_time = datetime.now()
            
            # --- spara inputs i dict och skicka till prediktionsendpointen ---
            input_data = {
                "distance_km": distance_km,
                "trip_duration_minutes": duration_minutes,
                "trip_datetime": current_time.isoformat()
            }
        
            price_response = post_api_endpoint("/predict_price/", data=input_data)
            
            if price_response.status_code == 200:
                predicted_prices = price_response.json()
                st.metric("Uppskattat pris (Linear Regression)", f"{predicted_prices['predicted_price_lr']*9.35:.2f} kr")
                st.metric("Uppskattat pris (Random Forest)", f"{predicted_prices['predicted_price_rf']*9.35:.2f} kr")
            else:
                st.error("Kunde inte hämta pris från backend.")
        else:
            st.error("Kunde inte hämta avstånd och tid från backend.")
            


with col_right:
    st.header("📈 KPI:s")
    avg_prices = read_api_endpoint("taxi/avg_price/").json()
    sek = 9.35
    col_kpi_left, col_kpi_right = st.columns(2)

    with col_kpi_left:
        st.metric("Medelpris (<10 min)", f"{avg_prices['10']*sek:.2f} :-")
        st.metric("Medelpris (<20 min)", f"{avg_prices['20']*sek:.2f} :-")
        st.metric("Medelpris (<30 min)", f"{avg_prices['30']*sek:.2f} :-")

    with col_kpi_right:
        mapping = {"Afternoon": "Eftermiddag", "Morning": "Morgon", "Evening": "Kväll", "Night": "Natt"}
        st.metric("Tidpunkt för dyrast resa", mapping.get(read_api_endpoint("taxi/most_expensive").json(), "N/A"))
        st.metric("Flest resenärer", mapping.get(read_api_endpoint("/taxi/most_customers").json(), "N/A"))
        
        st.feedback(options="stars", key=None, disabled=False, on_change=None, args=None, kwargs=None, width="content")

# --- Resedata & Plot ---
col_data, col_plot = st.columns([3,3])

with col_data:
    data = read_api_endpoint("taxi")
    if data and data.status_code == 200:
        df = pd.DataFrame(data.json())
        with st.expander("📊 Visa resedata"):
            st.dataframe(df)
    else:
        st.warning("Ingen resedata kunde hämtas just nu.")

with col_plot:    
    tab1, tab2 = st.tabs(["Fördelning av resor", "Prisgenomsnitt över dygn"])

    with tab1:
        st.header("🕒 Fördelning av resor per tid på dygnet")
        response = read_api_endpoint("/taxi/distribution_plot")
        if response.status_code == 200:
            fig_json_str = response.json()
            fig_json = json.loads(fig_json_str)  # omvandla JSON-sträng till dict
            fig = go.Figure(fig_json)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Kunde inte hämta distributionsdiagrammet")

    with tab2:
        st.header("📈 Prisgenomsnitt över dygnet")
        response = read_api_endpoint("/taxi/price_plot/")
        if response.status_code == 200:
            fig_json_str = response.json()
            # Konvertera JSON-sträng till dict
            fig_json = json.loads(fig_json_str)
            fig = go.Figure(fig_json)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Kunde inte hämta prisdiagrammet")