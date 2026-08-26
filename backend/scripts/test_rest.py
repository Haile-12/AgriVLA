import requests
import os
import json

api_key = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LU-OQrMkqz6po8J4gXJ5Ms-VgldhQfwkCMgBvmPuW6aw")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key
}
data = {
    "contents": [{"parts": [{"text": "Explain how AI works in a few words"}]}]
}

print(f"Testing Gemini REST API...")
response = requests.post(url, headers=headers, json=data)

print(f"Status Code: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)
