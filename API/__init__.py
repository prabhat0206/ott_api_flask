from flask import Flask, abort
from flask_httpauth import HTTPTokenAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from flask_cors import CORS
from os import path
import razorpay
from datetime import date
import boto3
from botocore.config import Config
from .config import S3_KEY, S3_SECRET, S3_BUCKET, S3_LOCATION, S3_REGION
# from werkzeug.security import check_password_hash

DB_NAME = 'API.db'
app = Flask(__name__)
app.config.from_pyfile('config.py')
UPLOAD_IMG = './static/'
UPLOAD_MOV = './UPLOADS'

BASE_IMAGE_URL = ""

app.config["UPLOAD_IMG"] = UPLOAD_IMG
db = SQLAlchemy(app)


s3 = boto3.client(
   "s3",
   config=Config(signature_version='s3v4'),
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET,
   region_name=S3_REGION
)

migrate = Migrate(app, db)
auth = HTTPTokenAuth(scheme="Bearer")
CORS(app, resources={r"/*": {"origins": "*"}})

db.init_app(app)
migrate.init_app(app, db)


client = razorpay.Client(auth=("rzp_test_grEV6KDDjdjUsj", "q4zynOZi8zg3JLf5t2Yo81PU"))


def get_model_dict(model):
    return dict((column.name, getattr(model, column.name))
                for column in model.__table__.columns)


def permission_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            uid = auth.current_user()
            user = User_table.query.filter_by(uid=uid).first()
            orders = user.membership_order
            if len(orders) > 0:
                order = orders[len(orders)-1]
                if order.valid_till < date.today():
                    user.membership_order.remove(order)
                    user.membership = "FREE"
                    db.session.commit()
            if user.membership == "FREE":
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def upload_file_to_s3(file, acl=False):
    better_filename = file.filename.replace(".", "").replace(" ", "_")
    try:
        if acl:
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                better_filename,
                ExtraArgs={
                    "ContentType": file.content_type
                }
            )
            return better_filename
        else:
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                better_filename,
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": file.content_type
                }
            )
            return "{}{}".format(S3_LOCATION, better_filename)

    except Exception as e:
        print("Something Happened: ", e)
        return e


def generate_signed_url(file):
    try:
        response = s3.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': file}, ExpiresIn=3600)
        return response
    except Exception as e:
        print(e)



from .account_api import account_api
from .product_api import product_api
from .order_api import order_api
from .admin_api import admin
from .payment_api import payment_api
from .models import *

if not path.exists('API/' + DB_NAME):
    db.create_all(app=app)


@auth.verify_token
def verify_token(token):
    user_id = token.split(":")[0]
    password = token.split(":")[1]
    user = User_table.query.filter_by(uid=user_id).first()
    if user:
        if user.password == password:
            return user.uid
    return False


app.register_blueprint(product_api, url_prefix='/')
app.register_blueprint(payment_api, url_prefix='/')
app.register_blueprint(admin, url_prefix='/')
app.register_blueprint(account_api, url_prefix='/')
app.register_blueprint(order_api, url_prefix='/')
