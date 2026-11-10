from repositories.predictions import PredictionRepository
from schemas.prediction import PredictRequest


class PredictionService:
    def __init__(self, repository: PredictionRepository) -> None:
        self._repository = repository

    def predict(self, advertisement: PredictRequest) -> bool:
        has_violations = not (
            advertisement.is_verified_seller or advertisement.images_qty > 0
        )
        self._repository.save(advertisement.item_id, has_violations)
        return has_violations
