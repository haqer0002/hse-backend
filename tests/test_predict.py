from unittest.mock import Mock

import pytest


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_predict_openapi_contract(client, advertisement):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    operation = schema["paths"]["/predict"]["post"]
    assert set(operation["responses"]) == {"200", "400", "500"}
    response_schema = operation["responses"]["200"]["content"]["application/json"]
    assert response_schema["schema"]["type"] == "boolean"
    request_schema = schema["components"]["schemas"]["PredictRequest"]
    assert set(request_schema["required"]) == set(advertisement)


@pytest.mark.parametrize(
    ("is_verified_seller", "images_qty", "has_violations"),
    [
        (True, 0, False),
        (True, 1, False),
        (False, 0, True),
        (False, 1, False),
    ],
)
def test_predict(client, advertisement, is_verified_seller, images_qty, has_violations):
    advertisement.update(is_verified_seller=is_verified_seller, images_qty=images_qty)

    response = client.post("/predict", json=advertisement)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() is has_violations


@pytest.mark.parametrize(
    "field",
    [
        "seller_id",
        "is_verified_seller",
        "item_id",
        "name",
        "description",
        "category",
        "images_qty",
    ],
)
def test_missing_required_field(client, advertisement, field):
    del advertisement[field]

    response = client.post("/predict", json=advertisement)

    assert response.status_code == 400
    assert any(
        error["loc"] == ["body", field] and error["type"] == "missing"
        for error in response.json()["detail"]
    )


@pytest.mark.parametrize("field", ["seller_id", "item_id", "category", "images_qty"])
@pytest.mark.parametrize("value", ["1", 1.5, True, None])
def test_invalid_integer_type(client, advertisement, field, value):
    advertisement[field] = value

    response = client.post("/predict", json=advertisement)

    assert response.status_code == 400
    assert response.json()["detail"][0]["loc"] == ["body", field]


@pytest.mark.parametrize("value", ["true", 1, None])
def test_invalid_boolean_type(client, advertisement, value):
    advertisement["is_verified_seller"] = value

    response = client.post("/predict", json=advertisement)

    assert response.status_code == 400
    assert response.json()["detail"][0]["loc"] == ["body", "is_verified_seller"]


@pytest.mark.parametrize("field", ["name", "description"])
@pytest.mark.parametrize("value", [123, False, None])
def test_invalid_string_type(client, advertisement, field, value):
    advertisement[field] = value

    response = client.post("/predict", json=advertisement)

    assert response.status_code == 400
    assert response.json()["detail"][0]["loc"] == ["body", field]


def test_missing_body(client):
    response = client.post("/predict")

    assert response.status_code == 400


@pytest.mark.parametrize(
    "body", ["{", "[]", '"text"', "1e10000", '{"seller_id":1e10000}']
)
def test_invalid_body(client, body):
    response = client.post(
        "/predict", content=body, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert "detail" in response.json()


@pytest.mark.parametrize("error_type", [RuntimeError, ValueError])
def test_business_logic_error(client, advertisement, service, monkeypatch, error_type):
    monkeypatch.setattr(
        service, "predict", Mock(side_effect=error_type("Business logic failed"))
    )

    response = client.post("/predict", json=advertisement)

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}


def test_repository_error(client, advertisement, repository, monkeypatch):
    monkeypatch.setattr(
        repository, "save", Mock(side_effect=RuntimeError("Repository failed"))
    )

    response = client.post("/predict", json=advertisement)

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
