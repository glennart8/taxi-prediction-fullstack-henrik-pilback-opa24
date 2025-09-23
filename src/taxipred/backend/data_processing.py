from taxipred.utils.constants import TAXI_CSV_PATH
import pandas as pd
import json

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
    
    def most_expensive(self):
        # Summera Trip_Price för varje Time_of_Day och returnera den med högst värde
        grouped = self.df.groupby("Time_of_Day")["Trip_Price"].sum()
        most_expensive_time = grouped.idxmax()
        return most_expensive_time
    
    def most_popular_time(self):
        pass
    
    