from . import db
import datetime

class User_table(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    Ph_number = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    full_name = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    DOB = db.Column(db.String, nullable=False)
    Gender = db.Column(db.String, nullable=False)
    profile_pic = db.Column(
        db.String,
        default="https://i.pinimg.com/564x/65/25/a0/6525a08f1df98a2e3a545fe2ace4be47.jpg"
    )
    watchlist = db.relationship("Movie", backref="in_watchlist_of")
    watchlist_web = db.relationship("Web_series", backref="in_watchlist")
    # History = db.relationship("Movie", backref="History_of", overlaps="in_watchlist_of,watchlist")
    # orders = db.relationship("Order", backref="order_by")
    membership = db.Column(db.String, nullable=False, default="FREE")
    membership_order = db.relationship("Order", backref="User", overlaps="order_by,orders")
    razorpay_id = db.Column(db.String, nullable=False)

#payment id method status amount

class Genre(db.Model):
    gid = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.Integer, db.ForeignKey('user_table.uid'))
    name = db.Column(db.String)
    image_url = db.Column(db.String)


temp_tabel = db.Table(
    'temp_tabel',
    db.Column('mid', db.Integer, db.ForeignKey('movie.mid'), primary_key=True),
    db.Column('gid', db.Integer, db.ForeignKey('genre.gid'), primary_key=True)
)


class Movie(db.Model):
    mid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user_table.uid'))
    name = db.Column(db.String)
    short_description = db.Column(db.String)
    image_url = db.Column(db.String)
    date = db.Column(db.Date)
    description = db.Column(db.String)
    gid = db.relationship('Genre', secondary=temp_tabel, lazy='subquery',
                          backref=db.backref('movies', lazy=True))
    q480p = db.Column(db.String)
    q720p = db.Column(db.String)
    q1080p = db.Column(db.String)
    genre = db.Column(db.String)
    Language = db.Column(db.String)
    Director = db.Column(db.String)
    Type = db.Column(db.String)
    orignal = db.Column(db.Integer)
    trending = db.Column(db.Boolean, default=False)
    sid = db.Column(db.Integer, db.ForeignKey('season.sid'))


class Season(db.Model):
    sid = db.Column(db.Integer, primary_key=True)
    mid = db.relationship("Movie", backref="Season")
    name = db.Column(db.String)
    date = db.Column(db.Date)
    wsid = db.Column(db.Integer, db.ForeignKey('web_series.wsid'))
    orignal = db.Column(db.Integer)


class Web_series(db.Model):
    wsid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user_table.uid"))
    name = db.Column(db.String)
    short_description = db.Column(db.String)
    image_url = db.Column(db.String)
    genre = db.Column(db.String)
    sid = db.relationship("Season", backref="Series")
    description = db.Column(db.String)
    date = db.Column(db.Date)
    orignal = db.Column(db.Integer)
    Language = db.Column(db.String)
    Director = db.Column(db.String)
    trending = db.Column(db.Boolean, default=False)


class Order(db.Model):
    oid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user_table.uid'))
    date = db.Column(db.Date, nullable=False)
    valid_till = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    payment_id = db.Column(db.String)
    membership = db.Column(db.String)
    amount = db.Column(db.String)
    payment_status = db.Column(db.String)


class Banners(db.Model):
    bid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    b_url = db.Column(db.String)


class BackupDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_date = db.Column(db.Date, default=datetime.datetime.strptime("2022-01-01", "%Y-%m-%d").date())
