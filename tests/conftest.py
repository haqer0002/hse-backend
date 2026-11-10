import pytest
from fastapi.testclient import TestClient

from main import app
from repositories.predictions import PredictionRepository
from routers.users import get_prediction_service
from services.prediction import PredictionService


@pytest.fixture
def advertisement():
    return {
        "seller_id": 1,
        "is_verified_seller": False,
        "item_id": 10,
        "name": "Велосипед",
        "description": "Городской велосипед",
        "category": 2,
        "images_qty": 0,
    }


@pytest.fixture
def repository():
    return PredictionRepository()


@pytest.fixture
def service(repository):
    return PredictionService(repository)


@pytest.fixture
def client(service):
    app.dependency_overrides[get_prediction_service] = lambda: service
    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
