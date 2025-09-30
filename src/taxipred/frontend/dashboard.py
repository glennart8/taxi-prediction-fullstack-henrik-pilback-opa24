import streamlit as st
from datetime import datetime 
from taxipred.utils.helpers import read_api_endpoint, post_api_endpoint
import pandas as pd
import plotly.graph_objects as go
import json
import folium
from streamlit_folium import st_folium

# --- To Do ---

# Få till alternativ när man skriver i en adress?


sek = 9.35

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
        # color: #F5A78C;
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

# --- Initiera session_state ---
if "distance_km" not in st.session_state:
    st.session_state["distance_km"] = None
if "duration_minutes" not in st.session_state:
    st.session_state["duration_minutes"] = None
if "predicted_prices" not in st.session_state:
    st.session_state["predicted_prices"] = None
if "route_coords" not in st.session_state:
    st.session_state["route_coords"] = None

if st.button("Uppskatta pris"):
    # --- Hämta avstånd och tid från backend ---
    params = {"start_address": start_address, "end_address": end_address}
    response = read_api_endpoint("/taxi/distance_duration/", params=params)

    if response.status_code == 200:
        data = response.json()
        st.session_state["distance_km"] = data["distance_km"]
        st.session_state["duration_minutes"] = data["duration_minutes"]
        st.session_state["route_coords"] = data["route_coords"]  # för kartan

        # --- Skicka till prediktionsendpoint ---
        input_data = {
            "distance_km": data["distance_km"],
            "trip_duration_minutes": data["duration_minutes"],
            "trip_datetime": datetime.now().isoformat()
        }
        
        price_response = post_api_endpoint("/predict_price/", data=input_data)
        
        if price_response.status_code == 200:
            st.session_state["predicted_prices"] = price_response.json() # Spara värdet för session state
        else:
            st.error("Kunde inte hämta pris från backend.")
    else:
        st.error("Kunde inte hämta avstånd och tid från backend.")

# --- Visa avstånd och restid ---
if st.session_state["distance_km"] is not None:
    st.success(f"Avstånd: {st.session_state['distance_km']:.2f} km")
if st.session_state["duration_minutes"] is not None:
    st.success(f"Restid: {st.session_state['duration_minutes']:.0f} minuter")

# --- Visa prediktion ---
if st.session_state["predicted_prices"] is not None:
    predicted_prices = st.session_state["predicted_prices"]
    st.metric("Uppskattat pris (Random Forest)", f"{predicted_prices['predicted_price_rf']*sek:.2f} kr")

# --- Visa karta ---
if st.session_state["route_coords"] is not None:
    route_coords = st.session_state["route_coords"]
    m = folium.Map(location=route_coords[0], zoom_start=10, tiles="OpenStreetMap")
    folium.Marker(location=route_coords[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(location=route_coords[-1], popup="Slut", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(m)
    st_folium(m, width=700, height=500)

# --- KPI:S ---
with col_right:
    st.header("📈 KPI:s")
    avg_prices = read_api_endpoint("taxi/avg_price/").json()
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

# with col_data:  
    
    # JAG VILL VISA MIN KARTA HÄR!
    
#     data = read_api_endpoint("taxi")
#     if data and data.status_code == 200:
#         df = pd.DataFrame(data.json())
#         with st.expander("📊 Visa resedata"):
#             st.dataframe(df)
#     else:
#         st.warning("Ingen resedata kunde hämtas just nu.")
        
with col_plot:    
    tab1, tab2, tab3 = st.tabs(["Fördelning av resor", "Prisgenomsnitt över dygn", "Korrelation - väder och tid"])

    with tab1:
        st.header("🕒 Fördelning av resor per tid på dygnet")
        # Skicka GET-request till backend-endpoint 
        response = read_api_endpoint("/taxi/distribution_plot")
        if response.status_code == 200:
            # Spara JSON-response som sträng
            fig_json_str = response.json()
            # Omvandla JSON-sträng till dict
            fig_json = json.loads(fig_json_str)
            # Skapa en pålotly-fig från dict  
            fig = go.Figure(fig_json)
            # Visa
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
            
    import plotly.io as pio

with tab3:
        st.subheader("⏱️ Genomsnittlig restid per väderförhållande")
        response = read_api_endpoint("/taxi/duration_by_weather/")

        if response.status_code == 200:
            fig_json = response.json()          # sträng som JSON
            fig = pio.from_json(fig_json)       # gör om till Plotly-figur
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Kunde inte hämta diagrammet för väder och restid")
