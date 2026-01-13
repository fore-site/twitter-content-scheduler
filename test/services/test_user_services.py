from services.user import (get_new_access_token,
                        create_user_in_db,
                        revoke_tokens,
                        get_current_active_user,
                        get_current_user, 
                        deactivate_user)
import pytest
from fastapi import HTTPException
from models.TokenModel import Token
from models.UserModel import BaseUser, UserOut
from datetime import datetime, timedelta, timezone
import uuid

@pytest.mark.asyncio(loop_scope='session')
async def test_get_access_token():
    token_obj = await get_new_access_token(123)
    assert isinstance(token_obj, Token)

# @pytest.mark.asyncio(loop_scope='session')
# async def test_create_user():
#     user = BaseUser(id=1234, username='fores', display_name='site', is_premium=True)
#     created_user = await create_user_in_db(user)
#     assert len(created_user) == 2, "Tuple should contain access and refresh tokens"

@pytest.mark.asyncio(loop_scope='session')
async def test_get_current_user():
    user = await get_current_user(123)
    assert isinstance(user, UserOut)

@pytest.mark.asyncio(loop_scope='session')
async def test_get_current_user_invalid_id():
    with pytest.raises(HTTPException):
        await get_current_user(1)

@pytest.mark.asyncio(loop_scope='session')
async def test_get_active_user():
    user = await get_current_user(123)
    active_user = await get_current_active_user(user)
    assert isinstance(active_user, UserOut)

@pytest.mark.asyncio(loop_scope='session')
async def test_get_disabled_user():
    user = await get_current_user(1234)
    with pytest.raises(HTTPException):
        await get_current_active_user(user)

@pytest.mark.asyncio(loop_scope='session')
async def test_revoke_access_tokens():
    payload = {
        "sub": 1234,
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=30),
        "jti": str(uuid.uuid4()),
        "type": "access"
    }
    result = {"detail": f"{payload['type']} token revoked successfully."}
    assert await revoke_tokens(payload) == result

@pytest.mark.asyncio(loop_scope='session')
async def test_revoke_refresh_tokens():
    payload = {
        "sub": 1234,
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=30),
        "jti": str(uuid.uuid4()),
        "type": "refresh"
    }
    result = {"detail": f"{payload['type']} token revoked successfully."}
    assert await revoke_tokens(payload) == result

@pytest.mark.asyncio(loop_scope='session')
async def test_deactivate_user():
    assert await deactivate_user(123) == {"message": 'User 123 deactivated.'}