import os
import requests
from app.providers.base import FlightProvider
from app.currency import to_cad

class SerpApiProvider(FlightProvider):
    def __init__(self):
        self.api_key = os.environ.get('SERPAPI_KEY')

    def search_flights(self, origin, destination, date):
        params = {
            "engine": "google_flights",
            "q": f"Flights from {origin} to {destination} on {date}",
            "api_key": self.api_key,
            "hl": "en",
            "gl": "ca",
            "currency": "USD" # We fetch in USD, then convert locally
        }

        try:
            print(f"📡 Fetching Live Data from SerpApi for {origin} -> {destination}...")
            response = requests.get("https://serpapi.com/search", params=params, timeout=15)
            data = response.json()
            
            flights = []
            
            # SerpApi structure handling
            results = data.get('best_flights', [])
            if not results:
                 results = data.get('other_flights', [])
            
            for f in results:
                price_usd = f.get('price', 0)
                
                # Check if flight has detailed data
                airline = "Unknown Airline"
                if 'flights' in f and len(f['flights']) > 0:
                    airline = f['flights'][0].get('airline', "Unknown Airline")

                flights.append({
                    'airline': airline,
                    # CONVERSION HAPPENS HERE
                    'price': to_cad(price_usd),
                    'duration': f.get('total_duration', 0),
                    'provider': 'Google Flights', 
                    'link': 'https://google.com/flights'
                })
            return flights
        except Exception as e:
            print(f"SerpApi Error: {e}")
            return []