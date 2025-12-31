import requests 
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTYyNDE5Njc3OTE1NzM0MDE3IiwiZXhwIjoxNzYyNTQ3OTQxLCJqdGkiOiJhOWMzOWVjYS0yOTAyLTQ5OTYtODk3My04ZDZmZjJkNTJiNjgiLCJ0eXBlIjoiYWNjZXNzIn0.8ZYMBfldc1cbLEj8zLCcdRxWT_J48fbdtlf9Fzj6AlA"
}

data = {
    "content": "Hello Twitte/r, WAGA TOMO YO!!",
    "hours": 1,
    "days": 2,
    "minutes": 30
}

# def test_create_post():
#     make_post = requests.post("http://127.0.0.1:5000/posts", json=data, headers=headers)
#     make_post.raise_for_status()
#     post = make_post.json()
#     assert post is not None

make_post = requests.get("http://127.0.0.1:5000/posts/4", headers=headers)
post = make_post.json()
print(post)


# from routes.post import make_post, post_update

# def test_make_post():
#     assert make_post is not None

# def test_post_update():
#     assert post_update is not None