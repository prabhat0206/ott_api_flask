import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('secret_key')
SQLALCHEMY_DATABASE_URI = os.environ.get('db_url')
SQLALCHEMY_TRACK_MODIFICATIONS = True

S3_BUCKET = os.environ.get('bucket')
S3_KEY = os.environ.get('s3_key')
S3_SECRET = os.environ.get('s3_secret')
S3_REGION = os.environ.get('s3_region')
S3_LOCATION = 'https://{}.s3.amazonaws.com/'.format(S3_BUCKET)
