from importlib.resources import files

TAXI_CSV_PATH = files("taxipred").joinpath("data/cleaned_data.csv")
# DATA_PATH = Path(__file__).parents[1] / "data"


MODEL_PATH = files("taxipred").joinpath("backend/models/linear_regression_model.pkl")
SCALER_PATH = files("taxipred").joinpath("backend/models/scaler.pkl")