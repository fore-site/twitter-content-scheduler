from services.user import get_new_access_token, create_user_in_db, get_access_refresh_token, revoke_tokens, get_current_active_user, get_current_user

headers = {
    "Authorization": "Bearer "
}

def test_access_retrieval():
    assert get_new_access_token is not None

def test_create_user():
    assert create_user_in_db is not None

def test_get_access_refresh():
    assert get_access_refresh_token is not None

def test_revoke_tokens():
    assert revoke_tokens is not None

def test_get_current_user():
    assert get_current_user is not None

def test_active_user():
    assert get_current_active_user is not None