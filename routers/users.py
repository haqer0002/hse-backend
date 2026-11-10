from typing import Annotated

from fastapi import APIRouter, Depends, status

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
    response_description="true — есть нарушение, false — нарушений нет",
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
