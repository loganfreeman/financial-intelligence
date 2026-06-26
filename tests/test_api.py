import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_company_relationships(client: TestClient) -> None:
    response = client.get("/companies/NVDA/relationships")
    assert response.status_code == 200
    payload = response.json()
    assert any(item["type"] == "SUPPLIER_DEPENDENCY" for item in payload)
    assert any(item["target_ticker"] == "AMD" for item in payload)


def test_factors(client: TestClient) -> None:
    response = client.get("/companies/AAPL/factors")
    assert response.status_code == 200
    names = {item["factor_name"] for item in response.json()}
    assert {"quality", "momentum", "volatility"}.issubset(names)


def test_network(client: TestClient) -> None:
    response = client.get("/network/NVDA")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "NVDA"
    assert payload["nodes"]
    assert payload["edges"]
