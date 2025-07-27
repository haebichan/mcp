# budget_estimator.py

def estimate_budget(flight_price: float, hotel_price_per_night: float, nights: int):
    # Calculate total cost
    total = flight_price + hotel_price_per_night * nights
    return {
        "estimated_total_budget": total
    }
