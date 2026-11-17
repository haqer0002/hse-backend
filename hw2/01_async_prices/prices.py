import asyncio

# "База" магазинов: цена и время ответа API в секундах. НЕ менять
PRICES: dict[str, int] = {"ozon": 990, "wb": 950, "yandex": 1100, "slow_shop": 900}
DELAYS: dict[str, float] = {"ozon": 0.3, "wb": 0.2, "yandex": 0.4, "slow_shop": 5.0}


async def fetch_price(shop: str) -> int:
    """Имитирует запрос к API магазина. НЕ менять.

    Неизвестный магазин отвечает за 0.1 с и возвращает цену 1000.
    """
    await asyncio.sleep(DELAYS.get(shop, 0.1))
    return PRICES.get(shop, 1000)


async def get_prices_sequential(shops: list[str]) -> list[int]:
    prices = []
    for shop in shops:
        prices.append(await fetch_price(shop))
    return prices


async def get_prices_concurrent(shops: list[str]) -> list[int]:
    return await asyncio.gather(*(fetch_price(shop) for shop in shops))


async def get_price_or_none(shop: str, timeout: float = 1.0) -> int | None:
    try:
        return await asyncio.wait_for(fetch_price(shop), timeout=timeout)
    except TimeoutError:
        return None


async def get_prices_with_timeout(shops: list[str], timeout: float = 1.0) -> list[int | None]:
    return await asyncio.gather(*(get_price_or_none(shop, timeout) for shop in shops))


async def get_prices_limited(shops: list[str], limit: int = 3) -> list[int]:
    if limit < 1:
        raise ValueError("limit должен быть >= 1")
    semaphore = asyncio.Semaphore(limit)

    async def fetch_limited(shop: str) -> int:
        async with semaphore:
            return await fetch_price(shop)

    return await asyncio.gather(*(fetch_limited(shop) for shop in shops))


if __name__ == "__main__":
    import time

    async def main() -> None:
        shops = ["ozon", "wb", "yandex"]
        for fn in (get_prices_sequential, get_prices_concurrent):
            start = time.perf_counter()
            result = await fn(shops)
            print(f"{fn.__name__:25} {time.perf_counter() - start:.2f}s  {result}")

        start = time.perf_counter()
        result_with_timeout = await get_prices_with_timeout(shops + ["slow_shop"])
        print(f"{'get_prices_with_timeout':25} {time.perf_counter() - start:.2f}s  {result_with_timeout}")

    asyncio.run(main())
