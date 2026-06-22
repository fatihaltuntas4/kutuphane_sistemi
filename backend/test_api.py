import urllib.request
import json

url = "http://127.0.0.1:8000/auth/register"
data = {"full_name": "Test", "email": "test99@test.com", "password": "123", "role": "Yönetici"}
headers = {"Content-Type": "application/json"}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
