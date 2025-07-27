# flight_search.py

def search_flights(departure_city: str, arrival_city: str, departure_date: str):
    # Dummy logic: returns example flights
    return {
        "flights": [
            {"flight": "XY123", "departure": departure_city, "arrival": arrival_city, "date": departure_date, "price": 320},
            {"flight": "XY456", "departure": departure_city, "arrival": arrival_city, "date": departure_date, "price": 285}
        ]
    }


# hotel_finder.py

def find_hotels(city: str, checkin_date: str, nights: int):
    # Dummy logic: returns example hotels
    return {
        "hotels": [
            {"name": "Hotel Luxe", "city": city, "price_per_night": 120, "rating": 4.5},
            {"name": "Budget Inn", "city": city, "price_per_night": 80, "rating": 3.8}
        ]
    }


# weather_lookup.py

def get_weather_forecast(city: str, date: str):
    # Dummy logic: returns example forecast
    return {
        "forecast": {
            "city": city,
            "date": date,
            "temperature_c": 23,
            "description": "Partly cloudy"
        }
    }


# budget_estimator.py

def estimate_budget(flight_price: float, hotel_price_per_night: float, nights: int):
    # Calculate total cost
    total = flight_price + hotel_price_per_night * nights
    return {
        "estimated_total_budget": total
    }
