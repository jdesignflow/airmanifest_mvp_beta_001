import os
from flask import Flask
from . import db, auth, main, traveler, admin
from .config import config
from .currency import get_usd_to_cad_rate

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    env_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[env_name])

    if test_config:
        app.config.from_mapping(test_config)

    # Initialize Database
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(traveler.bp)
    app.register_blueprint(admin.bp)

    # --- NEW: Context Processor for Currency ---
    @app.context_processor
    def inject_currency_rate():
        # This makes 'current_rate' available in ALL HTML templates
        return dict(current_rate=get_usd_to_cad_rate())

    return app