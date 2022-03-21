from flask import jsonify
import pytest

# GET endpoint tests


def test_get_users_no_query(client):
    response = client.get("auth/")
    assert response.status_code == 200

    data = response.json
    assert len(data) == 3


@pytest.mark.parametrize(
    "username, role", [("Admin", ""), ("Admin", "admin"), ("", "admin")]
)
def test_get_users_with_queries(client, username, role):
    def build_url():
        queries = []
        if username:
            queries.append(f"username={username}")
        if role:
            queries.append(f"role={role}")
        return f"?{'&'.join(queries)}"

    response = client.get(f"/auth/{build_url()}")
    assert response.status_code == 200

    data = response.json
    assert len(data) > 0
    if username:
        assert data[0]["username"] == username
