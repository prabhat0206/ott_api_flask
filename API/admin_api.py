from flask import Blueprint, jsonify, request, abort, send_file
from werkzeug.http import parse_authorization_header
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from .models import *
from . import S3_BUCKET, generate_signed_url, get_model_dict,  BASE_IMAGE_URL, upload_file_to_s3, s3, generate_signed_url_put
import os
static_folder = 'static'
admin = Blueprint('admin', __name__)


def admin_required(next):
    @wraps(next)
    def check_admin(*args, **kwargs):
        if request.headers.get('Authorization'):
            credentails = parse_authorization_header(
                request.headers.get('Authorization')
            )
            if credentails.password and credentails.username is not None:
                if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                    return next(*args, **kwargs)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)
    return check_admin


@admin.post('/admin/login')
def login():
    credentails = request.get_json()
    return {"Success": True if credentails['username'] == "thrillingwaves@gmail.com" and credentails['password'] == "9828060173@Python7" else False}


@admin.get("/admin/getLink/<mid>")
@admin_required
def get_link(mid):
    movie = Movie.query.filter_by(mid=int(mid)).first()
    link = generate_signed_url(movie.q1080p)
    return jsonify({"success": True, "link": link})


@admin.post('/admin/change_trending_movie')
@admin_required
def change_trending_movie():
    data = request.get_json()
    movie = Movie.query.filter_by(mid=int(data['mid'])).first()
    movie.trending = data['status']
    db.session.commit()
    return jsonify({'success': True})


@admin.post('/admin/change_trending_ws')
@admin_required
def change_trending_ws():
    data = request.get_json()
    movie = Web_series.query.filter_by(wsid=int(data['wsid'])).first()
    movie.trending = data['status']
    db.session.commit()
    return jsonify({'success': True})


@admin.post('/admin/getAllData')
@admin_required
def allData():
    movies = Movie.query.filter(Movie.Type != "Episode").all()
    web_series = Web_series.query.all()
    movies_data = []
    web_series_data = []
    if len(movies) > 0 or len(web_series) > 0:
        for movie in movies:
            movies_data.append(
                {
                    "mid": movie.mid,
                    "name": movie.name,
                    "image_url": BASE_IMAGE_URL + movie.image_url,
                }
            )
        for series in web_series:
            web_series_data.append(
                {
                    "wsid": series.wsid,
                    "name": series.name,
                    "image_url": BASE_IMAGE_URL + series.image_url,
                }
            )
        return jsonify({"success": True, 'Movies': movies_data, "Web_Series": web_series_data})
    else:
        return jsonify({"success": False})


@admin.route('/admin/getMovie', methods=['POST'])
@admin.route('/admin/getMovie/', methods=['POST'])
@admin_required
def get_Movie():
    data = request.get_json()
    mid = int(data['mid'])
    movie = Movie.query.filter_by(mid=mid).first()
    if movie:
        result = get_model_dict(movie)
        if movie.q1080p is not None:
            result['file_url'] = generate_signed_url(movie.q1080p)
        else:
            result['file_url'] = None
        return jsonify({'success': True, "Movie": result})
    return jsonify({'success': False})


@admin.post('/admin/getWeb_series')
@admin_required
def get_Web_series():
    data = request.get_json()
    wsid = data['wsid']
    ws = Web_series.query.filter_by(wsid=wsid).first()
    if ws:
        all_details = get_model_dict(ws)
        all_details['season'] = []
        for season in ws.sid:
            seasonEpisode = {}
            seasonEpisode['sid'] = season.sid
            seasonEpisode['name'] = season.name
            seasonEpisode['episodes'] = []
            name_season = 1
            for ep in season.mid:
                new_Episode = {
                    'mid': ep.mid,
                    'name': ep.name,
                    'image_url': ep.image_url,
                    "type": ep.Type,

                }
                if ep.q1080p is not None:
                    new_Episode["file_url"] = generate_signed_url(ep.q1080p)
                else:
                    new_Episode['file_url'] = None
                seasonEpisode['episodes'].append(new_Episode)
                name_season += 1
            all_details['season'].append(seasonEpisode)
        return jsonify({"success": True, 'WebSeries': all_details})
    else:
        return jsonify({'success': False})


