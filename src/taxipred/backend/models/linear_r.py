from taxipred.utils.constants import TAXI_CSV_PATH
import pandas as pd


df = pd.read_csv(TAXI_CSV_PATH)
print(df)


