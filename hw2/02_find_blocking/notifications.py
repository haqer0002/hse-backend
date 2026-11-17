import asyncio
import time


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}")


async def render_template(user: str) -> str:
    await asyncio.sleep(0.01)
    return f"Привет, {user}! У нас новые скидки."


async def send_email(user: str) -> str:
    text = await render_template(user)
    log(f"отправляю письмо {user}")
    # При time.sleep цикл событий не мог переключиться на другие отправки
    await asyncio.sleep(0.5)
    log(f"письмо {user} доставлено")
    return f"{user}: {len(text)} символов"


async def notify_all(users: list[str]) -> list[str]:
    return await asyncio.gather(*(send_email(user) for user in users))


if __name__ == "__main__":
    start = time.perf_counter()
    results = asyncio.run(notify_all(["anna", "boris", "vera", "gleb"]))
    print(results)
    print(f"Всего: {time.perf_counter() - start:.2f}s (ожидаем ~0.5 с)")
