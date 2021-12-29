from boto3 import client
from flask import Blueprint, jsonify, request, abort, url_for, send_file
from werkzeug.http import parse_authorization_header
from werkzeug.utils import secure_filename
from datetime import datetime
from .models import *
from . import S3_BUCKET, generate_signed_url, get_model_dict, UPLOAD_MOV, BASE_IMAGE_URL, upload_file_to_s3, s3
import os

static_folder = 'static'
admin = Blueprint('admin', __name__)


@admin.post('/admin/getAllData')
def allData():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
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
                    return jsonify({"success": True, 'Movies':movies_data, "Web_Series": web_series_data})
                else:
                    return jsonify({"success": False})
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/getMovie', methods=['POST'])
@admin.route('/admin/getMovie/', methods=['POST'])
def get_Movie():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":

                data = request.get_json()
                mid = int(data['mid'])
                movie = Movie.query.filter_by(mid=mid).first()
                if movie:
                    result = get_model_dict(movie)
                    return jsonify({'success': True, "Movie":result})
                return jsonify({'success': False})
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/addMovie', methods=['POST'])
@admin.route('/admin/addMovie/', methods=['POST'])
def add_Movie():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                data = request.form
                name = data['name']
                date = datetime.now()
                description = data['description']
                Language = data['Language']
                Director = data['Director']
                short_description = data['short_description']
                Type='Movie'
                image = request.files['image']
                genre = data['Genre']
                orignal = data['orignal']
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
                if 'q1080p' in request.files:
                    q1080p = request.files['q1080p']
                    if q1080p:
                        filename = secure_filename(q1080p.filename)
                        if "." not in filename:
                            return jsonify({'success': True, 'error': "File Extension is not valid"})
                        filename = str(movie.mid) + "1080p." + filename
                        movie.q1080p = upload_file_to_s3(q1080p, True)

                db.session.commit()
                return jsonify({'success': True, 'mid': movie.mid}), 200
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/editMovie', methods=['POST'])
@admin.route('/admin/editMovie/', methods=['POST'])
def edit_Movie():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":

                data = request.form
                mid = int(data['mid'])
                name = data['name']
                description = data['description']
                Language = data['Language']
                Director = data['Director']
                short_description = data['short_description']
                genre = data['Genre']
                orignal = data['orignal']
                movie = Movie.query.filter_by(mid=mid).first()
                if movie:
                    movie.name = name
                    movie.description = description
                    movie.Language = Language
                    movie.short_description = short_description
                    movie.Director = Director
                    movie.genre = genre
                    movie.orignal = orignal
                    if 'q1080p' in request.files:
                        q1080p = request.files['q1080p']
                        if q1080p:
                            filename = secure_filename(q1080p.filename)
                            if "." not in filename:
                                return jsonify({'success': True, 'error': "File Extension is not valid"})
                            filename = str(movie.mid) + "1080p." + filename
                            s3.delete_object(Bucket=S3_BUCKET, Key=movie.q1080p)
                            movie.q1080p = upload_file_to_s3(q1080p, True)

                    db.session.commit()
                    return jsonify({'success': True}), 200
                else:
                    abort(422)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/deleteMovie', methods=['POST'])
@admin.route('/admin/deleteMovie/', methods=['POST'])
def delete_Movie():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
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
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/add_Web_series', methods=['POST'])
@admin.route('/admin/add_Web_series/', methods=['POST'])
def add_Web_series():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                data = request.form()
                name = data['name']
                date = datetime.now()
                short_description = data['short_description']
                description = data['description']
                Language = data['Language']
                image_url = data['image']
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
                return jsonify({'success': True, 'wsid':web_series.wsid}), 200
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/edit_Web_series', methods=['POST'])
@admin.route('/admin/edit_Web_series/', methods=['POST'])
def edit_Web_series():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                data = request.form
                name = data['name']
                short_description = data['short_description']
                description = data['description']
                Language = data['Language']
                Director = data['Director']
                genre = data['Genre']
                wsid = data['wsid']
                orignal = data['orignal']
                web_series = Web_series.query.filter_by(wsid).first()
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
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/delete_Web_series', methods=['POST'])
@admin.route('/admin/delete_Web_series/', methods=['POST'])
def delete_Web_series():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
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
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/add_Season', methods=['POST'])
@admin.route('/admin/add_Season/', methods=['POST'])
def add_Season():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                data = request.get_json()
                name = data['name']
                wsid = data['wsid']
                date = datetime.now()
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
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/edit_Season', methods=['POST'])
@admin.route('/admin/edit_Season/', methods=['POST'])
def edit_Season():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                data = request.get_json()
                name = data['name']
                sid = data['sid']
                season = Web_series.query.filter_by(sid=sid).first()
                if season:
                    season.name = name
                    db.session.commit()
                    return jsonify({'success': True}), 200
                else:
                    abort(422)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/delete_Season', methods=['POST'])
