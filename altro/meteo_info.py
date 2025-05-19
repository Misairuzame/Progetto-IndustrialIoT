import os
import random

import requests

# Per la simulazione si è deciso di restituire
# semplicemente un valore casuale della nuvolosità

# TODO: API OpenMeteo!

api_key = os.getenv("WEATHER_API_KEY", "")
current_weather = {}


def get_meteo_api_call(lat, lon):
    global current_weather
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude={}&units={}&lang={}&appid={}".format(
                lat,
                lon,
                "daily,hourly,minutely",
                "metric",
                "it",
                api_key,
            )
        ).json()
        print(response)

        current_weather["cloudiness"] = response["current"]["clouds"]
        current_weather["weather"] = response["current"]["weather"]["main"]
        current_weather["description"] = response["current"]["weather"]["description"]
        return current_weather
    except Exception as e:
        print(
            f"Could not get meteo info for ({lat},{lon}): {e}, returning random value"
        )
        return get_meteo_internal()


def get_meteo_internal():
    """
    La nuvolosità può assumere valori da 0 a 100, per
    evitare di ridurre troppo la produzione dei pannelli
    solari limitiamo questo valore ad un massimo di 30
    (Se la nuvolosità è 100, il pannello produce 0W).
    """
    return random.triangular(0, 30, 0)


if __name__ == "__main__":
    # Per vedere un esempio di risultato fornito dall'API
    get_meteo_api_call(44.8298, 11.5885)
