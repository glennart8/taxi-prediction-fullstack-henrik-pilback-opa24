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

# --- SPARA MODELL OCH SCALER ---
# Måste göras för att kunna använda dem i din API senare
joblib.dump(model, 'linear_regression_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
