import os
from collections.abc import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"


from app import app as flask_app
from models import db
from repository import AssetRepository


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    flask_app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def repository(app: Flask) -> AssetRepository:
    return AssetRepository()
