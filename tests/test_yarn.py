import pytest

from yarn_killer.utils import decode_response


@pytest.mark.parametrize("id,brand,fibers_num", [(1, "Caron", 1), (4, "Lion Brand", 0)])
def test_get_yarn_by_id_valid_input(client, id, brand, fibers_num):
    # first test for a valid get call
    response = client.get(f"yarn/get/{id}")
    assert response.status_code == 200

    data = decode_response(response)
    assert data["brand"] == brand
    assert len(data["fibers"]) == fibers_num


@pytest.mark.parametrize("id", [(10000), ("aaaa")])
def test_get_yarn_by_id_invalid_input(client, id):
    response = client.get(f"yarn/get/{id}")
    assert response.status_code == 200
    data = decode_response(response)
    assert data == {}


def test_get_yarn_list(client):
    response = client.get("yarn/get_all")
    assert response.status_code == 200
    data = decode_response(response)
    assert len(data) == 4


@pytest.mark.parametrize(
    "brand,name,gauge, approx",
    [
        ("", "", "", ""),
        ("Caron", "", "", ""),
        ("caron", "", "", ""),
        ("", "vanna", "", ""),
        ("", "Vanna", "", ""),
        ("Lion", "Vanna", "", ""),
        ("", "", 19, "true"),
        ("", "", 19, "false"),
        ("", "", 19, ""),
    ],
)
def test_get_yarn_results(client, brand, name, gauge, approx):
    def build_url():
        queries = []
        if brand:
            queries.append(f"brand={brand}")
        if name:
            queries.append(f"name={name}")
        if gauge:
            queries.append(f"gauge={gauge}")
        if approx:
            queries.append(f"approx={approx}")
        return f"?{'&'.join(queries)}"

    response = client.get(f"/yarn/get{build_url()}")
    assert response.status_code == 200
    data = decode_response(response)
    assert len(data) > 0
    if brand:
        assert brand.lower() in data[0]["brand"].lower()
    if name:
        assert name.lower() in data[0]["name"].lower()
    if gauge:
        if approx:
            for yarn in data:
                assert gauge - 2 < yarn["gauge"] < gauge + 2
        else:
            for yarn in data:
                assert yarn["gauge"] == gauge
