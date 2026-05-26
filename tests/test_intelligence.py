from io import BytesIO

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


def test_upload_pdf_endpoint_returns_summary(client):
    pdf_bytes = b'''%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT /F1 24 Tf 72 120 Td (Hello world) Tj ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000063 00000 n 
0000000122 00000 n 
0000000244 00000 n 
0000000311 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
410
%%EOF'''

    response = client.post(
        "/api/v1/documento/upload",
        data={"file": (BytesIO(pdf_bytes), "example.pdf")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["file_name"] == "example.pdf"
    assert data["document_id"]
    assert data["summary"].startswith(("Summary: ", "Resumen: "))
    assert data["extracted_text"] == "Hello world"


def test_upload_rejects_non_pdf(client):
    response = client.post(
        "/api/v1/documento/upload",
        data={"file": (BytesIO(b"not a pdf"), "example.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "only PDF files are supported"


def test_v1_summarize_endpoint_returns_summary(client):
    response = client.post(
        "/api/v1/summaries",
        json={"document_id": "doc-123", "text": "Alpha. Beta. Gamma."},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["document_id"] == "doc-123"
    assert data["summary"].startswith(("Summary: ", "Resumen: "))
