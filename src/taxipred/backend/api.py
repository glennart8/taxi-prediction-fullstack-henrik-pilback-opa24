from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData

app = FastAPI()

# taxi_data = TaxiData()

@app.get("/taxi/")
async def read_taxi_data():
    taxi_data = TaxiData()
    return taxi_data.to_json()

@app.get("/taxi/avg_price/")
async def read_avg_price():
    taxi_data = TaxiData()
    return taxi_data.avg_price()
