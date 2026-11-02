from hello_add import app


def test_add():
    with app.test_client() as client:
        response = client.post("/add", json={"a": 1, "b": 2})
    assert response.status_code == 200
    assert response.get_json() == {"sum": 3}
