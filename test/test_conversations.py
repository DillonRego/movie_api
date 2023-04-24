from fastapi.testclient import TestClient

from src.api.server import app

import json

conversation = json.dumps({
  "character_1_id": 0,
  "character_2_id": 1,
  "lines": [
    {
      "character_id": 0,
      "line_text": "string"
    }
  ]
})

conversationB = json.dumps({
  "character_1_id": 0,
  "character_2_id": 0,
  "lines": [
    {
      "character_id": 0,
      "line_text": "string"
    }
  ]
})

client = TestClient(app)
def test_post_conversation():
    response = client.post("/movies/0/conversations/", json=json.dumps(conversation))
    assert response.status_code == 200

    with "83074" as f:
        assert response.json() == f

def test_post_invalid_conversation():
    response = client.post("/movies/0/conversations/", json = json.dumps(conversationB))
    assert response.status_code == 400
