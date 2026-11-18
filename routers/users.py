from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from repositories.predictions import PredictionRepository
from schemas.prediction import PredictRequest
from services.prediction import PredictionService

router = APIRouter()
repository = PredictionRepository()


def get_prediction_service() -> PredictionService:
    return PredictionService(repository)


@router.post(
    "/predict",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Проверить объявление на нарушения",
    response_description="true – есть нарушение, false – нарушений нет",
    responses={
        400: {"description": "Некорректные входные данные"},
        500: {"description": "Внутренняя ошибка сервиса"},
    },
)
def predict(
    advertisement: PredictRequest,
    service: Annotated[PredictionService, Depends(get_prediction_service)],
) -> bool:
    return service.predict(advertisement)


@router.get(
    "/simple_predict",
    response_model=bool,
    summary="Проверить объявление по ID",
    response_description="true – есть нарушение, false – нарушений нет",
    responses={
        400: {"description": "Неверный идентификатор объявления"},
        404: {"description": "Объявление не найдено"},
        500: {"description": "Внутренняя ошибка сервиса"},
    },
)
async def simple_predict(
    item_id: Annotated[int, Query(gt=0, le=2_147_483_647)],
    service: Annotated[PredictionService, Depends(get_prediction_service)],
) -> bool:
    has_violations = await service.predict_item(item_id)
    if has_violations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return has_violations
