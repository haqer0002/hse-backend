import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from routers.users import router as user_router

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": errors},
    )


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled application error", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


def custom_openapi() -> dict:
    if app.openapi_schema is None:
        app.openapi_schema = get_openapi(
            title=app.title, version=app.version, routes=app.routes
        )
        # Валидация возвращает 400 вместо 422.
        app.openapi_schema["paths"]["/predict"]["post"]["responses"].pop("422", None)
    return app.openapi_schema


app.openapi = custom_openapi
