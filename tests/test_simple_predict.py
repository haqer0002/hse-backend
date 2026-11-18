import pytest
from httpx import ASGITransport, AsyncClient

from database import connect_db
from main import app
from repositories.items import ItemRepository
from repositories.users import UserRepository

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def db():
    async with connect_db() as connection:
        yield connection


@pytest.fixture
async def saved_advertisement(db, request):
    is_verified, images_qty = getattr(request, "param", (False, 0))
    seller_id = await UserRepository(db).create(
        first_name="Иван",
        last_name="Петров",
        is_verified=is_verified,
        violations_qty=2,
    )
    try:
        item_id = await ItemRepository(db).create(
            seller_id=seller_id,
            name="Велосипед",
            description="Городской велосипед",
            category=2,
            images_qty=images_qty,
        )
        try:
            yield seller_id, item_id
        finally:
            await db.execute("DELETE FROM items WHERE id = $1", item_id)
    finally:
        await db.execute("DELETE FROM users WHERE id = $1", seller_id)


@pytest.fixture
async def missing_item_id(db, saved_advertisement):
    _, item_id = saved_advertisement
    await db.execute("DELETE FROM items WHERE id = $1", item_id)
    return item_id


@pytest.fixture
async def api_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest.mark.parametrize(
    ("saved_advertisement", "has_violations"),
    [
        ((False, 0), True),
        ((False, 1), False),
        ((True, 0), False),
        ((True, 1), False),
    ],
    indirect=["saved_advertisement"],
)
async def test_simple_predict(api_client, saved_advertisement, has_violations):
    _, item_id = saved_advertisement

    response = await api_client.get("/simple_predict", params={"item_id": item_id})

    assert response.status_code == 200
    assert response.json() is has_violations


async def test_repositories_create_records(db, saved_advertisement):
    seller_id, item_id = saved_advertisement

    seller = await db.fetchrow(
        "SELECT first_name, last_name, is_verified, violations_qty FROM users WHERE id = $1",
        seller_id,
    )
    item = await db.fetchrow(
        "SELECT seller_id, name, description, category, images_qty FROM items WHERE id = $1",
        item_id,
    )

    assert seller is not None
    assert dict(seller) == {
        "first_name": "Иван",
        "last_name": "Петров",
        "is_verified": False,
        "violations_qty": 2,
    }
    assert item is not None
    assert dict(item) == {
        "seller_id": seller_id,
        "name": "Велосипед",
        "description": "Городской велосипед",
        "category": 2,
        "images_qty": 0,
    }


async def test_simple_predict_item_not_found(api_client, missing_item_id):
    response = await api_client.get(
        "/simple_predict", params={"item_id": missing_item_id}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"item_id": ""},
        {"item_id": "bike"},
        {"item_id": "1.5"},
        {"item_id": 0},
        {"item_id": -1},
        {"item_id": 2_147_483_648},
    ],
)
async def test_simple_predict_invalid_item_id(api_client, params):
    response = await api_client.get("/simple_predict", params=params)

    assert response.status_code == 400
    assert response.json()["detail"][0]["loc"] == ["query", "item_id"]


async def test_simple_predict_openapi(api_client):
    response = await api_client.get("/openapi.json")

    assert response.status_code == 200
    operation = response.json()["paths"]["/simple_predict"]["get"]
    parameter, = operation["parameters"]
    assert parameter["name"] == "item_id"
    assert parameter["in"] == "query"
    assert parameter["required"] is True
    assert "requestBody" not in operation
    assert set(operation["responses"]) == {"200", "400", "404", "500"}
