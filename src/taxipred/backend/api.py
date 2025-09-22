from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import joblib
import os
from taxipred.utils.constants import MODEL_PATH, SCALER_PATH

# --- Ladda modell och scaler ---
# Notera att vi använder .as_posix() för att få en strängsökväg
model = joblib.load(MODEL_PATH.as_posix())
scaler = joblib.load(SCALER_PATH.as_posix())

# Definiera de exakta kolumnerna som din modell tränades på
# Ordningen är mycket viktig!
TRAIN_COLUMNS = ['Trip_Distance_km', 'Base_Fare', 'Per_Km_Rate', 'Per_Minute_Rate', 'Trip_Duration_Minutes', 'Time_of_Day_Afternoon', 'Time_of_Day_Evening', 'Time_of_Day_Morning', 'Time_of_Day_Night']

# --- Pydantic-modell för inkommande data ---
# Definierar strukturen för den data som din API-endpoint tar emot.
class PredictRequest(BaseModel):
    distance_km: float
    trip_duration_minutes: float
    trip_datetime: datetime

# --- Funktion för att räkna ut tid på dygnet ---
def calculate_time_of_day(trip_datetime: datetime) -> str:
    """
    Konverterar en datetime till en kategorisk "tid på dygnet"-sträng.
    """
    hour = trip_datetime.hour
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 22:
        return "Evening"
    else:
        return "Night"

app = FastAPI()

@app.get("/taxi/")
async def read_taxi_data():
    taxi_data = TaxiData()
    return taxi_data.to_json()

@app.get("/taxi/avg_price/")
async def read_avg_price():
    taxi_data = TaxiData()
    return taxi_data.avg_price()

# @app.get("/taxi/search_trip/")
# async def search_trip():
#     taxi_data = TaxiData()
#     return taxi_data.search_trip()

# --- Endpoint för prisprediktion ---
@app.post("/predict_price/")
def predict_price(request: PredictRequest):
    """
    Tar emot rådata och returnerar ett predikterat taxipris.
    """
    # 1. Omvandla rådata till det format som modellen förväntar sig
    time_of_day = calculate_time_of_day(request.trip_datetime)
    
    # Skapa en Pandas DataFrame för den inkommande datan
    input_data = pd.DataFrame([[
        request.distance_km,
        request.trip_duration_minutes,
        time_of_day
    ]], columns=['Trip_Distance_km', 'Trip_Duration_Minutes', 'Time_of_Day'])

    # 2. One-Hot Encoding av den kategoriska variabeln
    input_data_encoded = pd.get_dummies(
        input_data, 
        columns=['Time_of_Day'],
        dtype=int
    )
    
    # 3. Lägg till eventuella saknade dummy-kolumner med värdet 0
    # Detta steg är avgörande för att undvika fel när en kategori saknas
    # (t.ex. om den inkommande tiden inte är "Morning")
    for col in TRAIN_COLUMNS:
        if col not in input_data_encoded.columns:
            input_data_encoded[col] = 0

    # 4. Säkerställ att kolumnordningen är EXAKT densamma som träningsdatan
    final_input_df = input_data_encoded[TRAIN_COLUMNS]
    
    # 5. Skala datan med den inlästa scalern
    scaled_data = scaler.transform(final_input_df)
    
    # 6. Gör prediktionen med den tränade modellen
    predicted_price = model.predict(scaled_data)[0]
    
    # 7. Returnera resultatet
    return {"predicted_price": round(predicted_price, 2)}