import pytest

# GET endpoint tests


@pytest.mark.parametrize("yarn, store", [("", ""), (1, ""), ("", 2), (1, 2)])
def test_get_links_with_queries(client, yarn, store):
    def build_url():
        queries = []
        if yarn:
            queries.append(f"yarn={yarn}")
        if store:
            queries.append(f"store={store}")
        return f"?{'&'.join(queries)}"

    response = client.get(f"/link/{build_url()}")
    assert response.status_code == 200

    data = response.json
    assert len(data) > 0
    if yarn:
        for item in data:
            assert item["yarn_id"] == yarn
    if store:
        for item in data:
            assert item["store_id"] == store


def test_get_all_yarn(client):
    response = client.get(f"/link/")
    assert response.status_code == 200

    data = response.json
    assert len(data) == 3


@pytest.mark.parametrize("id", [(1)])
def test_get_link_by_id_valid_input(client, id):
    response = client.get(f"/link/{id}")
    assert response.status_code == 200

    data = response.json
    assert data["id"] == id


@pytest.mark.parametrize("id", [(10000), ("aaaa")])
def test_get_link_by_id_invalid_input(client, id):
    response = client.get(f"/link/{id}")
    assert response.status_code == 200

    data = response.json
    assert data == {}


# POST endpoint tests


@pytest.mark.parametrize(
    "input_data",
    [
        (
            {
                "yarn_id": 1,
                "url": "https://www.michaels.com/awegjnrakgr",
                "store": "Michaels",
            }
        )
    ],
)
def test_add_link_valid_input(client, input_data):
    response = client.post("link/", json=input_data)
    print(response.json)
    assert response.status_code == 200
    data = response.json
    assert "id" in data
    assert "store_id" in data


@pytest.mark.parametrize(
    "input_data",
    [
        (
            {
                "yarn_id": 10000,
                "url": "https://www.michaels.com/awegjnrakgr",
                "store": "Michaels",
            }
        ),
        (
            {
                "url": "https://www.michaels.com/awegjnrakgr",
                "store": "Michaels",
            }
        ),
        (
            {
                "yarn_id": 1,
                "url": "",
                "store": "Michaels",
            }
        ),
    ],
)
def test_add_link_invalid_input(client, input_data):
    response = client.post("link/", json=input_data)
    assert response.status_code == 400
    data = response.json
    assert "error" in data
