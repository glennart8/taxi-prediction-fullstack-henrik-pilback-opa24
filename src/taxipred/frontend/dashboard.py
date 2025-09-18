import streamlit as st
from taxipred.utils.helpers import read_api_endpoint
import pandas as pd
import requests

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

data = read_api_endpoint("taxi")
df = pd.DataFrame(data.json())

avg_prices = read_api_endpoint("taxi/avg_price/")
avg_prices_data = avg_prices.json()

# Vad ska streamlit innehålla?
#   - Fält för att fylla i från och till destination, autoläsa in tidpunkt och dag
#   - Skapa en modell som tränar på data och testas, se resultat och justera efter behov
#   - Denna model ska anropas via en metod när man söker resa

#   - Visa KPIs för avg_price för resor i spannet 10 min, 20 min, 30 min
#   - Visa när det behövs flest taxibilar ute
#   - Visa när "vi" tjänar mest på att köra
#   - Visa ba chart på när på dygnet resor sker
#   - Restid per tid på dygnet: Använd ett stapeldiagram för att visa den genomsnittliga Trip_Duration_Minutes för varje Time_of_Day. Detta kan avslöja vilka tider som har mest trafik.

def main():
    st.markdown("# Taxi Prediction Dashboard")
    
    col_1, col_2, col_kpis = st.columns([3, 3, 2])
    
    with col_1:
        st.markdown("### Resa")
        st.dataframe(df)
        
    with col_2:
        st.markdown("### Charts")
        

    with col_kpis:
        st.markdown("### KPI:er")
        
        try:
            st.metric(label="Medelpris (< 10 min)", 
                     value=f"{avg_prices_data['10']:.2f} $")
            
            st.metric(label="Medelpris (< 20 min)", 
                     value=f"{avg_prices_data['20']:.2f} $")
            
            st.metric(label="Medelpris (< 30 min)", 
                     value=f"{avg_prices_data['30']:.2f} $")
            
        except requests.exceptions.ConnectionError:
            st.error("Kunde inte ansluta till API:et. Se till att din FastAPI-server körs.")
    
if __name__ == "__main__":
    main()