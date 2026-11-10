import pytest

from schemas.prediction import PredictRequest


@pytest.mark.parametrize(
    ("is_verified_seller", "images_qty", "has_violations"),
    [
        (True, 0, False),
        (True, 3, False),
        (False, 0, True),
        (False, 3, False),
    ],
)
def test_prediction_service(
    service, advertisement, is_verified_seller, images_qty, has_violations
):
    advertisement.update(is_verified_seller=is_verified_seller, images_qty=images_qty)
    request = PredictRequest(**advertisement)

    assert service.predict(request) is has_violations


def test_prediction_is_recalculated_for_same_item(service, advertisement):
    assert service.predict(PredictRequest(**advertisement)) is True

    advertisement["images_qty"] = 1

    assert service.predict(PredictRequest(**advertisement)) is False
