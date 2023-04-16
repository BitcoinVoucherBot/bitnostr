#!/usr/bin/env python3

import redis, json
from src.settings import Settings
from src.utils import Utils
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from functools import wraps
from main import redis_host, r, settings

utils = Utils()
server = Flask(__name__)
auth = HTTPBasicAuth()
settings = Settings()
r = redis.Redis(host=redis_host, port=6379, db=0)

def start_server(host, port, debug=False):
    server.run(host=host, port=port, debug=debug)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success':False, 'message': 'Token is missing!'}), 403
        if token != settings.bot_api_key:
            return jsonify({'success':False, 'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated

@server.route('/order/complete', methods=['POST'])
@token_required
def order_complete():
    data = request.get_json()
    if not data:
        return jsonify({'success':False, 'message': 'Invalid request body'}), 400
    message = json.dumps(data)
    print(f"order_complete: {message}")
    r.publish('order_complete', message)
    return jsonify({'success':True}), 200

@server.route('/order/contact', methods=['POST'])
@token_required
def order_contact():
    data = request.get_json()
    if not data:
        return jsonify({'success':False, 'message': 'Invalid request body'}), 400
    message = json.dumps(data)
    print(f"order_contact: {message}")
    r.publish('order_contact', message)
    return jsonify({'success':True}), 200

@server.route('/admin/profile', methods=['GET'])
@token_required
def get_profile():
    pub_key = request.args.get('pub_key')
    if not pub_key:
        return jsonify({'success':False, 'message': 'Missing parameter: pub_key'}), 400
    if 'npub' in pub_key:
        pub_key = Utils.hex_from_npub(pub_key) 
    if pub_key is None:
        return jsonify({'success':False, 'message': 'Invalid pub_key'}), 400
    profile = r.hget(pub_key, 'profile')
    if not profile:
        return jsonify({'success':False, 'message': 'Profile not found'}), 404
    profile = json.loads(profile.decode('utf-8'))
    for key in profile:
        if isinstance(profile[key], str):
            profile[key] = Utils.remove_emoji(profile[key])
    return jsonify({'success':True, 'profile': profile}), 200

@server.route('/admin/orders', methods=['GET'])
@token_required
def get_orders():
    pub_key = request.args.get('pub_key')
    if not pub_key:
        return jsonify({'success':False, 'message': 'Missing parameter: pub_key'}), 400
    if 'npub' in pub_key:
        pub_key = Utils.hex_from_npub(pub_key)
    if pub_key is None:
        return jsonify({'success':False, 'message': 'Invalid pub_key'}), 400
    orders = r.lrange(f"{pub_key}:orders", 0, -1)
    orders = [order.decode('utf-8') for order in orders]
    return jsonify({'success':True, 'orders': orders}), 200

@server.errorhandler(400)
def bad_request(error):
    return jsonify({'success':False, 'error': {'name': error.name, 'message': error.description}}), 400

@server.errorhandler(404)
def not_found(error):
    return jsonify({'success':False, 'error': {'name': error.name, 'message': error.description}}), 404

@server.errorhandler(500)
def internal_server_error(error):
    return jsonify({'success':False, 'error': {'name': error.name, 'message': error.description}}), 500

@server.before_request
def before_request():
    if request.method == 'POST':
        response_string = json.dumps(request.get_json())
        print(f"Request: {request.method} - {request.url} - {response_string}")
    else:
        print(f"Request: {request.method} - {request.url}")

@server.after_request
def after_request(response):
    response_data = response.get_json()
    response_string = json.dumps(response_data)
    headers_string = json.dumps(dict(response.headers))
    print(f"Response: {request.method} -  {request.url} - {response.status_code} - {headers_string} - {response_string}")
    return response

if __name__ == "__main__":
    start_server()