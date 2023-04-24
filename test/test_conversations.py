from fastapi.testclient import TestClient

from src.api.server import app

conversation = {
  "character_1_id": 0,
  "character_2_id": 1,
  "lines": [
    {
      "character_id": 0,
      "line_text": "string"
    }
  ]
}

conversationB = {
  "character_1_id": 0,
  "character_2_id": 0,
  "lines": [
    {
      "character_id": 0,
      "line_text": "string"
    }
  ]
}

client = TestClient(app)
def test_post_conversation():
    response = client.post("/movies/0/conversations/", json = conversation)
    assert response.status_code == 200
    assert response.json() == 83074

def test_post_invalid_conversation():
    response = client.post("/movies/0/conversations/", json = conversationB)
    assert response.status_code == 400
