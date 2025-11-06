import requests 
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjExNjI0MTk2Nzc5MTU3MzQwMTcsImV4cCI6MTc2MjM0MTU1MiwianRpIjoiMjMwN2E3N2QtNTQwNS00NzZlLWFkMWQtMzQyNDVhYjEzZTAzIiwidHlwZSI6ImFjY2VzcyJ9.9gwL0XW6Y3wefhnx_Hk_P3z5LLr3mmGlY9OuFkKhceA"
}

data = {
    "content": "Hello Twitter",
    "hours": 4,
}

def test_create_post():
    make_post = requests.post("http://127.0.0.1:5000/posts", json=data, headers=headers)
    make_post.raise_for_status()
    post = make_post.json()
    assert post is not None

# from routes.post import make_post, post_update

# def test_make_post():
#     assert make_post is not None

# def test_post_update():
#     assert post_update is not None