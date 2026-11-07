from flask import Flask
from .extensions import db, migrate
from .config import DefaultConfig
from .errors import register_error_handlers
from .api.products import products_bp

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or DefaultConfig)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(products_bp)
    register_error_handlers(app)
    return app