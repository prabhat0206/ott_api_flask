from flask import Blueprint, request, jsonify, send_file, url_for
from .models import *
from . import db, get_model_dict, auth, permission_required
from datetime import datetime, timedelta
from .payment_api import client


order_api = Blueprint('order_api', __name__)


@order_api.route('/api/watchlist/', methods=['POST'])
@order_api.route('/api/watchlist', methods=['POST'])
@auth.login_required()
def get_watchlist():
    uid = auth.current_user()
    user = User_table.query.filter_by(uid=uid).first()
    if user:
        watchlists = user.watchlist
        all_watchlist = []
        if len(watchlists) > 0:
            for watchlist in watchlists:
                mid = watchlist.mid
                name = watchlist.name
                image_url = watchlist.image_url
                all_watchlist.append(
                    {
                        'name': name,
                        'mid': mid,
                        'image_url': image_url
                    }
                )
            return jsonify({'success': True, 'Watchlist': all_watchlist})
        else:
            return jsonify({'success': False})
    else:
        return jsonify({'success': False})


@order_api.route('/api/addtowatchlist/', methods=['POST'])
@order_api.route('/api/addtowatchlist', methods=['POST'])
@auth.login_required()
def add_watchlist():
    data = request.get_json()
    uid = auth.current_user()
    mid = data['mid']
    user = User_table.query.filter_by(uid=uid).first()
    movie = Movie.query.filter_by(mid=mid).first()
    if user and movie:
        user.watchlist.append(movie)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


@order_api.route('/api/delfromwatchlist/', methods=['POST'])
@order_api.route('/api/delfromwatchlist', methods=['POST'])
@auth.login_required()
def del_from_watchlist():
    data = request.get_json()
    uid = auth.current_user()
    mid = data['mid']
    user = User_table.query.filter_by(uid=uid).first()
    movie = Movie.query.filter_by(mid=mid).first()

    if user and movie:
        if movie in user.watchlist:
            user.watchlist.remove(movie)
            db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


@order_api.route('/api/get_membership/', methods=['POST'])
@order_api.route('/api/get_membership', methods=['POST'])
@auth.login_required()
def get_membership():
    uid = auth.current_user()
    user = User_table.query.filter_by(uid=uid).first()
    if user:
        if len(user.membership_order) > 0:
            membership = user.membership_order[0]
            temp = get_model_dict(membership)
            days_left = (temp['valid_till'] - datetime.now().date()).days
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
        return jsonify({'success': True, 'Membership': temp})
    else:
        return jsonify({'success': False})



@order_api.route('/api/getorderbycus/', methods=['POST'])
@order_api.route('/api/getorderbycus', methods=['POST'])
@auth.login_required()
def get_order_by_cus():
    uid = auth.current_user()
    user = User_table.query.filter_by(uid=uid).first()
    if user:
        orders = []
        for order in user.orders:
            temp_order = get_model_dict(order)
            del temp_order['payment_id']
            orders.append(temp_order)
        return jsonify({'success': True, 'Orders': orders})
    else:
        return jsonify({'success': False})


@order_api.route('/api/add_membership/', methods=['POST'])
@order_api.route('/api/add_membership', methods=['POST'])
@auth.login_required()
def add_membership():
    data = request.get_json()
    uid = auth.current_user()
    date = datetime.now()
    membership = data['membership']
    status = data['status']
    amount = data['amount']
    payment_id = data['payment_id']
    order_id = data['order_id']
    signature = data['signature']
    orderss = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }
    if client.utility.verify_payment_signature(orderss) == False:
        return jsonify({'success': False, "Error": "Invalid payment signature"})
    
    memberships = {
        'GOLD': timedelta(days=365),
        'SILVER': timedelta(days=60),
        'BRONZE': timedelta(days=30)
    }

    prices = {
        'GOLD': 599,
        'SILVER': 249,
        'BRONZE': 199
    }
    
    user = User_table.query.filter_by(uid=uid).first()
    membership = membership.upper()
    if membership not in memberships:
        return jsonify({'success': False})
    if user:
        new_order = Order(
            uid=user.uid,
            date=date,
            total_price=prices[membership],
            membership=membership,
            valid_till=date + memberships[membership],
            payment_status=status,
            amount=amount,
            payment_id=payment_id
        )
        db.session.add(new_order)
        user.membership = membership
        user.membership_order = [new_order]
        db.session.commit()
        return jsonify({'success': True, 'order_id': new_order.oid})
    else:
        return jsonify({'success': False})

