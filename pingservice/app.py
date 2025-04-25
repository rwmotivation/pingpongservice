# c:\Users\rwmot\OneDrive\Documents\dockerme\pingservice\app.py
from flask import Flask, Response
import requests
import logging # Optional: for better error logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO) # Optional: basic logging setup

PONG_SERVICE_URL = "http://pong-service:5001/pong"

@app.route("/ping")
def ping():
    try:
        # Make the request to the pong service
        response = requests.get(PONG_SERVICE_URL, timeout=5) # Added timeout

        # Raise an HTTPError if the status code is 4xx or 5xx
        response.raise_for_status()

        # If successful, return the combined message
        return f"Ping -> {response.text}"

    except requests.exceptions.Timeout:
        logging.error(f"Timeout connecting to {PONG_SERVICE_URL}")
        return Response("Error: Timeout contacting pong service", status=504) # Gateway Timeout

    except requests.exceptions.ConnectionError:
        logging.error(f"Connection error connecting to {PONG_SERVICE_URL}")
        return Response("Error: Could not connect to pong service", status=502) # Bad Gateway

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (4xx, 5xx) from the pong service
        logging.error(f"Pong service returned error: {e.response.status_code} - {e.response.text}")
        # Return a 502 Bad Gateway, indicating this service had trouble with an upstream service
        return Response(f"Error: Pong service failed with status {e.response.status_code}", status=502)

    except requests.exceptions.RequestException as e:
        # Catch any other request-related errors
        logging.error(f"An unexpected error occurred contacting pong service: {e}")
        return Response("Error: An unexpected error occurred while contacting pong service", status=500) # Internal Server Error

if __name__ == "__main__":
    # Use waitress or gunicorn in production instead of Flask's development server
    app.run(host="0.0.0.0", port=5000)

