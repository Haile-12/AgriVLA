import sys

print("Testing Gemini API connection...")

try:
    from google import genai
    print("[OK] google-genai SDK imported successfully")
except ImportError as e:
    print(f"[FAIL] Failed to import google-genai: {e}")
    sys.exit(1)

API_KEY = "AQ.Ab8RN6LU-OQrMkqz6po8J4gXJ5Ms-VgldhQfwkCMgBvmPuW6aw"

try:
    client = genai.Client(api_key=API_KEY)
    print("[OK] Gemini client created")
except Exception as e:
    print(f"[FAIL] Failed to create client: {e}")
    sys.exit(1)

try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say the single word OK and nothing else."
    )
    print(f"[OK] API call succeeded! Response: {response.text.strip()}")
    print("\n=== GEMINI API IS WORKING CORRECTLY ===")
except Exception as e:
    print(f"[FAIL] API call failed: {e}")
    sys.exit(1)
