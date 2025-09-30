from dotenv import load_dotenv
from taxipred.utils.constants import TAXI_CSV_PATH, TAXI_CSV_PATH_WITH_WEATHER
import pandas as pd
import json
import plotly.express as px
import googlemaps
import os
from fastapi.responses import JSONResponse

load_dotenv() 

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

class TaxiData:
    '''Klass som läser in den rensade datan, innehåller metoder som returnerar data (KPI och plots)'''
    Trip_Distance_km: float
    Time_of_Day: str
    Base_Fare: float 
    Per_Km_Rate: float 
    Per_Minute_Rate: float 
    Trip_Duration_Minutes: float 
    Trip_Price: float 
    
    def __init__(self):
        self.df = pd.read_csv(TAXI_CSV_PATH)

    def to_json(self):
        return json.loads(self.df.to_json(orient = "records"))
    
    def avg_price(self):
        trip_data = {}
        time_limits = [10, 20, 30]
        
        for time in time_limits:
            trip = self.df[self.df['Trip_Duration_Minutes'] < time]
            avg_price = trip['Trip_Price'].mean()
            trip_data[time] = avg_price
            
        return trip_data
    
    # När är det dyrast att åka taxi
    def most_expensive(self):
        # Summera Trip_Price för varje Time_of_Day och returnera den med högst värde
        grouped = self.df.groupby("Time_of_Day")["Trip_Price"].sum()
        most_expensive_time = grouped.idxmax()
        return most_expensive_time
    
    # När åker flest taxi
    def most_popular_time(self):
        # Gruppera på Time_of_day, summera antalet träffar/rader, visa det som det finns flest av
        time_counts = self.df['Time_of_Day'].value_counts() # Returnera endast en sträng, gruppera inte med time of day,det gör redan value counts
        most_popular_time = time_counts.idxmax()
        return most_popular_time
    
    # Visa antal resor över tidperioder på dygnet
    def show_distribution(self):
        time_counts = self.df['Time_of_Day'].value_counts().reset_index()
        time_counts.columns = ["Tid på dygnet", "Antal resor"]

        fig = px.bar(
            time_counts,
            x="Tid på dygnet",
            y="Antal resor",
            title="Fördelning av resor över dygnet",
            color="Tid på dygnet",
            color_discrete_sequence=px.colors.sequential.YlOrRd
        )

        fig.update_layout(
            xaxis_title="Tid på dygnet",
            yaxis_title="Antal resor",
        )

        return fig 

    # Visa priset för de olika tidsperioderna på dygnet
    def show_price_by_time_of_day(self):
        """
        Skapar ett linjediagram över medelpriset per tidpunkt på dygnet.
        Returnerar figuren som dict (för JSON).
        """
        avg_prices = self.df.groupby("Time_of_Day")["Trip_Price"].mean().reset_index()

        # Mappa engelska till svenska
        mapping = {"Afternoon": "Eftermiddag", "Morning": "Morgon", "Evening": "Kväll", "Night": "Natt"}
        avg_prices["Tid på dygnet"] = avg_prices["Time_of_Day"].map(mapping)

        # Sortera kategoriskt för att få rätt ordning
        order = ["Morgon", "Eftermiddag", "Kväll", "Natt"]
        avg_prices["Tid på dygnet"] = pd.Categorical(avg_prices["Tid på dygnet"],
                                                     categories=order,
                                                     ordered=True)
        avg_prices = avg_prices.sort_values("Tid på dygnet")

        fig = px.line(
            avg_prices,
            x="Tid på dygnet",
            y="Trip_Price",
            markers=True,
            title="Genomsnittligt pris per tidpunkt på dygnet",
            line_shape="linear",
            labels={"Trip_Price": "Resans pris"}
        )

        return fig.to_dict()  # returnera som dict för JSON, tex { "Morgon": 12.5, "Eftermiddag": 15.0}
        

def show_duration_by_weather():
    df_weather = pd.read_csv(TAXI_CSV_PATH_WITH_WEATHER)
    # Ta bort rader utan väder
    df_weather = df_weather.dropna(subset=["Weather"])
    
    # Beräkna genomsnittlig restid per väder
    avg_duration = df_weather.groupby("Weather")["Trip_Duration_Minutes"].mean().reset_index()
    
    fig = px.bar(
        avg_duration,
        x="Weather",
        y="Trip_Duration_Minutes",
        title="Genomsnittlig restid per väderförhållande",
        labels={"Weather": "Väder", "Trip_Duration_Minutes": "Genomsnittlig restid (minuter)"},
        color="Weather",
        color_discrete_sequence=px.colors.sequential.Bluyl
    )
    
    return fig


def get_distance_duration(start_address: str, end_address: str):
    try:
        start_result = gmaps_client.geocode(start_address)
        end_result = gmaps_client.geocode(end_address)

        start_loc = start_result[0]["geometry"]["location"]
        end_loc = end_result[0]["geometry"]["location"]

        directions = gmaps_client.directions(
            (start_loc["lat"], start_loc["lng"]),
            (end_loc["lat"], end_loc["lng"]),
            mode="driving"
        )

        distance_km = directions[0]["legs"][0]["distance"]["value"] / 1000
        duration_min = directions[0]["legs"][0]["duration"]["value"] / 60
        
        # Skapa en lista med koordinater längs rutten
        steps = directions[0]["legs"][0]["steps"]
        route_coords = []
        for step in steps:
            start_step = step["start_location"]
            route_coords.append((start_step["lat"], start_step["lng"]))
        route_coords.append((end_loc["lat"], end_loc["lng"]))  # lägg till slutpunkten

        return {
            "distance_km": distance_km,
            "duration_minutes": duration_min,
            "route_coords": route_coords
        }

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
