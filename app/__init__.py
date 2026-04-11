import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
bcrypt = Bcrypt()

# JWT token blacklist (in-memory for dev; use Redis in production)
jwt_blacklist = set()


def create_app(config=None):
    app = Flask(__name__)

    # Load config
    if config is None:
        from config import get_config
        app.config.from_object(get_config())
    else:
        app.config.from_object(config)

    # Ensure upload folder exits
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","))

    # Import models so Alembic can detect them
    with app.app_context():
        from app.models import User, Role, Category, Product, Cart, order, OrderItem

    return app
