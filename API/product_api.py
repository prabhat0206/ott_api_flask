from flask import Blueprint, jsonify, request, send_file
from .models import *
from . import db, get_model_dict, permission_required, UPLOAD_MOV

product_api = Blueprint('product_api', __name__)


@product_api.route('/api/getLatest/limit/<limit>', methods=['POST'])
@product_api.route('/api/getLatest/limit/<limit>/', methods=['POST'])
def get_Latest(limit):
    movies = Movie.query.with_entities(
        Movie.mid,
        Movie.name,
        Movie.image_url
    ).filter(Movie.Type != 'Episode').order_by(Movie.date.desc()).limit(int(limit))
    movies = db.session.execute(movies).all()
    web_series = Web_series.query.with_entities(
        Web_series.wsid,
        Web_series.name,
        Web_series.image_url
    ).order_by(Web_series.date.desc()).limit(int(limit))
    web_series = db.session.execute(web_series).all()
    result_data = []
    if len(movies) > 0 or len(web_series) > 0:
        for movie in movies:
            result_data.append(
                {
                    "mid": movie[0],
                    "name": movie[1],
                    "image_url": movie[2]
                }
            ) # hgju
        for series in web_series:
            result_data.append(
                {
                    "wsid": series[0],
                    "name": series[1],
                    "image_url": series[2]
                }
            )  
        return jsonify({"success": True, 'Movies':result_data})
    else:
        return jsonify({"success": False})


@product_api.route('/api/getOrignals/limit/<limit>', methods=['POST'])
@product_api.route('/api/getOrignals/limit/<limit>/', methods=['POST'])
def get_Orignals(limit):
    movies = Movie.query.with_entities(
        Movie.mid,
        Movie.name,
        Movie.image_url
    ).filter(Movie.Type != 'Episode', Movie.orignal == 1).order_by(Movie.date.desc()).limit(int(limit))
    movies = db.session.execute(movies).all()
    web_series = Web_series.query.with_entities(
        Web_series.wsid,
        Web_series.name,
        Web_series.image_url
    ).filter(Web_series.orignal == 1).order_by(Web_series.date.desc()).limit(int(limit))
    web_series = db.session.execute(web_series).all()
    result_movies = []
    result_web_series = []
    if len(movies) > 0 or len(web_series) > 0:
        for movie in movies:
            result_movies.append(
                {
                    "mid": movie[0],
                    "name": movie[1],
                    "image_url": movie[2]
                }
            )
        for series in web_series:
            result_web_series.append(
                {
                    "wsid": series[0],
                    "name": series[1],
                    "image_url": series[2]
                }
            )
        return jsonify({"success": True, 'Orignal_Movies': result_movies, 'Orignal_Web_series': result_web_series})
    else:
        return jsonify({"success": False})


@product_api.route('/api/getWeb_series/', methods=['POST'])
@product_api.route('/api/getWeb_series', methods=['POST'])
def get_Web_series():
    data = request.get_json()
    wsid = data['wsid']
    ws = Web_series.query.filter_by(wsid=wsid).first()
    if ws:
        all_details = get_model_dict(ws)
        for season in ws.sid:
            all_details[season.name] = {}
            for ep in season.mid:
                all_details[season.name][ep.name] = {
                    'mid': ep.mid,
                    'name': ep.name,
                    'image_url': ep.image_url
                }
        return jsonify({"success": True, 'Movie': all_details})
    else:
        return jsonify({'success': False})


@product_api.route('/api/getMovie/', methods=['POST'])
@product_api.route('/api/getMovie', methods=['POST'])
def getMovie():
    data = request.get_json()
    mid = data['mid']
    movie = Movie.query.filter_by(mid=mid).first()
    if movie:
        all_details = get_model_dict(movie)
        del all_details['uid'], all_details['q480p'], all_details['q720p'], all_details['q1080p']
        return jsonify({"success": True, 'Movie': all_details})
    else:
        return jsonify({'success': False})


@product_api.route('/api/searchproduct/<string:word>/', methods=['POST'])
@product_api.route('/api/searchproduct/<string:word>', methods=['POST'])
def search_product(word):
    word = str(word)
    movies = Movie.query.with_entities(
        Movie.mid,
        Movie.name,
        Movie.image_url
    ).filter(Movie.name.like("%" + word + "%") |
             Movie.description.like("%" + word + "%") |
             Movie.Language.like("%" + word + "%") |
             Movie.Director.like("%" + word + "%") |
             Movie.genre.like("%" + word + "%") |
             Movie.Type.like("%" + word + "%"), Movie.Type != 'Episode'
             ).order_by(Movie.date.desc()).all()

    web_series = Web_series.query.with_entities(
        Web_series.wsid,
        Web_series.name,
        Web_series.image_url
    ).filter(Web_series.name.like("%" + word + "%") |
             Web_series.description.like("%" + word + "%") |
             Web_series.Language.like("%" + word + "%") |
             Web_series.genre.like("%" + word + "%") |
             Web_series.Director.like("%" + word + "%")
             ).order_by(Web_series.date.desc()).all()

    result_movies = []
    result_web_series = []
    if len(movies) > 0 or len(web_series) > 0:
        for movie in movies:
            result_movies.append(
                {
                    "mid": movie[0],
                    "name": movie[1],
                    "image_url": movie[2]
                }
            )
        for series in web_series:
            result_web_series.append(
                {
                    "wsid": series[0],
                    "name": series[1],
                    "image_url": series[2]
                }
            )
        return jsonify({"success": True, 'Movies': result_movies, 'Web_series':result_web_series})
    else:
        return jsonify({"success": False})


@product_api.route('/Movie/<string:filename>')
@permission_required()
def send_file_mk(filename):
    return send_file(UPLOAD_MOV + filename)
