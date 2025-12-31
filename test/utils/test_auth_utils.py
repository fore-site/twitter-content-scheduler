from utils.auth_utils import generate_verifier, create_access_token, create_refresh_token
import pytest

def test_generate_code_verifier():
    assert generate_verifier() != None

class TestTokens:
    def test_create_access_token(self):
        payload = {"sub": 1234}
        access_token = create_access_token(payload)
        assert access_token != None

    def test_create_access_token_with_invalid_payload_key(self):
        payload = {"id": 1234}
        with pytest.raises(ValueError):
            create_access_token(payload)

    def test_create_refresh_token(self):
        payload = {"sub": 1234}
        access_token = create_refresh_token(payload)
        assert access_token != None

    def test_create_refresh_token_with_invalid_payload_key(self):
        payload = {"id": 1234}
        with pytest.raises(ValueError):
            create_refresh_token(payload)

    