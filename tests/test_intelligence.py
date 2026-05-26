import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    return app.test_client()


def test_chat_endpoint_returns_response(client):
    response = client.post("/api/chat", json={"message": "Hello, what is 2+2?"})
    assert response.status_code == 200
    data = response.get_json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert data["response"]


def test_chat_endpoint_rejects_empty_message(client):
    response = client.post("/api/chat", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "message is required"


def test_summarize_endpoint_returns_summary(client):
    response = client.post(
        "/api/summarize",
        json={"text": "First sentence. Second sentence. Third sentence."},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "summary" in data
    assert data["summary"].startswith(("Summary: ", "Resumen: "))
