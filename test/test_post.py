import requests 
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjExNjI0MTk2Nzc5MTU3MzQwMTcsImV4cCI6MTc2MjUwOTg5MywianRpIjoiNDc2M2Q0MzAtZDQ5OC00YWRjLTgwZTAtNWZjY2E1M2Q3MmIyIiwidHlwZSI6ImFjY2VzcyJ9.pzhZyQO3POhElHsJPJh1Gtfk0_qwvAdFDTZj6GwMGuM"
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