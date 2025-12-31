from datetime import datetime, timedelta, timezone
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidAlgorithmError, InvalidSignatureError
import jwt
import requests
import time

header = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjExNjI0MTk2Nzc5MTU3MzQwMTcsImV4cCI6MTc2MjQyNjE1MiwianRpIjoiMTcwZDk2NzMtYTM5Yy00YTQ3LTg5M2YtODk2OWYxZDUxY2U3IiwidHlwZSI6InJlZnJlc2gifQ.t8qZk3yOhaAg_b0sUQF7o-zjQ0YRQHcZU0j6Tecou3w"
}

# def test_refresh_token():
#     refresh = requests.get("http://127.0.0.1:5000/refresh", headers=header)
#     refresh.raise_for_status()
#     res = refresh.json()
#     assert res is not None

# refresh = requests.get("http://127.0.0.1:5000/refresh", headers=header)
# res = refresh.json()
# print(res)

token = jwt.encode({"sub": 123, "exp": datetime.now(timezone.utc) + timedelta(seconds=3)}, "secret", "HS256")
print(token)
time.sleep(1)

try:
    t = jwt.decode(token, key="secret", algorithms=["HS256"])
except ExpiredSignatureError:
    print("expired")
except InvalidAlgorithmError:
    print("Algorithm")
except InvalidSignatureError:
    print("Signature")
else:
    print(t)