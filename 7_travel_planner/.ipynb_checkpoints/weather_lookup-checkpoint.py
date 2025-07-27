import requests
import os

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")  # Set this in your .env or shell

def get_weather(location: str) -> str:
    """Fetch real weather data using OpenWeatherMap API"""
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"⚠️ Failed to get weather data for {location}. Error: {response.text}"

    data = response.json()
    temp = data["main"]["temp"]
    weather = data["weather"][0]["description"]
    return f"The current temperature in {location} is {temp}°C with {weather}."
