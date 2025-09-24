from importlib.resources import files

# TAXI_CSV_PATH = files("taxipred").joinpath("data/cleaned_data.csv")
TAXI_CSV_PATH = files("taxipred").joinpath("data/cleaned_data_no_outliers.csv")


MODEL_PATH = files("taxipred").joinpath("backend/models/linear_regression_model.joblib")
SCALER_PATH = files("taxipred").joinpath("backend/models/scaler.joblib")

MODEL_RF = files("taxipred").joinpath("backend/models/random_forest_model.joblib")