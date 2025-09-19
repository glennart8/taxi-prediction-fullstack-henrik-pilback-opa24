from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
from pydantic import BaseModel
from datetime import datetime

class PredictRequest(BaseModel):
    distance_km: float
    trip_duration_minutes: float
    trip_datetime: datetime # FastAPI/Pydantic konverterar ISO-strängen till ett datetime-objekt
    # Base_Fare
    # Per_Km_Rate
    # Per_Minute_Rate
    # Trip_Price

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

@app.post("/predict_price/")
async def predict_price(request: PredictRequest):
    # Anropa predict_price-metoden och skicka med datetime-objektet
    taxi_data = TaxiData()
    return taxi_data.predict_price(
        distance_km=request.distance_km,
        trip_duration_minutes=request.trip_duration_minutes,
        trip_datetime=request.trip_datetime
    )