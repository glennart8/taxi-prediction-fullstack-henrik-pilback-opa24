# Taxi prediction app

# Vad streamlit innehåller?
- Fält för att fylla i från och till destination, autoläsa in tidpunkt och dag
- Skapa en modell som tränar på data och testas, se resultat och justera efter behov
- Denna modell ska anropas via en metod när man söker resa
- Visa KPIs för avg_price för resor i spannet 10 min, 20 min, 30 min
- Visa när det behövs flest taxibilar ute
- Visa när "vi" tjänar mest på att köra
- Visa barchart på när på dygnet resor sker
- Restid per tid på dygnet: Använd ett stapeldiagram för att visa den genomsnittliga Trip_Duration_Minutes för varje Time_of_Day. Detta kan avslöja vilka tider som har mest trafik.


# Frontend - FastAPI - Backend
1. Från Streamlit till FastAPI: HTTP-förfrågan
Gör requests genom att anropa get_api_endpoint och post_api_endpoint i helpers.py

2. Helpers.py skapar ett HTTP-anrop
Den konverterar min Python-data (input_data) till en textsträng i JSON-format.

3. FastAPI tar emot anropet
FastAPI, som kör på min server, lyssnar på inkommande anrop
Den kollar i koden och ser att jag har definierat just en sådan endpoint: @app.post("/predict_price/").
FastAPI vet då att det är JUST DEN funktionen (predict_price) som ska köras.
Det är INTE funktionsnamnet som kopplar ihop dem, utan webbadressen.

4. Metoderna körs och returnerar data
t.ex: return {"predicted_price": round(predicted_price, 2)}. Denna rad skickar ett Python-dictionary tillbaka till FastAPI.

5. FastAPI konverterar svaret och skickar tillbaka det som en JSON-svar.

6. Streamlit tar emot svaret - nu kan det användas/visas

# Problem på vägen

### Varför minusvärden med LR?
Något med intercept? Den kan ju aldrig vara noll eftersom basefare finns på alla resor, ska jag lägga in den separat på något vis för att starta på ett värde?
Skippade LR och körde på RF.