@admin.route('/admin/delete_Season/', methods=['POST'])
def delete_Season():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
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
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/add_Episode', methods=['POST'])
@admin.route('/admin/add_Episode/', methods=['POST'])
def add_Episode():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                data = request.form
                name = data['name']
                Type='Episode'
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
                    if 'q1080p' in request.files:
                        q1080p = request.files['q1080p']
                        if q1080p:
                            filename = secure_filename(q1080p.filename)
                            if "." not in filename:
                                return jsonify({'success': True, 'error': "File Extension is not valid"})
                            filename = str(movie.mid) + "1080p." + filename
                            movie.q1080p = upload_file_to_s3(q1080p, True)
                    db.session.commit()
                    return jsonify({'success': True, 'mid': movie.mid}), 200
                else:
                    abort(422)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.post('/admin/edit_Episode/')
def edit_Episode():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                data = request.form
                mid = data.get('mid')
                name = data['name']
                Type='Episode'
                sid = data['sid']
                season = Season.query.filter_by(sid=sid).first()
                movie = Movie.query.filter_by(mid=mid).first()
                if season:
                    movie.name=name,
                    movie.Type=Type,
                    movie.sid=sid
                    if 'image' in request.files:
                        image_url = request.files['image'] or None
                        if image_url:
                            movie.image_url=upload_file_to_s3(image_url),
                    if 'q1080p' in request.files:
                        q1080p = request.files['q1080p']
                        if q1080p:
                            filename = secure_filename(q1080p.filename)
                            if "." not in filename:
                                return jsonify({'success': True, 'error': "File Extension is not valid"})
                            filename = str(movie.mid) + "1080p." + filename
                            s3.delete_object(Bucket=S3_BUCKET, Key=movie.q1080p)
                            movie.q1080p = upload_file_to_s3(q1080p, True)
                    db.session.commit()
                    return jsonify({'success': True, 'mid': movie.mid}), 200
                else:
                    abort(422)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)

@admin.post('/admin/delete_Episode')
def delete_Episode():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
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
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/allorders', methods=['POST'])
@admin.route('/admin/allorders/', methods=['POST'])
def all_orders():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                try:
                    orders = Order.query.order_by(Order.date.desc()).all()
                    if len(orders) > 0:
                        all_order = []
                        for order in orders:
                            user = User_table.query \
                                .with_entities(User_table.full_name) \
                                .filter_by(customer_id=order.uid).first()
                            temp_order = get_model_dict(order)
                            temp_order['Buyers_name'] = user.full_name
                            temp_order['Total_price'] = order.total_price
                            all_order.append(temp_order)
                        return jsonify({'success': True}), 200
                    else:
                        return jsonify({'success': True, 'orders': 'Empty'}), 200
                except:
                    abort(422)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


@admin.route('/admin/allusers', methods=['POST'])
@admin.route('/admin/allusers/', methods=['POST'])
def all_users():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
                try:
                    users = User_table.query.order_by(User_table.uid.desc()).all()
                    if len(users) > 0:
                        all_users = []
                        for user in users:
                            temp_user = get_model_dict(user)
                            all_users.append(temp_user)
                        return jsonify({'success': True, "users": all_users}), 200
                    else:
                        return jsonify({'success': True, 'orders': 'Empty'}), 200
                except:
                    abort(422)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)

@admin.route('/admin/addimage', methods=['POST'])
@admin.route('/admin/addimage/', methods=['POST'])
def addimage():
    if request.headers.get('Authorization'):
        credentails = parse_authorization_header(
            request.headers.get('Authorization')
        )
        if not credentails:
            abort(401)
        if credentails.password and credentails.username is not None:
            if credentails.username == "thrillingwaves@gmail.com" and credentails.password == "9828060173@Python7":
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
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(401)


def filename_finder(name):
    if os.path.exists("../static/" + str(name)):
        name = "1"+name
        return filename_finder(name)
    else:
        return name


@admin.route('/static/<string:filename>')
def send_file_mk(filename):
    return send_file("../static/"+filename)
