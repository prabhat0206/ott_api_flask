from flask import Blueprint, jsonify
from . import get_model_dict
from .models import *

views = Blueprint('views', __name__)

# category does not exist in models

@views.get('/')
def check():
    return jsonify({"success": True})


@views.route('/api/getbannerbyname/bannername/<string:banner_name>/', methods=['POST'])
@views.route('/api/getbannerbyname/bannername/<string:banner_name>', methods=['POST'])
def banner_by_name(banner_name):
    banner_name = str(banner_name)
    banner = Banners.query.filter_by(name=banner_name).first()
    if banner:
        banner = get_model_dict(banner)
        return jsonify({'success': True, 'banner': banner})
    else:
        return jsonify({'success': False})


# @views.route('/api/getCategories/', methods=['POST'])
# @views.route('/api/getCategories', methods=['POST'])
# def get_Categories():
#     all_categories = Category.query.with_entities(Category.name, Category.cid, Category.image_url) 
#     all_categories = db.session.execute(all_categories).fetchall()
#     categories = []
#     if len(all_categories) > 0:
#         for category in all_categories:
#             categories.append(
#                 {
#                     'cid': category[1],
#                     'name': category[0],
#                     'url': category[2]
#                 }
#             )
#         return jsonify({'success': True, 'Categories': categories})
#     else:
#         return jsonify({'success': False})
