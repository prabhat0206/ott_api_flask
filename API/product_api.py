from flask import Blueprint, jsonify, request, send_file
from .models import *
from . import db, get_model_dict, permission_required, UPLOAD_MOV, BASE_IMAGE_URL
from . import auth
# import random

product_api = Blueprint('product_api', __name__)


@product_api.route('/api/getLatest/<int:pagesize>/<int:pageno>/', methods=['POST'])
@product_api.route('/api/getLatest/<int:pagesize>/<int:pageno>', methods=['POST'])
def get_Latest(pagesize, pageno):
    movies = Movie.query.order_by(Movie.date.desc()).filter(Movie.Type != 'Episode').paginate( pageno,pagesize, False).items
    # movies = db.session.execute(movies).all()
    web_series = Web_series.query.order_by(Web_series.wsid.desc()).paginate( pageno,pagesize, True).items
    # web_series = db.session.execute(web_series).all()
    movies_data = []
    web_series_data = []
    trending = []
    if len(movies) > 0 or len(web_series) > 0:
        for movie in movies:
            movies_data.append(
                {
                    "mid": movie.mid,
                    "name": movie.name,
                    "image_url": BASE_IMAGE_URL + movie.image_url,
                }
            )
            if movie.trending:
                trending.append({"mid": movie.mid, "name": movie.name, "image_url": movie.image_url, "type": "movie"})
        for series in web_series:
            web_series_data.append(
                {
                    "wsid": series.wsid,
                    "name": series.name,
                    "image_url": BASE_IMAGE_URL + series.image_url,
                }
            ) 
            if series.trending:
                trending.append({"wsid": series.wsid, "name": series.name, "image_url": series.image_url,  "type": "web_series"})
        return jsonify({"success": True, 'Movies':movies_data, "Web_Series": web_series_data, "trending": trending,})
    else:
        return jsonify({"success": False})


@product_api.route('/api/getOrignals/<int:pagesize>/<int:pageno>/', methods=['POST'])
@product_api.route('/api/getOrignals/<int:pagesize>/<int:pageno>', methods=['POST'])
def get_Orignals(pagesize, pageno):
    movies = Movie.query.filter(Movie.Type != 'Episode', Movie.orignal == 1).order_by(Movie.date.desc()).paginate( pageno, pagesize, False ).items
    # movies = db.session.execute(movies).all()
    web_series = Web_series.query.filter(Web_series.orignal == 1).order_by(Web_series.date.desc()).paginate( pageno, pagesize, False).items
    # web_series = db.session.execute(web_series).all()
    result_movies = []
    result_web_series = []
    if len(movies) > 0 or len(web_series) > 0:
        for movie in movies:
            result_movies.append(
                {
                    "mid": movie.mid,
                    "name": movie.name,
                    "image_url": BASE_IMAGE_URL + movie.image_url
                }
            )
        for series in web_series:
            result_web_series.append(
                {
                    "wsid": series.wsid,
                    "name": series.name,
                    "image_url": BASE_IMAGE_URL + series.image_url
                }
            )
        return jsonify({"success": True, 'Orignal_Movies': result_movies, 'Orignal_Web_series': result_web_series})
    else:
        return jsonify({"success": False})


@product_api.post('/api/getMovies/<int:pagesize>/<int:pageno>')
def getMovies(pagesize=12, pageno=1):
    moviesPages = Movie.query.order_by(Movie.mid.desc()).paginate(pageno, pagesize, True).items
    movies = []
    if len(moviesPages) > 0:
        for movie in moviesPages:
            movies.append(
                {
                    "mid": movie.mid,
                    "name": movie.name,
                    "image_url":BASE_IMAGE_URL + movie.image_url,
                }
            )
        return jsonify({"success": True, 'movies': movies})
    return jsonify({"success": False})


@product_api.post('/api/getWebSeries/<int:pagesize>/<int:pageno>')
def getWebSeries(pagesize=12, pageno=1):
    web_series_page = Web_series.query.order_by(Web_series.wsid.desc()).paginate(pageno, pagesize, False).items
    web_series = []
    if  len(web_series_page) > 0:
        
        for series in web_series_page:
            web_series.append(
                {
                    "wsid": series.wsid,
                    "name": series.name,
                    "image_url": BASE_IMAGE_URL + series.image_url,
                }
            )
        return jsonify({"success": True, 'web_series': web_series})
    return jsonify({"success": False})


@product_api.route('/api/getWeb_series/', methods=['POST'])
@product_api.route('/api/getWeb_series', methods=['POST'])
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
                seasonEpisode['episodes'].append({
                    'mid': ep.mid,
                    'name': "Season " + str(name_season),
                    'image_url': BASE_IMAGE_URL + ep.image_url,
                    "type": ep.Type,
                })
                name_season+=1
            all_details['season'].append(seasonEpisode)
        return jsonify({"success": True, 'WebSeries': all_details})
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
                    "image_url":BASE_IMAGE_URL + movie[2]
                }
            )
        for series in web_series:
            result_web_series.append(
                {
                    "wsid": series[0],
                    "name": series[1],
                    "image_url":BASE_IMAGE_URL + series[2]
                }
            )
        return jsonify({"success": True, 'Movies': result_movies, 'Web_series':result_web_series})
    else:
        return jsonify({"success": False})


@product_api.route('/Movie/<string:filename>')
@permission_required()
def send_file_mk(filename):
    return send_file(UPLOAD_MOV + filename)
