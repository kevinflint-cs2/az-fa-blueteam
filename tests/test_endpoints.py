import requests

BASE_URL = "http://localhost:7071/api"

def test_helloworld():
    response = requests.get(f"{BASE_URL}/helloworld", params={"name": "Kevin"})
    assert response.status_code == 200
    assert response.text == "Hello, Kevin"

def test_goodbye():
    response = requests.get(f"{BASE_URL}/goodbye", params={"name": "Kevin"})
    assert response.status_code == 200
    assert response.text == "Goodbye, Kevin"

def test_helloworld_missing_name():
    response = requests.get(f"{BASE_URL}/helloworld")
    assert response.status_code == 400

def test_goodbye_missing_name():
    response = requests.get(f"{BASE_URL}/goodbye")
    assert response.status_code == 400