from importlib.resources import files

# TAXI_CSV_PATH = files("taxipred").joinpath("data/cleaned_data.csv")

# --- WITOUT OUTLIERS ---
TAXI_CSV_PATH = files("taxipred").joinpath("data/cleaned_data_no_outliers.csv")
TAXI_CSV_PATH_WITH_WEATHER = files("taxipred").joinpath("data/cleaned_data_with_weather.csv")


# --- LINEAR REGRESSION ---
# MODEL_PATH = files("taxipred").joinpath("backend/models/linear_regression_model.joblib")
# SCALER_PATH = files("taxipred").joinpath("backend/models/scaler.joblib")


MODEL_PATH = files("taxipred").joinpath("backend/models/linear_regression_model_no_outliers.joblib")
SCALER_PATH = files("taxipred").joinpath("backend/models/scaler_no_outliers.joblib")

# --- RANDOM FOREST ---
# MODEL_RF = files("taxipred").joinpath("backend/models/random_forest_model.joblib")
MODEL_RF = files("taxipred").joinpath("backend/models/random_forest_model_no_outliers.joblib")