class PredictionRepository:
    def __init__(self) -> None:
        self._predictions: dict[int, bool] = {}

    def save(self, item_id: int, has_violations: bool) -> None:
        self._predictions[item_id] = has_violations
