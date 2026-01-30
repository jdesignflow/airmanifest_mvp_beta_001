from app.db import get_db

class PriceSubject:
    def __init__(self, watch_id, user_id, threshold, origin, destination):
        self.watch_id = watch_id
        self.user_id = user_id
        self.threshold = float(threshold)
        self.origin = origin
        self.destination = destination
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, new_price, provider_name):
        # Trigger logic: Notify ONLY if price is below threshold
        if new_price <= self.threshold:
            for observer in self.observers:
                observer.update(self.user_id, self.watch_id, new_price, provider_name, self.origin, self.destination)

class NotificationObserver:
    def update(self, user_id, watch_id, price, provider, origin, dest):
        db = get_db()
        cursor = db.cursor()
        
        message = f"Deal Alert! Flight {origin} to {dest} is now ${price} on {provider}."
        
        # Insert notification
        cursor.execute(
            "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
            (user_id, message)
        )
        
        # Log snapshot
        cursor.execute(
            "INSERT INTO price_snapshots (watch_id, price, provider) VALUES (%s, %s, %s)",
            (watch_id, price, provider)
        )