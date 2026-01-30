import os
from flask import Flask
from . import db, auth, main, traveler, admin
from .config import config

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from config.py based on environment
    env_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[env_name])

    # Override with test config if passed (used during automated tests)
    if test_config:
        app.config.from_mapping(test_config)

    # Initialize Database
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(traveler.bp)
    app.register_blueprint(admin.bp)

    return app