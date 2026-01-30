import os
import requests
from .base import FlightProvider

class SerpApiProvider(FlightProvider):
    def __init__(self):
        self.api_key = os.environ.get('SERPAPI_KEY')
        self.currency_key = os.environ.get('CURRENCY_API_KEY')

    def _convert_usd_to_cad(self, usd_amount):
        # Robust conversion with fallback
        try:
            url = f"https://api.currencyapi.com/v3/latest?apikey={self.currency_key}&base_currency=USD&currencies=CAD"
            response = requests.get(url, timeout=5)
            data = response.json()
            rate = data['data']['CAD']['value']
            return round(usd_amount * rate, 2)
        except:
            return round(usd_amount * 1.35, 2) # Fallback rate

    def search_flights(self, origin, destination, date):
        params = {
            "engine": "google_flights",
            "q": f"Flights from {origin} to {destination} on {date}",
            "api_key": self.api_key,
            "hl": "en",
            "gl": "ca",
            "currency": "USD" 
        }

        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            data = response.json()
            
            flights = []
            if 'flights' in data.get('other_flights', {}): # SerpApi structure varies
                # Parsing logic simplified for brevity
                pass 
            
            # Use 'best_flights' if available as it's cleaner
            results = data.get('best_flights', [])
            
            for f in results:
                price_usd = f.get('price', 0)
                flights.append({
                    'airline': f['flights'][0]['airline'],
                    'price': self._convert_usd_to_cad(price_usd),
                    'duration': f['total_duration'],
                    'provider': 'Google Flights', 
                    'link': 'https://google.com/flights' # Placeholder for deep link
                })
            return flights
        except Exception as e:
            print(f"SerpApi Error: {e}")
            return []