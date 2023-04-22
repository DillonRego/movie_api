from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)
def test_get_linesbychar():
    response = client.get("/lines/bycharacter/0?limit=5&offset=5")
    assert response.status_code == 200

    with open("test/lines/49.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_lines():
    response = client.get("/lines/50")
    assert response.status_code == 200

    with open("test/lines/50.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_characters():
    response = client.get("/lines/?text=father&limit=5&offset=0")
    assert response.status_code == 200

    with open("test/lines/father.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_404():
    response = client.get("/lines/0")
    assert response.status_code == 404