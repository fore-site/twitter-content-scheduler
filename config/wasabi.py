from config.settings import WASABI_ACCESS_KEY, WASABI_SECRET_KEY
import boto3

class WasabiClient:
    def __init__(self):
        self.s3 = boto3.client('s3',
                  endpoint_url="https://s3.eu-west-3.wasabisys.com",
                  aws_access_key_id=WASABI_ACCESS_KEY,
                  aws_secret_access_key=WASABI_SECRET_KEY)
    
    def generate_presigned_url(self, key: str, method: str = 'put'):
        url = self.s3.generate_presigned_url(
            ClientMethod=f'{method.lower()}_object',
            Params={
                'Bucket': 'content-scheduler',
                'Key': key
            },
            ExpiresIn=604800 if method.lower() == 'get' else 3600,
            HttpMethod=method.upper())
        return url
