from celery import Celery
from config.settings import REDIS_URI
from utils.auth_utils import twitter_client

celery_app = Celery('tasks', backend=REDIS_URI, broker=REDIS_URI)

@celery_app.task
def send_post(data):
    
    twitter_client.post(url="https://api.x.com/2/tweets")
