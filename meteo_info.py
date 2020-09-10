import requests
import json
import random

# Per la simulazione si è deciso di restituire
# semplicemente un valore casuale della nuvolosità

current_weather = {}

def get_meteo_api_call(lat, lon):
    global current_weather
    response = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude={}&units={}&lang={}&appid={}"
    .format(lat, lon, 'daily,hourly,minutely', 'metric', 'it', '8709871b2ef6c5f0eb80312295ba530c')).json()

    current_weather["cloudiness"] = response["current"]["clouds"]
    current_weather["weather"] = response["current"]["weather"]["main"]
    current_weather["description"] = response["current"]["weather"]["description"]
    return current_weather


def get_meteo_internal():
    """
    La nuvolosità può assumere valori da 0 a 100, per
    evitare di ridurre troppo la produzione dei pannelli
    solari limitiamo questo valore ad un massimo di 30
    (Se la nuvolosità è 100, il pannello produce 0W).
    """
    return random.randint(0, 30)


if __name__ == '__main__':
    get_meteo_api_call(40.12, -96.66) # Per vedere un esempio di risultato fornito dall'API