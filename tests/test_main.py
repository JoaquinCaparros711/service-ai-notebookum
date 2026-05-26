import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    return app.test_client()


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Service AI NotebookUm is running"


def test_v1_index(client):
    response = client.get("/api/v1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Service AI NotebookUm is running"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "ok", "service": "ai"}


def test_v1_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "ok", "service": "ai"}