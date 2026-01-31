import json
import os
import random
from flask import current_app
from app.providers.base import FlightProvider
from app.currency import to_cad

class MockProvider(FlightProvider):
    def search_flights(self, origin, destination, date):
        # Load mock data
        path = os.path.join(current_app.root_path, 'static', 'data', 'mock_flights.json')
        try:
            with open(path) as f:
                data = json.load(f)
                
            results = []
            for item in data:
                # 1. Simulate Price Fluctuation (USD)
                variation = random.randint(-20, 20)
                base_usd = item['base_price'] + variation
                
                # 2. Convert to CAD using the Live Rate
                # This ensures the currency converter is tested even in Mock Mode
                price_cad = to_cad(base_usd)
                
                # Create a copy of the item to avoid modifying the original JSON cache
                flight = item.copy()
                flight['price'] = price_cad
                
                results.append(flight)
                
            return results
        except Exception as e:
            print(f"Mock Provider Error: {e}")
            return []