@admin.get('/admin/aws_url/<key>')
@admin_required
def get_aws_url(key):
    return jsonify({'success': True, "url": generate_signed_url_put(key)})


@admin.route('/admin/addMovie', methods=['POST'])
@admin.route('/admin/addMovie/', methods=['POST'])
@admin_required
def add_Movie():
    data = request.form
    name = data['name']
    date = datetime.datetime.now()
    description = data['description']
    Language = data['Language']
    Director = data['Director']
    short_description = data['short_description']
    Type = 'Movie'
    image = request.files['image']
    genre = data['Genre']
    orignal = int(data['orignal'])
    movie = Movie(
        name=name,
        date=date,
        image_url=upload_file_to_s3(image),
        short_description=short_description,
        description=description,
        Language=Language,
        Director=Director,
        Type=Type,
        genre=genre,
        orignal=orignal
    )
    db.session.add(movie)
    # if 'q1080p' in request.files:
    q1080p = request.form['q1080p']
    if q1080p:
        movie.q1080p = q1080p
    db.session.commit()
    return jsonify({'success': True, 'mid': movie.mid}), 200


@admin.route('/admin/editMovie', methods=['POST'])
@admin.route('/admin/editMovie/', methods=['POST'])
@admin_required
def edit_Movie():
    data = request.form
    mid = int(data['mid'])
    name = data['name']
    description = data['description']
    Language = data['Language']
    Director = data['Director']
    short_description = data['short_description']
    genre = data['Genre']
    orignal = int(data['orignal'])
    movie = Movie.query.filter_by(mid=mid).first()
    if movie:
        movie.name = name
        movie.description = description
        movie.Language = Language
        movie.short_description = short_description
        movie.Director = Director
        movie.genre = genre
        movie.orignal = orignal

        if 'image' in request.files:
            movie.image_url = upload_file_to_s3(request.files['image'])
    
        if 'q1080p' in request.form:
            q1080p = request.form['q1080p']
            if q1080p:
                s3.delete_object(Bucket=S3_BUCKET, Key=movie.q1080p)
                movie.q1080p = q1080p

        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        abort(422)


@admin.route('/admin/deleteMovie', methods=['POST'])
@admin.route('/admin/deleteMovie/', methods=['POST'])
@admin_required
def delete_Movie():
    try:
        data = request.get_json()
        mid = data['mid']
        movie = Movie.query.filter_by(mid=mid).first()
        if movie:
            if movie.q1080p:
                filename = movie.q1080p
                s3.delete_object(Bucket=S3_BUCKET, Key=filename)
            db.session.delete(movie)
            db.session.commit()
            return jsonify({'success': True}), 200
        else:
            abort(422)
    except:
        abort(422)


@admin.post('/admin/add_Web_series')
@admin_required
def add_Web_series():
    try:
        data = request.form
        name = data['name']
        date = datetime.datetime.now()
        short_description = data['short_description']
        description = data['description']
        Language = data['Language']
        image_url = request.files['image']
        Director = data['Director']
        genre = data['Genre']
        orignal = data['orignal']
        web_series = Web_series(
            name=name,
            date=date,
            image_url=upload_file_to_s3(image_url),
            short_description=short_description,
            description=description,
            Language=Language,
            Director=Director,
            genre=genre,
            orignal=orignal
        )

        db.session.add(web_series)
        db.session.commit()
        return jsonify({'success': True, 'wsid': web_series.wsid}), 200

    except Exception as e:
        print(e, "here")
        return jsonify({'success': True})


