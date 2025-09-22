# Taxi prediction app

TODO: add selling/marketing exlanations of what this project is about:

# Vad ska streamlit innehålla?
#   - Fält för att fylla i från och till destination, autoläsa in tidpunkt och dag
#   - Skapa en modell som tränar på data och testas, se resultat och justera efter behov
#   - Denna model ska anropas via en metod när man söker resa

#   - Visa KPIs för avg_price för resor i spannet 10 min, 20 min, 30 min
#   - Visa när det behövs flest taxibilar ute
#   - Visa när "vi" tjänar mest på att köra
#   - Visa ba chart på när på dygnet resor sker
#   - Restid per tid på dygnet: Använd ett stapeldiagram för att visa den genomsnittliga Trip_Duration_Minutes för varje Time_of_Day. Detta kan avslöja vilka tider som har mest trafik.


1. Från Streamlit till FastAPI: HTTP-förfrågan
anropar post_api_endpoint i helpers.py

2. helpers.py skapar ett HTTP-anrop
Den konverterar din Python-data (input_data) till en textsträng i JSON-format.

3. FastAPI tar emot anropet
FastAPI, som kör på din server, lyssnar på inkommande anrop
Den kollar i koden och ser att jag har definierat just en sådan endpoint: @app.post("/predict_price/").
FastAPI vet då att det är JUST DEN funktionen (predict_price) som ska köras.
Det är INTE funktionsnamnet som kopplar ihop dem, utan webbadressen.

4. predict_price körs och returnerar data
return {"predicted_price": round(predicted_price, 2)}. Denna rad skickar ett Python-dictionary tillbaka till FastAPI.

5. FastAPI konverterar svaret och skickar tillbaka det som en JSON-svar.

6. Streamlit tar emot svaret