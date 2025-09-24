import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import joblib
from taxipred.utils.constants import TAXI_CSV_PATH

df = pd.read_csv(TAXI_CSV_PATH)

# Dummy encoding för kategoriska variabler
df = pd.get_dummies(
    df,
    columns=['Time_of_Day'],
    dtype=int
)

# --- DEFINIERA FEATURES OCH TARGET ---
X = df.drop("Trip_Price", axis="columns")
y = df["Trip_Price"]

# --- TRAIN-TEST SPLIT ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=42
)

# --- SKALNING ---
scaler = MinMaxScaler()
scaler.fit(X_train)

scaled_X_train = scaler.transform(X_train)
scaled_X_test = scaler.transform(X_test)

# --- MODELLTRÄNING ---
model = LinearRegression()
model.fit(scaled_X_train, y_train)

print("Kolumner använda för träning:", X_train.columns.tolist())
# Kolumner använda för träning:
# ['Trip_Distance_km', 'Base_Fare', 'Per_Km_Rate', 'Per_Minute_Rate', 'Trip_Duration_Minutes', 'Time_of_Day_Afternoon', 'Time_of_Day_Evening', 'Time_of_Day_Morning', 'Time_of_Day_Night']

# --- SPARA MODELL OCH SCALER ---
joblib.dump(model, 'linear_regression_model_no_outliers.joblib')
joblib.dump(scaler, 'scaler_no_outliers.joblib')
