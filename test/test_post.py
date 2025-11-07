import requests 
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTYyNDE5Njc3OTE1NzM0MDE3IiwiZXhwIjoxNzYyNTQzNTQzLCJqdGkiOiI2ZGYyNzAyYi1iYTc3LTQ1YTItOThlOC01MDI2NzlkM2M1MDIiLCJ0eXBlIjoiYWNjZXNzIn0.oGttue0wTUvle-OsfvRIMUbV5AvimOna-pz7WWeOGus"
}

data = {
    "content": "Hello Twitte/r",
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