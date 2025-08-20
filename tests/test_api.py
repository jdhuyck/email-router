import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
class TestAPIEndpoints:
    """Test suite for the API endpoints using an AsyncClient."""

    @pytest_asyncio.fixture
    async def client(self):
        """Fixture to create an AsyncClient for testing the app."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as test_client:  # noqa:E501
            yield test_client

    async def test_root_endpoint(self, client):
        """Test the root endpoint returns a successful response."""
        response = await client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "Email Router API is running."}

    async def test_health_endpoint(self, client):
        """Test the health endpoint returns a healthy status."""
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    async def test_classify_endpoint_valid_request(self, client):
        """Test the classify endpoint with a valid request."""
        payload = {
            "email_text": "I can't log into my account, please help reset my password."
        }  # noqa:E501

        response = await client.post("/api/v1/classify", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "labels" in data
        assert "scores" in data
        assert "sequence" in data
        assert data["labels"][0] in ["customer support", "billing issue", "complaint"]

    async def test_classify_endpoint_empty_text(self, client):
        """Test the classify endpoint with empty text returns a 400 error."""
        payload = {"email_text": "   "}

        response = await client.post("/api/v1/classify", json=payload)

        assert response.status_code == 400
        assert "detail" in response.json()
