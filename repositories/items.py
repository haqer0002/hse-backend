from asyncpg import Connection

from schemas.prediction import PredictRequest


class ItemRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def create(
        self,
        seller_id: int,
        name: str,
        description: str,
        category: int,
        images_qty: int,
    ) -> int:
        return await self._connection.fetchval(
            """
            INSERT INTO items (seller_id, name, description, category, images_qty)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """,
            seller_id,
            name,
            description,
            category,
            images_qty,
        )

    async def get_for_prediction(self, item_id: int) -> PredictRequest | None:
        row = await self._connection.fetchrow(
            """
            SELECT items.seller_id, users.is_verified AS is_verified_seller,
                   items.id AS item_id, items.name, items.description,
                   items.category, items.images_qty
            FROM items
            JOIN users ON users.id = items.seller_id
            WHERE items.id = $1
            """,
            item_id,
        )
        if row is None:
            return None
        return PredictRequest(**dict(row))
