# c:\Users\rwmot\OneDrive\Documents\dockerme\pingservice\test_app.py
import pytest
import requests_mock
import requests
from app import app as flask_app

@pytest.fixture
def client():
    """Create a Flask test client."""
    flask_app.config['TESTING'] = True
    # Optional: Propagate exceptions during testing to see underlying errors
    # flask_app.config['PROPAGATE_EXCEPTIONS'] = True
    with flask_app.test_client() as client:
        yield client

# Define the URL centrally for consistency
PONG_SERVICE_URL = "http://pong-service:5001/pong"

def test_ping_success(client, requests_mock):
    """Test the /ping endpoint successfully calls pong service."""
    # Arrange
    expected_pong_response = "Mocked Pong!"
    requests_mock.get(PONG_SERVICE_URL, text=expected_pong_response, status_code=200)

    # Act
    response = client.get("/ping")

    # Assert
    assert response.status_code == 200
    assert response.data.decode('utf-8') == f"Ping -> {expected_pong_response}"
    assert requests_mock.called
    assert requests_mock.last_request.url == PONG_SERVICE_URL

def test_ping_pong_service_http_error(client, requests_mock):
    """Test /ping when pong service returns an HTTP error (e.g., 500)."""
    # Arrange: Mock pong service to return 500
    error_text = "Internal Server Error from Pong"
    requests_mock.get(PONG_SERVICE_URL, status_code=500, text=error_text)

    # Act: Call the /ping endpoint
    response = client.get("/ping")

    # Assert: Check that the ping service returns a 502 Bad Gateway
    # because it received an error from the upstream service.
    assert response.status_code == 502 # Bad Gateway
    assert f"Error: Pong service failed with status 500" in response.data.decode('utf-8')
    assert requests_mock.called
    assert requests_mock.last_request.url == PONG_SERVICE_URL

def test_ping_pong_service_connection_error(client, requests_mock):
    """Test /ping when the pong service cannot be reached."""
    # Arrange: Mock a connection error
    requests_mock.get(PONG_SERVICE_URL, exc=requests.exceptions.ConnectionError)

    # Act
    response = client.get("/ping")

    # Assert: Check for 502 Bad Gateway or appropriate error
    assert response.status_code == 502 # Bad Gateway
    assert "Error: Could not connect to pong service" in response.data.decode('utf-8')
    assert requests_mock.called
    assert requests_mock.last_request.url == PONG_SERVICE_URL

def test_ping_pong_service_timeout(client, requests_mock):
    """Test /ping when the request to pong service times out."""
    # Arrange: Mock a timeout
    requests_mock.get(PONG_SERVICE_URL, exc=requests.exceptions.Timeout)

    # Act
    response = client.get("/ping")

    # Assert: Check for 504 Gateway Timeout
    assert response.status_code == 504 # Gateway Timeout
    assert "Error: Timeout contacting pong service" in response.data.decode('utf-8')
    assert requests_mock.called
    assert requests_mock.last_request.url == PONG_SERVICE_URL

