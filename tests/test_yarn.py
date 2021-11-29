import pytest

from yarn_killer.models import Yarn, Link, Colorway, Fiber
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
    

@pytest.mark.parametrize('yarn_id,new_name', [
    (1, 'Simply Soft Solids'),
])
def test_edit_yarn(client, yarn_id, new_name): # TODO add fiber editing
    assert client.get(f'yarn/{yarn_id}/edit').status_code == 200
    assert client.get(f'yarn/new/edit').status_code == 200

    data = {
        'brand_name': 'Caron', 
        'yarn_name': new_name, 
        'weight_name': 'Thread', 
        'gauge': 18, 
        'yardage': 200, 
        'weight_grams': 200, 
        'texture': 'Single-ply', 
        'color_style': 'Solid'
    }
    client.post(f'yarn/{yarn_id}/edit', data=data)
    yarn = Yarn.query.get(yarn_id)
    assert yarn.name == new_name
    assert yarn.texture == 'Single-ply'


def test_edit_yarn_validation(client):
    pass


@pytest.mark.parametrize('yarn_id,url,store_name', [
    (1, 'https://www.michaels.com/caron-simply-soft-solid-yarn/M10109896.html', 'Michaels'),
    (1, 'https://www.lovecrafts.com/en-us/p/caron-simply-soft', 'LoveCrafts'),
    (1, 'https://www.yarnspirations.com/caron-simply-soft-yarn/H97003.html', 'Yarnspirations')
])
def test_add_link(client, yarn_id, url, store_name):
    data = {'url': url }
    client.post(f'yarn/{yarn_id}/add_link', data=data)

    link = Link.query.filter_by(url=url).first()
    assert link is not None
    assert link.yarn_id == yarn_id
    assert link.store.name == store_name
    assert link.current_price is not None
    
