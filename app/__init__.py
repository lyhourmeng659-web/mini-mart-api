import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from app.utils.response import error_response

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

    # JWT blacklist checker
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in jwt_blacklist

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return error_response("Token has been revoked", 401)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return error_response("Authorization token is missing", 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return error_response("Token is invalid", 401)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response("Token has expired", 401)

    # Register blueprints
    from app.controllers.admin.auth_controller import admin_auth_bp
    from app.controllers.front.auth_controller import front_auth_bp
    from app.controllers.admin.user_controller import admin_user_bp
    from app.controllers.admin.category_controller import admin_category_bp
    from app.controllers.front.category_controller import front_category_bp
    from app.controllers.front.product_controller import front_product_bp
    from app.controllers.admin.product_controller import admin_product_bp
    from app.controllers.front.cart_controller import front_cart_bp
    from app.controllers.front.order_controller import front_order_bp
    from app.controllers.admin.order_controller import admin_order_bp
    from app.controllers.admin.report_controller import admin_report_bp

    app.register_blueprint(admin_auth_bp, url_prefix="/api/admin/auth")
    app.register_blueprint(front_auth_bp, url_prefix="/api/front/auth")
    app.register_blueprint(admin_user_bp, url_prefix="/api/admin/users")
    app.register_blueprint(admin_category_bp, url_prefix="/api/admin/categories")
    app.register_blueprint(front_category_bp, url_prefix="/api/front/categories")
    app.register_blueprint(front_product_bp, url_prefix="/api/front/products")
    app.register_blueprint(admin_product_bp, url_prefix="/api/admin/products")
    app.register_blueprint(front_cart_bp, url_prefix="/api/front/cart")
    app.register_blueprint(front_order_bp, url_prefix="/api/front/orders")
    app.register_blueprint(admin_order_bp, url_prefix="/api/admin/orders")
    app.register_blueprint(admin_report_bp, url_prefix="/api/admin/reports")

    # Health check
    @app.route("/api/health")
    def health():
        from app.utils.response import success_response
        return success_response({
            "status": "ok",
        }, "Service is running")

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return error_response("Resource not found", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("Method not allowed", 405)

    @app.errorhandler(500)
    def internal_server_error(e):
        return error_response("Internal server error", 500)

    from flask import send_from_directory
    @app.route("/api/uploads/<path:filename>")
    def serve_upload(filename):
        upload_folder = os.path.join(app.root_path, '..', app.config["UPLOAD_FOLDER"])
        upload_folder = os.path.abspath(upload_folder)
        return send_from_directory(upload_folder, filename)

    @app.route("/api/debug/paths")
    def debug_paths():
        upload_folder = app.config["UPLOAD_FOLDER"]
        abs_path = os.path.abspath(upload_folder)
        files = os.listdir(abs_path) if os.path.exists(abs_path) else []
        return {
            "root_path": app.root_path,
            "upload_folder_config": upload_folder,
            "absolute_path": abs_path,
            "folder_exists": os.path.exists(abs_path),
            "files_in_folder": files
        }

    return app
