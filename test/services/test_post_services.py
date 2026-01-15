from config.settings import TWITTER_USER_ID
from fastapi import HTTPException
from models.PostModel import BasePost, UpdatePost, PostOut
from services.post import get_all_posts, get_post, create_post, update_post, delete_post
import pytest

@pytest.mark.asyncio(loop_scope='session')
async def test_create_post():
    post = BasePost(text='Hello', minutes=1)
    assert await create_post(123, post) == post
    
@pytest.mark.asyncio(loop_scope='session')
async def test_create_post_invalid_values():
    post = BasePost(text='Hello', minutes=-1)
    assert await create_post(123, post) == post

@pytest.mark.asyncio(loop_scope='session')
async def test_get_post():
    post = await get_post(5, TWITTER_USER_ID)
    assert isinstance(post, PostOut)

@pytest.mark.asyncio(loop_scope='session')
async def test_get_post_invalid_PostID():
    assert await get_post(-8, TWITTER_USER_ID) == []

@pytest.mark.asyncio(loop_scope='session')
async def test_get_all_posts():
    posts = await get_all_posts(TWITTER_USER_ID)
    result_format = {"data": None, "pagination": None}
    assert posts.keys() == result_format.keys()

@pytest.mark.asyncio(loop_scope='session')
async def test_get_all_posts_empty():
    posts = await get_all_posts(1234)
    assert posts == []

@pytest.mark.asyncio(loop_scope='session')
async def test_update_post():
    post = UpdatePost(text='New')
    assert await update_post(2, TWITTER_USER_ID, post) == post

@pytest.mark.asyncio(loop_scope='session')
async def test_update_post_invalid_postID():
    post = UpdatePost(text='Update')
    with pytest.raises(HTTPException):
        await update_post(25, 123, post)

@pytest.mark.asyncio(loop_scope='session')
async def test_update_post_non_pending_status():
    post = UpdatePost(text='New update')
    with pytest.raises(HTTPException):
        await update_post(19, TWITTER_USER_ID, post)

@pytest.mark.asyncio(loop_scope='session')
async def test_delete_post():
    assert await delete_post(8, TWITTER_USER_ID) == None

@pytest.mark.asyncio(loop_scope='session')
async def test_delete_post_invalid_postID():
    with pytest.raises(HTTPException):
        await delete_post(40, TWITTER_USER_ID)