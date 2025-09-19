import requests 
from urllib.parse import urljoin
import json

def read_api_endpoint(endpoint = "/", base_url = "http://127.0.0.1:8000"):
    url = urljoin(base_url, endpoint)
    response = requests.get(url)
    
    return response


def post_api_endpoint(endpoint, data, base_url="http://127.0.0.1:8000"):
    url = urljoin(base_url, endpoint)
    headers = {'Content-Type': 'application/json'} # Datan som skickas är i JSON-format
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error making POST request to {url}: {e}")
        return None