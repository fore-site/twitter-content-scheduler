from services.user import (get_new_access_token,
                        create_user_in_db,
                        revoke_tokens,
                        get_current_active_user,
                        get_current_user, 
                        update_user)
import pytest
from fastapi import HTTPException
from models.TokenModel import Token
from models.UserModel import BaseUser, UserOut

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

# def test_revoke_tokens():
#     assert revoke_tokens is not None
