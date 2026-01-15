import pytest

@pytest.mark.asyncio(loop_scope='session')
async def test_get_profile(default_access_token, async_client):
    header = {
        "Authorization": f"Bearer {default_access_token}"
        }
    res = await async_client.get('/v1/profile', headers=header)
    assert res.status_code == 200
    assert res.json().keys() == {"id": 123, 
                                  "username": None, 
                                  "display_name": None,
                                  "profile_img": None,
                                  "is_premium": False,
                                  "user_status": None,
                                  "registered_at": None,
                                  "pending_posts": None,
                                  "sent_posts": None,
                                  "failed_posts": None}.keys()