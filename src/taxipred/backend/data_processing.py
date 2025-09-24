from taxipred.utils.constants import TAXI_CSV_PATH
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns

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
    
    # Visa en barplot på fördelningen av antalet resor under dagen
    def show_distribution(self):
            """
            Skapar en barplot-figur över resor per tid på dygnet och returnerar den.
            """
            time_counts = self.df['Time_of_Day'].value_counts()
            
            # Skapa en Matplotlib-figur och en axel
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Rita diagrammet på den skapade axeln
            sns.barplot(x=time_counts.index, y=time_counts.values, ax=ax, palette='viridis')
            
            ax.set_title('Fördelning av resor per tid på dygnet', fontsize=16)
            ax.set_xlabel('Tid på dygnet', fontsize=12)
            ax.set_ylabel('Antal resor', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Returnera hela figuren
            return fig

        