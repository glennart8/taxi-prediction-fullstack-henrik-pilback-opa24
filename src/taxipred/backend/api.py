from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import joblib
from taxipred.utils.constants import MODEL_PATH, SCALER_PATH, MODEL_RF
from fastapi.responses import JSONResponse
import plotly.io as pio
import googlemaps
import os
from dotenv import load_dotenv


load_dotenv()
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
app = FastAPI()

# --- Ladda modell och scaler ---
# .as_posix() för att få en strängsökväg
model_lr = joblib.load(MODEL_PATH.as_posix())
model_rf = joblib.load(MODEL_RF.as_posix())
scaler = joblib.load(SCALER_PATH.as_posix())

# Kolumnerna som modellen tränats på i exakt ordning - en konstant
TRAIN_COLUMNS = ['Trip_Distance_km', 
                 'Base_Fare', 
                 'Per_Km_Rate', 
                 'Per_Minute_Rate', 
                 'Trip_Duration_Minutes', 
                 'Time_of_Day_Afternoon', 
                 'Time_of_Day_Evening', 
                 'Time_of_Day_Morning', 
                 'Time_of_Day_Night']


# --- Pydantic-modell för inkommande data ---
# Definierar strukturen för den data som API-endpoint tar emot.
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

def prepare_input_data(request: PredictRequest) -> pd.DataFrame:
    """
    Förbereder inkommande data från PredictRequest för prediktion.
    """
    # Anropa funktion som konverterar tidpunkt till sträng
    time_of_day = calculate_time_of_day(request.trip_datetime)

    # Skapa en DataFrame för den inkommande datan
    df_to_predict = pd.DataFrame([[
        request.distance_km,
        request.trip_duration_minutes,
        time_of_day
    ]], columns=['Trip_Distance_km', 'Trip_Duration_Minutes', 'Time_of_Day'])

    # One-Hot Encoding av den kategoriska variabeln Time_of_Day
    input_data_encoded = pd.get_dummies(
        df_to_predict,
        columns=['Time_of_Day'],
        dtype=int
    )

    # Lägg till eventuella saknade dummy-kolumner med värdet 0
    for col in TRAIN_COLUMNS:
        if col not in input_data_encoded.columns:
            input_data_encoded[col] = 0

    # Säkerställ att kolumnordningen är EXAKT densamma som träningsdatan
    return input_data_encoded[TRAIN_COLUMNS]


@app.get("/taxi/distance_duration/")
async def distance_duration(start_address: str, end_address: str):
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

        return {"distance_km": distance_km, "duration_minutes": duration_min}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# --- API-ANROP ---

@app.get("/taxi/")
async def read_taxi_data():
    taxi_data = TaxiData()
    return taxi_data.to_json()

@app.get("/taxi/avg_price/")
async def read_avg_price():
    taxi_data = TaxiData()
    return taxi_data.avg_price()

@app.get("/taxi/most_expensive/")
async def read_most_expensive():
    taxi_data = TaxiData()
    return taxi_data.most_expensive()

@app.get("/taxi/most_customers/")
async def read_most_customers():
    taxi_data = TaxiData()
    return taxi_data.most_popular_time()

# --- Endpoint för prisprediktion ---
@app.post("/predict_price/")
async def predict_price(request: PredictRequest):
    """
    Tar emot rådata och returnerar predikterade taxipriser från två modeller.
    """
    # Förbered datan med en separat funktion för renare kod
    final_input_df = prepare_input_data(request)
    
    # Skala datan (enligt din befintliga kod)
    scaled_data = scaler.transform(final_input_df)
    
    # Gör prediktioner med båda modellerna
    predicted_price_lr = model_lr.predict(scaled_data)[0]
    predicted_price_rf = model_rf.predict(final_input_df)[0]
    
    # Returnerar en dictionary med tydliga nycklar för varje prediktion
    return {
        "predicted_price_lr": round(predicted_price_lr, 2),
        "predicted_price_rf": round(predicted_price_rf, 2)
    }


# --- PLOTS ---

@app.get("/taxi/distribution_plot")
async def get_distribution_plot():
    taxi_data = TaxiData()
    fig = taxi_data.show_distribution()  # fig från TaxiData
    fig_json_str = pio.to_json(fig)      # konvertera korrekt
    return JSONResponse(content=fig_json_str)


@app.get("/taxi/price_plot/")
async def get_price_plot():
    taxi_data = TaxiData()
    fig = taxi_data.show_price_by_time_of_day()
    
    # Konvertera till JSON-sträng som hanterar NumPy
    fig_json_str = pio.to_json(fig)  
    return JSONResponse(content=fig_json_str)
