from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Migrate
from .config import Config

db = SQLAlchemy()
migrate = Migrate()  # Create Migrate instance

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Migrate with app and db

    with app.app_context():
        from .routes import booking_blueprint  # Import the Blueprint
        app.register_blueprint(booking_blueprint)  # Register the Blueprint
        db.create_all()  # Create database tables

    return app