@admin.route('/admin/edit_Web_series', methods=['POST'])
@admin.route('/admin/edit_Web_series/', methods=['POST'])
@admin_required
def edit_Web_series():
    data = request.form
    name = data['name']
    short_description = data['short_description']
    description = data['description']
    Language = data['Language']
    Director = data['Director']
    genre = data['Genre']
    wsid = int(data['wsid'])
    orignal = data['orignal']
    web_series = Web_series.query.filter_by(wsid=wsid).first()
    if web_series:
        web_series.name = name
        web_series.short_description = short_description
        web_series.description = description
        web_series.Language = Language
        web_series.Director = Director
        web_series.genre = genre
        web_series.orignal = orignal
        if 'image' in request.files:
            image_url = request.files['image'] or None
            if image_url:
                web_series.image_url = upload_file_to_s3(image_url)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        abort(422)


@admin.route('/admin/delete_Web_series', methods=['POST'])
@admin.route('/admin/delete_Web_series/', methods=['POST'])
@admin_required
def delete_Web_series():
    try:
        data = request.get_json()
        wsid = data['wsid']
        ws = Web_series.query.filter_by(wsid=wsid).first()
        if ws:
            for season in ws.sid:
                for movie in season.mid:
                    if movie.q1080p:
                        filename = movie.q1080p
                        filename = filename.partition("/Movie/")[2]
                        s3.delete_object(Bucket=S3_BUCKET, Key=movie.q1080p)
                    db.session.delete(movie)
                db.session.delete(season)
            db.session.delete(ws)
            db.session.commit()
            return jsonify({'success': True}), 200
        else:
            abort(422)
    except:
        abort(422)


@admin.route('/admin/add_Season', methods=['POST'])
@admin.route('/admin/add_Season/', methods=['POST'])
@admin_required
def add_Season():
    data = request.get_json()
    name = data['name']
    wsid = data['wsid']
    date = datetime.datetime.now()
    web_series = Web_series.query.filter_by(wsid=wsid).first()
    if web_series:
        season = Season(
            name=name,
            date=date,
            wsid=wsid
        )
        db.session.add(season)
        db.session.commit()
        if season not in web_series.sid:
            web_series.sid.append(season)
            db.session.commit()
        return jsonify({'success': True, 'sid': season.sid}), 200
    else:
        abort(422)


# pyThOn($)78
@admin.post('/admin/edit_Season')
@admin_required
def edit_Season():
    data = request.get_json()
    name = data['name']
    sid = data['sid']
    season = Season.query.filter_by(sid=sid).first()
    if season:
        season.name = name
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        abort(422)


@admin.route('/admin/delete_Season', methods=['POST'])
@admin.route('/admin/delete_Season/', methods=['POST'])
@admin_required
def delete_Season():
    try:
        data = request.get_json()
        sid = data['sid']
        season = Season.query.filter_by(sid=sid).first()
        if season:
            for movie in season.mid:
                if movie.q1080p:
                    filename = movie.q1080p
                    filename = filename.partition("/Movie/")[2]
                    s3.delete_object(Bucket=S3_BUCKET, Key=movie.q1080p)
                db.session.delete(movie)
            db.session.delete(season)
            db.session.commit()
            return jsonify({'success': True}), 200
        else:
            abort(422)
    except:
        abort(422)


@admin.route('/admin/add_Episode', methods=['POST'])
@admin.route('/admin/add_Episode/', methods=['POST'])
@admin_required
def add_Episode():
    data = request.form
    name = data['name']
    Type = 'Episode'
    sid = data['sid']
    season = Season.query.filter_by(sid=sid).first()
    if season:
        movie = Movie(
            name=name,
            Type=Type,
            sid=sid
        )
        db.session.add(movie)
        if 'image' in request.files:
            image_url = request.files['image']
            movie.image_url = upload_file_to_s3(image_url)
        if 'q1080p' in request.form:
            q1080p = request.form['q1080p']
            if q1080p:
                movie.q1080p = q1080p
        db.session.commit()
        return jsonify({'success': True, 'mid': movie.mid}), 200
    else:
        abort(422)


