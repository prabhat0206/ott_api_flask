from flask import Flask, abort
from flask_httpauth import HTTPBasicAuth
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

app.config["UPLOAD_IMG"] = UPLOAD_IMG


app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///'+DB_NAME
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

migrate = Migrate(app, db)
auth = HTTPBasicAuth()
CORS(app, resources={r"/api/*": {"origins": "*"}})

db.init_app(app)
migrate.init_app(app, db)


client = razorpay.Client(auth=("rzp_test_Xt2JLjZeOvsi19", "pbDRRTEMdA2kezzQbJh1hD55"))


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
from .models import *

if not path.exists('API/' + DB_NAME):
    db.create_all(app=app)


@auth.verify_password
def verify(username, password):
    user = User_table.query.filter_by(uid=username).first()
    if user:
        if user.password == password:
            return True
    return False


app.register_blueprint(product_api, url_prefix='/')
# app.register_blueprint(payment_api, url_prefix='/')
app.register_blueprint(admin, url_prefix='/')
app.register_blueprint(account_api, url_prefix='/')
app.register_blueprint(order_api, url_prefix='/')
