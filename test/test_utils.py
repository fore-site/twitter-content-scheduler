from utils.AuthUtils import create_access_token

def test_auth():
    assert create_access_token is not None

