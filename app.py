import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from pydantic import ValidationError
from werkzeug.wrappers import Response

from exceptions import AssetError, AssetNotFoundError, DuplicateAssetError
from models import db
from repository import AssetRepository
from routes import assets_blueprint


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///assets.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(assets_blueprint)

    @app.errorhandler(AssetError)
    def handle_asset_error(error: AssetError) -> tuple[Response, int]:
        if isinstance(error, AssetNotFoundError):
            return jsonify({"error": str(error)}), 404
        if isinstance(error, DuplicateAssetError):
            return jsonify({"error": str(error)}), 409
        return jsonify({"error": "Asset operation failed"}), 500

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError) -> tuple[Response, int]:
        return jsonify(
            {
                "error": "Invalid request",
                "details": error.errors(include_context=False),
            }
        ), 400

    @app.errorhandler(500)
    def handle_server_error(error: Exception) -> tuple[Response, int]:
        return jsonify({"error": "Internal server error"}), 500

    with app.app_context():
        AssetRepository().create_tables()

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
