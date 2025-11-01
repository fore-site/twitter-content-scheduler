import requests

headers = {
    "Authorization": "Bearer "
}
def add(x):
    return x + 1

def test_add():
    assert add(2) == 3