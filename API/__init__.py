from flask import Flask, abort
from flask_httpauth import HTTPTokenAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from flask_cors import CORS
from os import path
import razorpay
from datetime import date
# from werkzeug.security import check_password_hash

DB_NAME = 'API.db'
app = Flask(__name__)
app.secret_key = 'topsecret'
UPLOAD_IMG = './static/'
UPLOAD_MOV = './UPLOADS'

BASE_IMAGE_URL = "https://python7proffus.herokuapp.com"

app.config["UPLOAD_IMG"] = UPLOAD_IMG


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vkjgwkybkeokwx:01f31e64d8c35f4ec06a7e3efd210af4bcacfb697cef829d6474011f96e6a383@ec2-54-159-107-189.compute-1.amazonaws.com:5432/d7glihdfmkm190'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

migrate = Migrate(app, db)
auth = HTTPTokenAuth(scheme="Bearer")
CORS(app, resources={r"/api/*": {"origins": "*"}})

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
