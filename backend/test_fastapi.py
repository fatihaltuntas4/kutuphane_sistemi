from fastapi.testclient import TestClient
from main import app
import traceback

client = TestClient(app)

try:
    response = client.post("/auth/register", json={
        "full_name": "Test",
        "email": "test1000@test.com",
        "password": "123",
        "role": "Yönetici"
    })
    print("Status:", response.status_code)
    print("JSON:", response.json())
except Exception as e:
    traceback.print_exc()
