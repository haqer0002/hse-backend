## Установка и запуск

Нужен Python 3.10 или новее. В корне репозитория:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev
```

После запуска сервис доступен на [localhost:8000](http://127.0.0.1:8000),
документация Swagger – на [/docs](http://127.0.0.1:8000/docs).

`GET /` возвращает `{"message": "Hello World"}`.

## POST /predict

В теле запроса нужно передать JSON:

| Поле | Тип |
| --- | --- |
| `seller_id` | `int` |
| `is_verified_seller` | `bool` |
| `item_id` | `int` |
| `name` | `str` |
| `description` | `str` |
| `category` | `int` |
| `images_qty` | `int` |

Все поля обязательны. Типы проверяются строго: строки `"1"` и `"true"`
вместо числа и булева значения не принимаются.

Ответ – одно булево значение: `true`, если есть нарушение, и `false`,
если нарушений нет.

| Продавец подтверждён | Есть изображения | Ответ |
| --- | --- | --- |
| Да | Нет | `false` |
| Да | Да | `false` |
| Нет | Нет | `true` |
| Нет | Да | `false` |

Пример запроса:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "seller_id": 1,
    "is_verified_seller": false,
    "item_id": 10,
    "name": "Велосипед",
    "description": "Городской велосипед",
    "category": 2,
    "images_qty": 0
  }'
```

Ответ: `true`, статус `200`.

Статусы:

- `200` – запрос обработан, в ответе результат проверки;
- `400` – некорректный JSON, неверный тип или пропущенное обязательное поле;
- `500` – внутренняя ошибка сервиса или репозитория.

В ответе с ошибкой есть поле `detail` с её описанием.
Для `500` возвращается `{"detail": "Internal Server Error"}`.

## Структура

- `main.py` – приложение, корневой маршрут и обработка ошибок.
- `routers/users.py` – обработчик `/predict`.
- `schemas/prediction.py` – поля запроса и проверка типов.
- `services/prediction.py` – правило модерации.
- `repositories/predictions.py` – хранение последнего результата по `item_id`
  в памяти. После перезапуска результаты теряются.
- `tests/` – тесты API и сервиса.

## Тесты

В том же виртуальном окружении:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

В тестах есть все четыре случая из таблицы, пропущенные поля, неверные типы,
некорректные запросы и ошибки сервиса и репозитория.
