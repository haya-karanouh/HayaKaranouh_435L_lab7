"""Lab 7 graded activity — Haya Karanouh.

Every test uses a fresh temporary SQLite database, never the Lab 5 database.
"""

import importlib
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

import database


EXPECTED_USERS = [
    {"user_id": 1, "name": "Haya Karanouh", "email": "haya@example.com",
     "phone": "70123456", "address": "Beirut", "country": "Lebanon"},
    {"user_id": 2, "name": "Ali Rahal", "email": "ali@example.com",
     "phone": "70234567", "address": "Sidon", "country": "Lebanon"},
    {"user_id": 3, "name": "Maya Nasser", "email": "maya@example.com",
     "phone": "70345678", "address": "Tripoli", "country": "Lebanon"},
]


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Create an isolated database with the original Lab 5 seed users."""
    path = tmp_path / "test_users.db"
    monkeypatch.setattr(database, "DB_PATH", str(path))
    assert database.create_db_table() is True
    return path


@pytest.fixture
def client(db_path, monkeypatch):
    # Import only after DB_PATH has been redirected: app initializes DB on import.
    app_module = importlib.import_module("app")
    monkeypatch.setitem(app_module.app.config, "TESTING", True)
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def new_user():
    return {"name": "Haya Karanouh Test", "email": "haya.test@example.com",
            "phone": "70987654", "address": "Beirut", "country": "Lebanon"}


def stored_users(path):
    """Read SQLite directly to independently verify persisted results."""
    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(
            "SELECT * FROM users ORDER BY user_id")]


# 1. First application run creates the database with the specified users.
def test_database_created_with_specified_users_on_first_app_run(tmp_path):
    project = Path(__file__).resolve().parent
    db_file = tmp_path / "database.db"
    assert not db_file.exists()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project)
    result = subprocess.run(
        [sys.executable, "-c", "import app"], cwd=tmp_path, env=env,
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert db_file.is_file()
    assert stored_users(db_file) == EXPECTED_USERS


def test_database_initialization_does_not_duplicate_users(db_path, new_user):
    added = database.insert_user(new_user)
    assert database.create_db_table() is True
    assert stored_users(db_path) == [*EXPECTED_USERS, added]


# 2. insert_user()
def test_insert_user(db_path, new_user):
    result = database.insert_user(new_user)
    assert result == {"user_id": 4, **new_user}
    assert stored_users(db_path) == [*EXPECTED_USERS, result]


def test_insert_user_rejects_missing_required_field(db_path, new_user):
    del new_user["email"]
    with pytest.raises(ValueError, match="email"):
        database.insert_user(new_user)
    assert stored_users(db_path) == EXPECTED_USERS


# 3. get_users()
def test_get_users(db_path):
    assert database.get_users() == EXPECTED_USERS


def test_get_users_when_empty(db_path):
    with sqlite3.connect(db_path) as connection:
        connection.execute("DELETE FROM users")
    assert database.get_users() == []


# 4. get_user_by_id() (the actual function name in Lab 5)
def test_get_user_by_id(db_path):
    assert database.get_user_by_id(1) == EXPECTED_USERS[0]


def test_get_user_by_id_when_missing(db_path):
    assert database.get_user_by_id(9999) is None


# 5. update_user()
def test_update_user(db_path, new_user):
    payload = {"user_id": 1, **new_user}
    assert database.update_user(payload) == payload
    assert stored_users(db_path) == [payload, *EXPECTED_USERS[1:]]


def test_update_user_when_missing(db_path, new_user):
    assert database.update_user({"user_id": 9999, **new_user}) is None
    assert stored_users(db_path) == EXPECTED_USERS


# 6. delete_user()
def test_delete_user(db_path):
    assert database.delete_user(1) == 1
    assert stored_users(db_path) == EXPECTED_USERS[1:]


def test_delete_user_when_missing(db_path):
    assert database.delete_user(9999) == 0
    assert stored_users(db_path) == EXPECTED_USERS


# 7. API GET: check both status and every downloaded field.
def test_api_get_user(client):
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == EXPECTED_USERS[0]


def test_api_get_users(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.get_json() == EXPECTED_USERS


def test_api_get_user_when_missing(client):
    response = client.get("/api/users/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}


# 8. API POST: check status, uploaded/returned fields, and persistence.
def test_api_add_user(client, db_path, new_user):
    response = client.post("/api/users/add", json=new_user)
    expected = {"user_id": 4, **new_user}
    assert response.status_code == 201
    assert response.get_json() == expected
    assert stored_users(db_path) == [*EXPECTED_USERS, expected]
    downloaded = client.get("/api/users/4")
    assert downloaded.status_code == 200
    assert downloaded.get_json() == expected


def test_api_add_user_rejects_missing_field(client, db_path, new_user):
    del new_user["email"]
    response = client.post("/api/users/add", json=new_user)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing required fields: email"}
    assert stored_users(db_path) == EXPECTED_USERS


def test_api_add_user_rejects_non_json(client, db_path):
    response = client.post("/api/users/add", data="not JSON", content_type="text/plain")
    assert response.status_code == 400
    assert response.get_json() == {"error": "JSON body is required"}
    assert stored_users(db_path) == EXPECTED_USERS


# 9. API PUT: check status, uploaded/returned fields, and persistence.
def test_api_update_user(client, db_path, new_user):
    payload = {"user_id": 1, **new_user}
    response = client.put("/api/users/update", json=payload)
    assert response.status_code == 200
    assert response.get_json() == payload
    assert stored_users(db_path) == [payload, *EXPECTED_USERS[1:]]
    downloaded = client.get("/api/users/1")
    assert downloaded.status_code == 200
    assert downloaded.get_json() == payload


def test_api_update_user_when_missing(client, db_path, new_user):
    response = client.put("/api/users/update", json={"user_id": 9999, **new_user})
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}
    assert stored_users(db_path) == EXPECTED_USERS


def test_api_update_user_rejects_missing_field(client, db_path, new_user):
    response = client.put("/api/users/update", json=new_user)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing required fields: user_id"}
    assert stored_users(db_path) == EXPECTED_USERS


def test_api_update_user_rejects_invalid_id(client, db_path, new_user):
    response = client.put("/api/users/update", json={"user_id": "abc", **new_user})
    assert response.status_code == 400
    assert response.get_json() == {"error": "user_id must be an integer"}
    assert stored_users(db_path) == EXPECTED_USERS


# 10. API DELETE: check status, response body, and subsequent absence.
def test_api_delete_user(client, db_path):
    response = client.delete("/api/users/delete/1")
    assert response.status_code == 200
    assert response.get_json() == {"status": "User deleted successfully"}
    assert stored_users(db_path) == EXPECTED_USERS[1:]
    downloaded = client.get("/api/users/1")
    assert downloaded.status_code == 404
    assert downloaded.get_json() == {"error": "User not found"}


def test_api_delete_user_when_missing(client, db_path):
    response = client.delete("/api/users/delete/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}
    assert stored_users(db_path) == EXPECTED_USERS


def test_api_delete_user_twice(client, db_path):
    first = client.delete("/api/users/delete/1")
    second = client.delete("/api/users/delete/1")
    assert first.status_code == 200
    assert first.get_json() == {"status": "User deleted successfully"}
    assert second.status_code == 404
    assert second.get_json() == {"error": "User not found"}
    assert stored_users(db_path) == EXPECTED_USERS[1:]
