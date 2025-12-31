from utils.auth_utils import create_access_token

def test_auth():
    assert create_access_token is not None

