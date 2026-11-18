from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg

DATABASE_URL = "postgresql://postgres:postgres@localhost:5435/hw"


@asynccontextmanager
async def connect_db() -> AsyncIterator[asyncpg.Connection]:
    connection = await asyncpg.connect(DATABASE_URL)
    try:
        yield connection
    finally:
        await connection.close()
