import pytest

from yarn_killer.models import Yarn


@pytest.mark.parametrize(
    "yarn_id, fiber_type, fiber_amount",
    [(3, "Acrylic", 10), (3, "Acrylic", 20), (3, "Wool", 10)],
)
def test_add_fibers_valid(client, yarn_id, fiber_type, fiber_amount):
    yarn = Yarn.query.get(yarn_id)
    response = yarn.add_fibers(fiber_type=fiber_type, fiber_amount=fiber_amount)
    assert response
    fiber_sum = 0
    for fiber in yarn.fibers:
        fiber_sum += fiber.amount
    assert fiber_amount <= fiber_sum <= 100


@pytest.mark.parametrize(
    "yarn_id, fiber_type, fiber_amount",
    [(4, "Acrylic", 110), (1, "Wool", 1), (3, "Wool", 30)],
)
def test_add_fibers_invalid(client, yarn_id, fiber_type, fiber_amount):
    yarn = Yarn.query.get(yarn_id)
    response = yarn.add_fibers(fiber_type=fiber_type, fiber_amount=fiber_amount)
    assert not response
