from taxipred.utils.constants import TAXI_CSV_PATH
import pandas as pd
import json
from datetime import datetime 
from pydantic import BaseModel, Field

# Behöver jag en klass för att träna modellen och en klass för att skicka in datan
# som simuleras med streamlit, den innehåller ju inte flera av de värden som taxidata har
class TaxiData(BaseModel):
    Trip_Distance_km: float = Field(gt=0) 
    Time_of_Day: str
    Day_of_Week: str
    Base_Fare: float = Field(gt=0)
    Per_Km_Rate: float = Field(gt=0)
    Per_Minute_Rate: float = Field(gt=0)
    Trip_Duration_Minutes: float = Field(gt=0)
    Trip_Price: float = Field(gt=0)
    
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
 
    def predict_price(self, distance_km: float, trip_duration_minutes: float, trip_datetime: datetime):

        # Konvertera datetime-värdena till strings för att kunna mappa mot datasetet
        hour = trip_datetime.hour
        if 5 <= hour < 12:
            time_of_day = "Morning"
        elif 12 <= hour < 17:
            time_of_day = "Afternoon"
        elif 17 <= hour < 22:
            time_of_day = "Evening"
        else:
            time_of_day = "Night"
        
        # Ta ut endast veckodag (vet inte om den kan matcha engelska)
        day_of_week = trip_datetime.strftime('%A')
        
        input_data = pd.DataFrame([[
            distance_km,
            trip_duration_minutes,
            time_of_day,
            day_of_week
        ]], columns=['Trip_Distance_km', 'Trip_Duration_Minutes', 'Time_of_Day', 'Day_of_Week'])
        
        # -- Anropa modell --- 
        
        # if self.model:
        #     predicted_price = self.model.predict(input_data)[0]
        #     return {"predicted_price": round(predicted_price, 2)}
        