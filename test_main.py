from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_todo():
    response = client.post("/todos", json={"title": "Test Task", "description": "Learn CI/CD"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data

def test_get_todos():
    response = client.get("/todos")
    assert response.status_code == 500
    assert isinstance(response.json(), list)
