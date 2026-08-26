import requests
import sys

agent_id = "df5df765-ff9e-499f-a518-9b6463127d75" # Using the one from logs
url = f"http://127.0.0.1:8000/api/v1/agents/{agent_id}/step"

# We just need to trigger the endpoint. The frontend passes a bearer token.
# Wait, do we need auth? The route has `current_user: UserInDB = Depends(get_current_user)`.
# I might get a 401 Unauthorized. Let's create a test user, or just see if the backend allows it.

print(f"Testing {url} ...")
try:
    resp = requests.post(url)
    print(resp.status_code)
    print(resp.text)
except Exception as e:
    print(e)
