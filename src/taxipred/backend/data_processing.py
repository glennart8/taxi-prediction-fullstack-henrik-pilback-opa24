from taxipred.utils.constants import TAXI_CSV_PATH
import pandas as pd
import json
from datetime import datetime 
# from pydantic import BaseModel, Field

# Behöver jag en klass för att träna modellen och en klass för att skicka in datan
# som simuleras med streamlit, den innehåller ju inte flera av de värden som taxidata har
class TaxiData:
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
    

        # -- Anropa modell --- 
        
        # if self.model:
        #     predicted_price = self.model.predict(input_data)[0]
        #     return {"predicted_price": round(predicted_price, 2)}
        