@admin.post('/admin/edit_Episode')
@admin_required
def edit_Episode():
    data = request.form
    mid = data.get('mid')
    name = data['name']
    sid = data['sid']
    season = Season.query.filter_by(sid=sid).first()
    movie = Movie.query.filter_by(mid=mid).first()
    if season:
        movie.name = name
        if 'image' in request.files:
            image_url = request.files['image']
            if image_url:
                movie.image_url = upload_file_to_s3(image_url)
        if 'q1080p' in request.form:
            q1080p = request.form['q1080p']
            if q1080p:
                s3.delete_object(Bucket=S3_BUCKET, Key=movie.q1080p)
                movie.q1080p = q1080p
        db.session.commit()
        return jsonify({'success': True, 'mid': movie.mid}), 200
    else:
        abort(422)


@admin.post('/admin/delete_Episode')
@admin_required
def delete_Episode():
    try:
        data = request.get_json()
        mid = data['mid']
        movie = Movie.query.filter_by(mid=mid).first()
        if movie:
            if movie.q1080p:
                filename = movie.q1080p
                filename = filename.partition("/Movie/")[2]
                s3.delete_object(Bucket=S3_BUCKET, Key=movie.q1080p)
            db.session.delete(movie)
            db.session.commit()
            return jsonify({'success': True}), 200
        else:
            abort(422)
    except:
        abort(422)


@admin.route('/admin/allorders', methods=['POST'])
@admin.route('/admin/allorders/', methods=['POST'])
@admin_required
def all_orders():
    try:
        orders = Order.query.order_by(Order.date.desc()).all()
        if len(orders) > 0:
            all_order = []
            for order in orders:
                user = User_table.query \
                    .with_entities(User_table.full_name) \
                    .filter_by(uid=order.uid).first()
                temp_order = get_model_dict(order)
                temp_order['Buyers_name'] = user.full_name
                temp_order['Total_price'] = order.total_price
                all_order.append(temp_order)
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': True, 'orders': 'Empty'}), 200
    except:
        abort(422)


@admin.route('/admin/allusers', methods=['POST'])
@admin.route('/admin/allusers/', methods=['POST'])
@admin_required
def all_users():
    try:
        users = User_table.query.order_by(User_table.uid.desc()).all()
        if len(users) > 0:
            all_users = []
            for user in users:
                temp_user = get_model_dict(user)
                del temp_user['password']
                if len(user.membership_order) > 0:
                    membership = user.membership_order[0]
                    temp = get_model_dict(membership)
                    days_left = (temp['valid_till'] -
                                 datetime.datetime.now().date()).days
                    if days_left > 0:
                        temp['days_left'] = days_left
                        del temp['payment_id']
                    else:
                        user.membership_order = []
                        user.membership = 'FREE'
                        db.session.commit()
                        temp = {
                            "days_left": 0,
                            "membership": "FREE",
                            "total_price": 0
                        }
                else:
                    temp = {
                        "days_left": 0,
                        "membership": "FREE",
                        "total_price": 0
                    }
                temp_user['membership'] = temp
                all_users.append(temp_user)
            return jsonify({'success': True, "users": all_users}), 200
        else:
            return jsonify({'success': True, 'orders': 'Empty'}), 200
    except:
        abort(422)


@admin.route('/admin/addimage', methods=['POST'])
@admin.route('/admin/addimage/', methods=['POST'])
@admin_required
def addimage():
    file = request.files['file']
    # if not file:
    #     return jsonify({'success': True, 'error': "No File Chosen!"})
    # filename = secure_filename(file.filename)
    # if "." not in filename:
    #     return jsonify({'success': True, 'error': "File Extension is not valid"})
    # filename = filename_finder(filename)
    # file.save(os.path.join(UPLOAD_IMG, filename))
    # return jsonify({'success': True, 'url': url_for('static', filename=filename, _external=True)}), 200
    output = upload_file_to_s3(file)
    return jsonify({"success": True, "url": output})


def filename_finder(name):
    if os.path.exists("../static/" + str(name)):
        name = "1"+name
        return filename_finder(name)
    else:
        return name


@admin.route('/static/<string:filename>')
def send_file_mk(filename):
    return send_file("../static/"+filename)
