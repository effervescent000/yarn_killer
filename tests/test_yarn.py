import pytest


# GET endpoint tests


@pytest.mark.parametrize("id,brand,fibers_num", [(1, "Caron", 1), (4, "Lion Brand", 0)])
def test_get_yarn_by_id_valid_input(client, id, brand, fibers_num):
    response = client.get(f"yarn/{id}")
    assert response.status_code == 200

    data = response.json
    assert data["brand"] == brand
    assert len(data["fibers"]) == fibers_num


@pytest.mark.parametrize("id", [(10000), ("aaaa")])
def test_get_yarn_by_id_invalid_input(client, id):
    response = client.get(f"yarn/{id}")
    assert response.status_code == 200
    data = response.json
    assert data == {}


def test_get_yarn(client):
    response = client.get("yarn/")
    assert response.status_code == 200
    data = response.json
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
def test_get_yarn_with_queries(client, brand, name, gauge, approx):
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

    response = client.get(f"/yarn/{build_url()}")
    assert response.status_code == 200
    data = response.json
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


# POST endpoint tests


@pytest.mark.parametrize(
    "input_data",
    [
        (
            {
                "brand": "Lily",
                "name": "Sugar'n Cream Solids & Denim",
                "weightName": "Worsted",
                "gauge": 20,
                "yardage": 120,
                "unitWeight": 71,
                "texture": "Plied (3+)",
                "colorStyle": "Solid",
                "discontinued": False,
                "fibers": [{"type": "Cotton", "amount": 100}],
            }
        ),
        (
            {
                "brand": "Lily",
                "name": "Sugar'n Cream Solids & Denim",
                "weightName": "Worsted",
                "gauge": 20,
                "unitWeight": 71,
                "texture": "Plied (3+)",
                "colorStyle": "Solid",
                "discontinued": False,
                "fibers": [{"type": "Cotton", "amount": 100}],
            }
        ),
        (
            {
                "brand": "Lily",
                "name": "Sugar'n Cream Solids & Denim",
                "weightName": "Worsted",
                "gauge": 20,
                "yardage": 120,
                "unitWeight": 71,
                "texture": "Plied (3+)",
                "discontinued": False,
                "fibers": [{"type": "Cotton", "amount": 100}],
            }
        ),
    ],
)
def test_add_yarn_valid(client, input_data):
    response = client.post("yarn/", json=input_data)
    assert response.status_code == 200

    data = response.json
    assert data["id"]
    assert data["brand"] == input_data["brand"]

    for x in input_data["fibers"]:
        fiber_match = False
        for y in data["fibers"]:
            if x["type"] == y["type"] and x["amount"] == y["amount"]:
                fiber_match = True
                break
        assert fiber_match


@pytest.mark.parametrize(
    "input_data",
    [
        (
            {
                "name": "Sugar'n Cream Solids & Denim",
                "weightName": "Worsted",
                "gauge": 20,
                "yardage": 120,
                "unitWeight": 71,
                "texture": "Plied (3+)",
                "colorStyle": "Solid",
                "discontinued": False,
                "fibers": [{"type": "Cotton", "amount": 100}],
            }
        ),
        (
            {
                "brand": "Lily",
                "weightName": "Worsted",
                "gauge": 20,
                "yardage": 120,
                "unitWeight": 71,
                "texture": "Plied (3+)",
                "colorStyle": "Solid",
                "discontinued": False,
                "fibers": [{"type": "Cotton", "amount": 100}],
            }
        ),
        (
            {
                "brand": "Lily",
                "name": "Sugar'n Cream Solids & Denim",
                "gauge": 20,
                "yardage": 120,
                "unitWeight": 71,
                "texture": "Plied (3+)",
                "colorStyle": "Solid",
                "discontinued": False,
                "fibers": [{"type": "Cotton", "amount": 100}],
            }
        ),
        (
            {
                "brand": "Lily",
                "name": "Sugar'n Cream Solids & Denim",
                "weightName": "Worsted",
                "yardage": 120,
                "unitWeight": 71,
                "texture": "Plied (3+)",
                "colorStyle": "Solid",
                "discontinued": False,
                "fibers": [{"type": "Cotton", "amount": 100}],
            }
        ),
    ],
)
def test_add_yarn_invalid(client, input_data):
    response = client.post("yarn/", json=input_data)
    assert response.status_code == 200
    assert "error" in response.json
