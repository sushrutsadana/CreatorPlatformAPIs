import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

def test_openai_connection():
    response = client.get("/api/v1/contract/test-openai")
    assert response.status_code == 200
    assert "status" in response.json()

@patch('app.services.generate_contract.generate_contract_from_llm')
def test_generate_contract(mock_generate):
    mock_generate.return_value = "Sample contract text"
    
    response = client.post("/api/v1/contract/generate/test-creator-id")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "contract_text" in response.json() 