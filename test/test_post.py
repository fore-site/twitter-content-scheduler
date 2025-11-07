import requests 
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTYyNDE5Njc3OTE1NzM0MDE3IiwiZXhwIjoxNzYyNTM5ODk0LCJqdGkiOiI3MGE2ZTA3Ni05MjJlLTQ1YTQtOTQ3Ny0wOTg2MjJlY2MxZGUiLCJ0eXBlIjoiYWNjZXNzIn0.8NrkAX8X-WdESuTxHJk4-GXHtxfGugroeoH1Pw8ZIfA"
}

data = {
    "content": "Hello Twitter",
    "hours": 4,
}

# def test_create_post():
#     make_post = requests.post("http://127.0.0.1:5000/posts", json=data, headers=headers)
#     make_post.raise_for_status()
#     post = make_post.json()
#     assert post is not None


make_post = requests.post("http://127.0.0.1:5000/posts", json=data, headers=headers)
post = make_post.json()
print(post)


# from routes.post import make_post, post_update

# def test_make_post():
#     assert make_post is not None

# def test_post_update():
#     assert post_update is not None