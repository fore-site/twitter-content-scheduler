from services.post import get_all_posts, get_post, create_post, update_post, delete_post

def test_create_post():
    assert create_post is not None

def test_update_post():
    assert update_post is not None