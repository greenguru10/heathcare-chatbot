def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"


def test_sources_endpoint(client):
    response = client.get("/api/v1/sources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_categories_endpoint(client):
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_emergency_query_flow(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "I have severe chest pain and difficulty breathing"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "red"
    assert data["response_mode"] == "emergency"
    assert "urgent medical attention" in data["answer"].lower()
    assert len(data["sources"]) == 0  # No LLM or retrieval call executed


def test_blocked_medication_flow(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "What medicine should I take for this severe cough?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "blocked"
    assert data["response_mode"] == "safety_refusal"
    assert "cannot advise on specific medications" in data["answer"].lower()


def test_general_grounded_chat_flow(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "What is blood pressure?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["green", "yellow"]
    assert "answer" in data
    assert "confidence" in data
