import pytest

from yarn_killer.models import Yarn
from yarn_killer.forms import YarnForm, FiberForm


def test_browse(client):
    rv = client.get('yarn/browse')
    assert rv.status_code == 200
    # TODO change this to be something specific to the browse page, not part of the header
    assert b'Yarn Killer' in rv.data

@pytest.mark.parametrize('id', [
    1, 2, 3
])
def test_view_yarn(client, id):
    rv = client.get(f'yarn/{id}')
    assert rv.status_code == 200


@pytest.mark.parametrize('fiber_dict', [
    {'Acrylic': 100},
    {'Wool': 100},
    {'Wool': 50, 'Acrylic': 50},
    {'Acrylic': 75, 'Cotton': 30}
])
def test_populate_fibers(client, app, fiber_dict):
    with app.app_context():
        from yarn_killer.yarn import populate_fibers
        form = YarnForm()
        for k, v in fiber_dict.items():
            form.fiber_type_list.entries.append(FiberForm(fiber_type=k, fiber_qty=v))
        yarns = (
            Yarn.query.filter_by(brand='Caron', name='Simply Soft').first(),
            Yarn.query.filter_by(brand='Lion Brand', name="Vanna's Choice").first()
        )
        for yarn in yarns:
            populate_fibers(yarn, form)
            total_fiber_count = 0
            for fiber in yarn.fibers:
                total_fiber_count += fiber.amount
            assert total_fiber_count <= 100
            # assert sum(x.fibers.amount for x.fibers.amount in x.fibers) <= 100