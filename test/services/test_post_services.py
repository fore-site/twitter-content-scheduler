from models.PostModel import BasePost
from services.post import get_all_posts, get_post, create_post, update_post, delete_post
import pytest


@pytest.mark.asyncio(loop_scope='session')
async def test_create_post():
    post = BasePost(text='Hello', days=3)
    assert create_post(123, post) is not None

def test_update_post():
    assert update_post is not None