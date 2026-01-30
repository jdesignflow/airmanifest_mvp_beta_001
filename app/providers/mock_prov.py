import json
import os
import random
from flask import current_app
from .base import FlightProvider

class MockProvider(FlightProvider):
    def search_flights(self, origin, destination, date):
        # Simulate network delay slightly
        
        # Load mock data
        path = os.path.join(current_app.root_path, 'static', 'data', 'mock_flights.json')
        try:
            with open(path) as f:
                data = json.load(f)
                
            # Filter somewhat realistically or return random subset
            results = []
            for item in data:
                # Fluctuate price to test Observer Pattern
                variation = random.randint(-50, 50)
                item['price'] = max(100, item['base_price'] + variation)
                results.append(item)
                
            return results
        except Exception as e:
            print(f"Mock Provider Error: {e}")
            return []