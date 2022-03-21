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


@pytest.mark.parametrize("id,username", [(1, "Admin")])
def test_get_user_valid(client, id, username):
    response = client.get(f"/auth/{id}")
    assert response.status_code == 200

    data = response.json
    assert data["id"] == id
    assert data["username"] == username


def test_get_user_invalid(client):
    response = client.get("/auth/1000")
    assert response.status_code == 404


# POST endpoint tests


@pytest.mark.parametrize("username, password", [("testing", "password")])
def test_create_user_valid(client, username, password):
    response = client.post(
        "/auth/signup", json={"username": username, "password": password}
    )
    assert response.status_code == 201

    data = response.json
    assert "access_token" in data
    assert "user" in data

    user = data["user"]
    assert "id" in user
    assert user["username"] == username
    assert "password" not in user


@pytest.mark.parametrize(
    "username, password", [("Admin", "password"), ("", "password"), ("testing", "")]
)
def test_create_user_invalid(client, username, password):
    response = client.post(
        "/auth/signup", json={"username": username, "password": password}
    )
    assert response.status_code == 400

    data = response.json
    assert "user" not in data


@pytest.mark.parametrize(
    "username, password",
    [
        ("Admin", "test_password"),
    ],
)
def test_login_valid(client, username, password):
    response = client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200

    data = response.json
    assert "access_token" in data
    assert "user" in data

    user = data["user"]
    assert user["username"] == username


@pytest.mark.parametrize(
    "username, password",
    [
        ("Admin", "wrong_password"),
        ("wrong_admin", "test_password"),
        ("", "test_password"),
        ("Admin", ""),
    ],
)
def test_login_invalid(client, username, password):
    response = client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 400
